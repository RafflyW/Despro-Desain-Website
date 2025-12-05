import json
import os
import subprocess

def get_current_wifi():
    try:
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
    except (subprocess.CalledProcessError, IndexError):
        return None