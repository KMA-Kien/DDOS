import os
import time
import queue
import csv
import threading
import tkinter as tk
from tkinter import ttk
import joblib
import pandas as pd
import sys
# Thư viện bắt gói tin mạng
from scapy.all import sniff, IP, TCP, UDP, ICMP

sys.stdout.reconfigure(encoding='utf-8')

gui_queue = queue.Queue()
start_time = time.time()

# 1. Tải mô hình
try:
    model_data = joblib.load("model/iot_attack_model.pkl")
    model = model_data['model']
    print("✅ Đã tải mô hình AI thành công.")
except Exception as e:
    print(f"⚠️ Lỗi tải mô hình: {e}. Sẽ chỉ dùng Rule-based.")
    model = None

# 2. File ghi log
log_file = "attack_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Source IP", "Prediction"])

def log_attack(timestamp, ip, prediction):
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, prediction])

# 3. ==== GUI setup ====
root = tk.Tk()
root.title("🔥 Giám sát An ninh IoT - Packet Sniffer")
root.geometry("600x400")

frame = ttk.Frame(root, padding=10)
frame.grid(row=0, column=0, sticky="nsew")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)
frame.grid_rowconfigure(1, weight=1)
frame.grid_columnconfigure(0, weight=1)

status_label = ttk.Label(frame, text="📡 Đang lắng nghe mạng...", font=("Arial", 14))
status_label.grid(row=0, column=0, pady=10)

tree = ttk.Treeview(frame, columns=("time", "ip", "label", "pkts"), show="headings")
tree.heading("time", text="🕒 Thời gian")
tree.heading("ip", text="🌐 IP Nguồn")
tree.heading("label", text="🎯 Trạng thái")
tree.heading("pkts", text="📦 Số Packets")
tree.column("pkts", width=80)
tree.grid(row=1, column=0, sticky="nsew")
tree.tag_configure('attack', background='#ffcccc')

def update_gui():
    try:
        while not gui_queue.empty():
            ts, ip, lbl, pkts = gui_queue.get()
            tags = ('attack',) if lbl == "🔥 TẤN CÔNG" else ()
            tree.insert("", 0, values=(ts, ip, lbl, pkts), tags=tags)
            status_label.config(text=f"🟢 Đang hoạt động | Cập nhật IP: {ip}")
    except Exception as e:
        pass
    root.after(200, update_gui)

# 4. ==== Logic Bắt và Phân tích Gói tin ====
traffic_stats = {}

def analyze_traffic(ip, duration, stats):
    # Khớp 17 features mà model yêu cầu
    features = [
        0, # ts
        stats['src_port'], stats['dst_port'], duration, 
        stats['src_bytes'], 0, 0, stats['src_pkts'], 
        stats['src_bytes'], 0, 0, 0, 0, 0, 0, 0, 0
    ]

    print(f"\n📊 Phân tích IP: {ip} | Gửi {stats['src_pkts']} pkts | Băng thông: {stats['src_bytes']} bytes")
    
    # DoS Rule-based: Nếu gửi quá 100 gói tin trong 2 giây -> Tấn công (rất nhạy với hping3)
    if stats['src_pkts'] > 100:
        print("🔴 PHÁT HIỆN TẤN CÔNG QUA RULE-BASED (Lưu lượng bất thường)")
        prediction = 1
    else:
        if model:
            feature_names = [
                'ts', 'src_port', 'dst_port', 'duration', 'src_bytes', 
                'dst_bytes', 'missed_bytes', 'src_pkts', 'src_ip_bytes', 
                'dst_pkts', 'dst_ip_bytes', 'dns_qclass', 'dns_qtype', 
                'dns_rcode', 'http_request_body_len', 'http_response_body_len', 'http_status_code'
            ]
            input_df = pd.DataFrame([features], columns=feature_names)
            try:
                prediction = model.predict(input_df)[0]
            except:
                prediction = 0
        else:
            prediction = 0

    label = "🔥 TẤN CÔNG" if prediction == 1 else "✅ BÌNH THƯỜNG"
    ts_str = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # Đẩy lên GUI
    gui_queue.put((ts_str, ip, label, stats['src_pkts']))
    log_attack(ts_str, ip, label)

def process_packet(packet):
    if IP not in packet:
        return

    src_ip = packet[IP].src
    # Bỏ qua lưu lượng nội bộ để tránh nhiễu
    if src_ip == "127.0.0.1": 
        return

    current_time = time.time()
    pkt_len = len(packet)

    if src_ip not in traffic_stats:
        traffic_stats[src_ip] = {
            'start_time': current_time,
            'src_bytes': 0,
            'src_pkts': 0,
            'src_port': 0,
            'dst_port': 0
        }

    traffic_stats[src_ip]['src_bytes'] += pkt_len
    traffic_stats[src_ip]['src_pkts'] += 1

    if TCP in packet:
        traffic_stats[src_ip]['src_port'] = packet[TCP].sport
        traffic_stats[src_ip]['dst_port'] = packet[TCP].dport
    elif UDP in packet:
        traffic_stats[src_ip]['src_port'] = packet[UDP].sport
        traffic_stats[src_ip]['dst_port'] = packet[UDP].dport

    # Đóng gói dữ liệu mỗi 2 giây để phân tích
    duration = current_time - traffic_stats[src_ip]['start_time']
    if duration >= 2.0:
        analyze_traffic(src_ip, duration, traffic_stats[src_ip])
        del traffic_stats[src_ip] # Reset thống kê

def start_sniffer():
    print("🚀 Đang khởi động bộ dò quét mạng (Packet Sniffer)...")
    # Lắng nghe tất cả các card mạng
    sniff(prn=process_packet, store=False)

# 5. ==== Khởi chạy ====
threading.Thread(target=start_sniffer, daemon=True).start()
update_gui()
root.mainloop()