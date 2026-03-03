# 🛡️ ĐỀ TÀI: TẤN CÔNG DDOS VÀ CÁCH PHÒNG CHỐNG

## 👥 Nhóm tác giả
* [cite_start]Nguyễn Trung Kiên – AT200432 [cite: 573]
* [cite_start]Nguyễn Văn Khánh – AT200430 [cite: 574]
* [cite_start]Vũ Trọng Khang – AT200130 [cite: 575]
* [cite_start]Nguyễn Công Khánh – AT200131 [cite: 576]
* [cite_start]Đinh Trí Đức – AT200114 [cite: 577]

## 📖 Tổng quan dự án (Overview)
[cite_start]Dự án này là hệ thống hóa toàn bộ kiến thức về Tấn công Từ chối Dịch vụ Phân tán (DDoS) và triển khai các kịch bản thực nghiệm để tìm ra giải pháp phòng vệ tối ưu[cite: 665]. [cite_start]Báo cáo đi sâu vào phân tích các kỹ thuật tấn công phổ biến như SYN Flood, ICMP Flood, UDP Flood, và HTTP POST/GET Attack[cite: 669]. [cite_start]Thông qua môi trường mô phỏng, dự án đánh giá hiệu quả của các biện pháp phòng vệ đa tầng bao gồm IPtables Firewall và Snort IDS[cite: 672].

## 🛠️ Công cụ sử dụng (Tools & Technologies)
* [cite_start]**Mô phỏng tấn công:** Hping3, Slowhttptest, Py-botnet[cite: 670].
* [cite_start]**Phân tích lưu lượng:** Wireshark[cite: 671].
* [cite_start]**Phòng thủ & Cảnh báo:** Snort IDS, IPtables (Linux Firewall), WAF[cite: 672, 1074, 1077].

## ⚔️ Các kịch bản thực nghiệm tấn công
Dự án đã triển khai thành công các kịch bản sau:
* [cite_start]**Tấn công tràn băng thông (Flood Attack):** Sử dụng ICMP Flood và SYN Flood bằng công cụ Hping3[cite: 1083].
* [cite_start]**Tấn công tầng ứng dụng (Layer 7):** Sử dụng HTTP GET Flood và HTTP POST Flood bằng công cụ Slowhttptest[cite: 1099, 1104, 1115].
* [cite_start]**Mô phỏng mạng Botnet:** Triển khai mô hình Command and Control (C&C Server) bằng Py-botnet[cite: 1122].

## 🛡️ Giải pháp phòng vệ đã triển khai
* [cite_start]**Cấu hình IPtables:** Thiết lập giới hạn kết nối (Rate Limiting) để chặn các IP có dấu hiệu gửi gói tin ồ ạt[cite: 1076].
* [cite_start]**Cấu hình Snort IDS:** Tạo các Rule (Luật) để phát hiện lưu lượng ICMP Flood bất thường[cite: 1072, 1073].

## ⚠️ Tuyên bố từ chối trách nhiệm (Disclaimer)
[cite_start]Dự án này được thực hiện hoàn toàn cho mục đích giáo dục, nghiên cứu an toàn thông tin tại Học viện Kỹ thuật Mật mã[cite: 567, 572]. Các kịch bản mô phỏng được thực hiện trong môi trường Lab cục bộ. Nhóm tác giả không chịu trách nhiệm cho bất kỳ hành vi lạm dụng nào nhằm vào các hệ thống thực tế ngoài phạm vi nghiên cứu.
