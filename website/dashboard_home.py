import json
import os
import subprocess
import platform  # <--- Ini tambahan penting buat deteksi OS

def get_current_wifi():
    # Cek sistem operasi laptop yang sedang menjalankan kode ini
    system_os = platform.system()

    try:
        # === SKENARIO 1: WINDOWS (Punya Temanmu) ===
        if system_os == "Windows":
            # Execute the netsh command to get Wi-Fi interface information
            output = subprocess.check_output(["netsh", "wlan", "show", "interfaces"], text=True)
            # Split the output into lines
            lines = output.splitlines()
            # Look for the line containing the SSID
            for line in lines:
                if "SSID" in line and "BSSID" not in line:
                    # Extract the SSID value after the colon
                    ssid = line.split(":", 1)[1].strip()
                    return ssid if ssid else None

        # === SKENARIO 2: MACBOOK (Punya Kamu) ===
        elif system_os == "Darwin":  # "Darwin" adalah kode nama untuk macOS
            # Perintah khusus Mac untuk ambil info Wifi
            # Menggunakan tool bawaan Mac bernama 'airport'
            cmd = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I"
            output = subprocess.check_output(cmd, shell=True, text=True)
            
            lines = output.splitlines()
            for line in lines:
                # Di Mac outputnya biasanya " SSID: NamaWifi"
                if " SSID:" in line:
                    ssid = line.split(":")[1].strip()
                    return ssid
            
            return "Mac Wi-Fi Connected" # Pesan cadangan kalau nama wifi gak terdeteksi

    except (subprocess.CalledProcessError, IndexError, FileNotFoundError, Exception):
        # Kalau ada error apapun, return None biar website gak crash
        return None

    return None