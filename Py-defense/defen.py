import os
import time
import queue
import csv
import threading
import tkinter as tk
from tkinter import ttk
import sys
import socket
from scapy.all import sniff, IP, TCP, UDP, ICMP, Raw

sys.stdout.reconfigure(encoding='utf-8')

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

SERVER_IP = get_local_ip()
GUI_UPDATE_RATE = 200

print(f"[*] IP máy chủ hiện tại được tự động nhận diện: {SERVER_IP}")

gui_queue = queue.Queue()
start_time = time.time()
global_traffic = {
    'start_time': time.time(),
    'total_pkts': 0
}

# ==== 1. GHI LOG ====
log_file = "attack_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Source IP", "Status", "Packets"])

def log_attack(timestamp, ip, status, pkts):
    with open(log_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, ip, status, pkts])

# ==== 2. GIAO DIỆN (GUI) ====
root = tk.Tk()
root.title(f"🔥 Giám sát An ninh IoT - IP: {SERVER_IP}")
root.geometry("700x400")

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
tree.heading("label", text="🎯 Phân loại Tấn công")
tree.heading("pkts", text="📦 Packets")
tree.column("pkts", width=80)
tree.column("label", width=200)
tree.grid(row=1, column=0, sticky="nsew")

tree.tag_configure('attack', background='#ffcccc')
tree.tag_configure('ddos', background='#ff6666', foreground='white')

def update_gui():
    try:
        while not gui_queue.empty():
            ts, ip, lbl, pkts = gui_queue.get()
            if "DDOS" in lbl:
                tags = ('ddos',)
            elif "TẤN CÔNG" in lbl or "FLOOD" in lbl:
                tags = ('attack',)
            else:
                tags = ()
                
            tree.insert("", 0, values=(ts, ip, lbl, pkts), tags=tags)
            status_label.config(text=f"🟢 Đang hoạt động | Cập nhật: {ip}")
    except Exception:
        pass
    root.after(GUI_UPDATE_RATE, update_gui)

# ==== 3. PHÂN TÍCH VÀ PHÂN LOẠI GÓI TIN ====
traffic_stats = {}

def analyze_traffic(ip, duration, stats):
    label_detail = "✅ BÌNH THƯỜNG"

    # 1. ICMP Flood (Ping Flood)
    if stats['icmp_pkts'] > 50:
        print(f"🔴 PHÁT HIỆN ICMP FLOOD (Ping) từ {ip}!")
        label_detail = "🔥 ICMP (Ping) FLOOD"
        
    # 2. HTTP Flood (Tấn công lớp ứng dụng - Ngưỡng thấp hơn vì gói HTTP nặng)
    elif stats['http_pkts'] > 20:
        print(f"🔴 PHÁT HIỆN HTTP FLOOD (Lớp 7) từ {ip}!")
        label_detail = "🔥 HTTP GET/POST FLOOD"
        
    # 3. SYN Flood (Lớp 4)
    elif stats['syn_pkts'] > 50: 
        print(f"🔴 PHÁT HIỆN SYN FLOOD từ {ip}!")
        label_detail = "🔥 SYN FLOOD"
        
    # 4. UDP Flood (Lớp 4)
    elif stats['udp_pkts'] > 80:
        print(f"🔴 PHÁT HIỆN UDP FLOOD từ {ip}!")
        label_detail = "🔥 UDP FLOOD"
        
    # 5. Tấn công ngập lụt chung (TCP hoặc các giao thức khác)
    elif stats['src_pkts'] > 100:
        print(f"🔴 PHÁT HIỆN DOS CHUNG từ {ip}!")
        label_detail = "🔥 TCP/GENERIC DOS"

    ts_str = time.strftime("%Y-%m-%d %H:%M:%S")
    gui_queue.put((ts_str, ip, label_detail, stats['src_pkts']))
    log_attack(ts_str, ip, label_detail, stats['src_pkts'])

def process_packet(packet):
    if IP not in packet:
        return

    src_ip = packet[IP].src
    if src_ip == "127.0.0.1" or src_ip == SERVER_IP: 
        return

    current_time = time.time()

    # --- LỚP 1: DDOS TỔNG LỰC ---
    global global_traffic
    global_traffic['total_pkts'] += 1
    if current_time - global_traffic['start_time'] >= 1.0:
        if global_traffic['total_pkts'] > 500: 
            ts_str = time.strftime("%Y-%m-%d %H:%M:%S")
            gui_queue.put((ts_str, "MULTIPLE_IPS", "🚨 DDOS TỔNG LỰC", global_traffic['total_pkts']))
            log_attack(ts_str, "MULTIPLE_IPS", "🚨 DDOS TỔNG LỰC", global_traffic['total_pkts'])
        global_traffic['start_time'] = current_time
        global_traffic['total_pkts'] = 0
        
    # --- LỚP 2: BÓC TÁCH TỪNG GIAO THỨC ---
    if src_ip not in traffic_stats:
        traffic_stats[src_ip] = {
            'start_time': current_time,
            'src_pkts': 0, 'syn_pkts': 0, 'udp_pkts': 0,
            'icmp_pkts': 0, 'http_pkts': 0
        }

    traffic_stats[src_ip]['src_pkts'] += 1

    # Nhận diện ICMP (Ping)
    if ICMP in packet:
        traffic_stats[src_ip]['icmp_pkts'] += 1
        
    # Nhận diện UDP
    elif UDP in packet:
        traffic_stats[src_ip]['udp_pkts'] += 1
        
    # Nhận diện TCP (Bao gồm SYN và HTTP)
    elif TCP in packet:
        # Check cờ SYN
        if packet[TCP].flags == "S" or packet[TCP].flags == "SA":
            traffic_stats[src_ip]['syn_pkts'] += 1
            
        # Check HTTP (Dựa vào Port 80/443 và Payload chứa GET/POST)
        if packet[TCP].dport in [80, 443] and packet.haslayer(Raw):
            try:
                payload = packet[Raw].load.decode('utf-8', errors='ignore')
                if payload.startswith("GET ") or payload.startswith("POST "):
                    traffic_stats[src_ip]['http_pkts'] += 1
            except:
                pass

    # Phân tích mỗi 2 giây
    if current_time - traffic_stats[src_ip]['start_time'] >= 2.0:
        analyze_traffic(src_ip, current_time - traffic_stats[src_ip]['start_time'], traffic_stats[src_ip])
        del traffic_stats[src_ip] 

def start_sniffer():
    print("🚀 Đang khởi động bộ dò quét mạng (Forensics Mode)...")
    sniff(prn=process_packet, store=False)

threading.Thread(target=start_sniffer, daemon=True).start()
update_gui()
root.mainloop()