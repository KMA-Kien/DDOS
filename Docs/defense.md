# Triển khai phòng thủ DDOS

---

## 1.	Triển khai cấu hình tường lửa IPtables để chặn IP/Lọc gói tin.

IPtables là tường lửa tích hợp sẵn trên Linux, hoạt động dựa trên các quy tắc (Rules) nằm trong các chuỗi (Chains). Đối với việc ngăn chặn DDoS, chúng ta tác động chủ yếu vào chuỗi dữ liệu đi vào server (Input).
Các hành động cơ bản:
-	ACCEPT: Cho phép gói tin đi qua.
-	DROP: Loại bỏ gói tin ngay lập tức, kẻ tấn công sẽ không nhận được phản hồi.
-	REJECT: Từ chối gói tin và gửi lại thông báo lỗi, hành động này không khuyến khích sử dụng vì khi bị tấn công DDoS sẽ làm tốn thêm tài nguyên để gửi tin báo lỗi.

Bước 1: Kiểm tra trạng thái IPtables ban đầu.
Trước khi thêm các rule phòng chống, kiểm tra cấu hình IPtables hiện tại trên máy nạn nhân.

```
iptables -L -n -v
```
Giải thích lệnh:
-L: Liệt kê các rules hiện có trong chain.
-n: Hiện thị IP dạng số.
-v: Hiện thị chi tiết lưu lượng gói tin đã chặn.

![DDOS](images/defense/1.png)

Các câu lệnh DROP:

![DDOS](images/defense/2.png)

1.	Chặn đích danh IP tấn công.

```
sudo iptables -A INPUT -s <IP_Attacker> -j DROP
```

Khi bị tấn công:

![DDOS](images/defense/3.png)

Kiểm tra CMD:

![DDOS](images/defense/4.png)

Kết quả cho thấy đã có 1776K gói tin với dung lượng 50MB từ địa chỉ IP 192.168.214.148 đã bị chặn (DROP). Các rule chặn đã hoạt động hiệu quả, bảo vệ máy nạn nhân khỏi tấn công.

2.	Lọc gói tin theo giao thức SYN.

```
sudo iptables -A INPUT -p tcp --syn -m limit --limit 1/s --limit-burst 3 -j ACCEPT
sudo iptables -A INPUT -p tcp --syn -j DROP
```

Giải thích lệnh:
-	-A INPUT (Append): Thêm hoặc chèn vào cuối quy tắc này vào chuỗi INPUT. Chuỗi INPUT chịu trách nhiệm xử lí tấc cả các gói tin bên ngoài đi vào máy chủ của bạn.
  
-	-p tcp (Protocol): Chỉ định quy tắc này chỉ áp dụng cho giao thức TCP.
  
-	--syn: Đây là cờ (flag) đặc biệt. Nó yêu cầu IPtables chỉ bắt các gói tin TCP có cờ SYN được bật.
  
-	-m limit (Match): Gọi một module mở rộng của IPtables có tên là limit. Module này cung cấp khả năng đếm và giới hạn tốc độ gói tin.
  
-	--limit 1/s: Đặt tốc độ tối đa cho phép là 1 gói tin/giây. Có thể thay đổi thành 1/m (phút), 1/h (giờ) tùy nhu cầu.
  
-	--limit-burst 3: Quy định số lượng gói tin “bùng nổ” (burst) tối đa ban đầu được phép di chuyển qua cùng lúc trước khi IPtables bắt đầu áp dụng tốc độ 1/s ở trên. Ở đây cho phép tối đa 3 gói tin đến cùng lúc.
  
-	-j ACCEPT / DROP (Jump): Hành động sẽ thực thi nếu gói tin khớp với điều kiện trên.

-	ACCEPT: Cho phép gói tin đi qua tường lửa để vào hệ điều hành xử lý.
  
-	DROP: Vứt bỏ gói tin ngay lập tức, kẻ tấn công sẽ không nhận được bất kì phản hồi nào, khiến chúng bị treo, chờ đợi.
  
Khi bị tấn côngtấn công:

![DDOS](images/defense/5.png)

Kiểm tra CMD:

![DDOS](images/defense/6.png)

Kết quả cho thấy đã có 1777K gói tin với dung lượng 50MB từ địa chỉ IP 192.168.214.148 đã bị chặn (DROP). Rule giới hạn SYN đã hoạt động, chỉ 1 gói tin được ACCEPT, các gói SYN vượt quá ngưỡng “burst“ (3 gói) đều bị DROP. Máy nạn nhân đã được bảo vệ khỏi tấn công SYN Flood.

3.	Chặn ICMP Flood.


![DDOS](images/defense/7.png)
![DDOS](images/defense/8.png)
![DDOS](images/defense/9.png)
![DDOS](images/defense/10.png)
![DDOS](images/defense/11.png)
![DDOS](images/defense/12.png)
![DDOS](images/defense/13.png)
![DDOS](images/defense/14.png)
![DDOS](images/defense/15.png)
![DDOS](images/defense/16.png)
![DDOS](images/defense/17.png)
![DDOS](images/defense/18.png)
![DDOS](images/defense/19.png)
