# 🛡️ ĐỀ TÀI: TẤN CÔNG DDOS VÀ CÁCH PHÒNG CHỐNG


## 📖 Tổng quan dự án (Overview)
Dự án này là hệ thống hóa toàn bộ kiến thức về Tấn công Từ chối Dịch vụ Phân tán (DDoS) và triển khai các kịch bản thực nghiệm để tìm ra giải pháp phòng vệ tối ưu. Báo cáo đi sâu vào phân tích các kỹ thuật tấn công phổ biến như SYN Flood, ICMP Flood, UDP Flood, và HTTP POST/GET Attack. Thông qua môi trường mô phỏng, dự án đánh giá hiệu quả của các biện pháp phòng vệ đa tầng bao gồm IPtables Firewall và Snort IDS.

## 🛠️ Công cụ sử dụng (Tools & Technologies)
* **Mô phỏng tấn công:** Hping3, Slowhttptest, Py-botnet.
* **Phân tích lưu lượng:** Wireshark , Task manager.
* **Phòng thủ & Cảnh báo:** Snort IDS, IPtables (Linux Firewall), WAF.

## ⚔️ Các kịch bản thực nghiệm tấn công
Dự án đã triển khai thành công các kịch bản sau:
* **Tấn công tràn băng thông (Flood Attack):** Sử dụng ICMP Flood và SYN Flood bằng công cụ Hping3.
* **Tấn công tầng ứng dụng (Layer 7):** Sử dụng HTTP GET Flood và HTTP POST Flood bằng công cụ Slowhttptest.
* **Mô phỏng mạng Botnet:** Triển khai mô hình Command and Control (C&C Server) bằng Py-botnet.

## 🛡️ Giải pháp phòng vệ đã triển khai
* **Cấu hình IPtables:** Thiết lập giới hạn kết nối (Rate Limiting) để chặn các IP có dấu hiệu gửi gói tin ồ ạt.
* **Cấu hình Snort IDS:** Tạo các Rule (Luật) để phát hiện lưu lượng ICMP Flood bất thường.

---

## 📚 Các bước tiến hành thực nghiệm
1. [Chuẩn bị môi trường](docs/environment-preparation.md)
2. [Tấn công](docs/attack.md)
3. [Phòng thủ](docs/defense.md)

---

## ⚠️ Tuyên bố từ chối trách nhiệm (Disclaimer)
Dự án này được thực hiện hoàn toàn cho mục đích giáo dục, nghiên cứu an toàn thông tin tại Học Viện Kỹ Thuật Mật Mã. Các kịch bản mô phỏng được thực hiện trong môi trường Lab cục bộ. Tác giả không chịu trách nhiệm cho bất kỳ hành vi lạm dụng nào nhằm vào các hệ thống thực tế ngoài phạm vi nghiên cứu.
