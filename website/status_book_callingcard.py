from enum import IntEnum

class StatusRobot(IntEnum):
    ROBOT_TIDAK_AKTIF = 101
    ROBOT_AKTIF = 102
    ROBOT_STANDBY_DISTATION = 103
    ROBOT_MENGANTAR_PAKET = 104
    ROBOT_TELAH_MENGANTAR_PAKET = 105
    ROBOT_MENUJU_STATION = 106
    ROBOT_MENGALAMI_KENDALA = 107

class StatusElektronika(IntEnum):
    ELEKTRONIKA_TIDAKTERHUBUNG = 201
    ELEKTRONIKA_TERHUBUNG = 202
    ELEKTRONIKA_OK = 203
    WIFI_TIDAKTERHUBUNG = 251
    WIFI_TERHUBUNG = 252

class StatusPaket(IntEnum):
    ROBOT_TIDAK_TERSEDIA = 301
    MENUNGGU_PAKET = 302
    PAKET_DIANTAR = 303
    PAKET_TIBA = 304

def get_status_robot(code):
    robot_status = {"text": "UNKNOWN", "color": "text-secondary"}
    
    if code == 101:
        robot_status = {"text": "ROBOT TIDAK AKTIF", "color": "text-danger"} # Merah
    elif code == 102:
        robot_status = {"text": "ROBOT AKTIF", "color": "text-secondary"} # Grey
    elif code == 103:
        robot_status = {"text": "ROBOT STANDBY DI STATION", "color": "text-warning"} # Amber
    elif code == 104:
        robot_status = {"text": "ROBOT MENGANTAR PAKET, MENUJU TUJUAN ", "color": "text-primary"} # Biru
    elif code == 105:
        robot_status = {"text": "ROBOT TIBA DI TUJUAN", "color": "text-success"} # Hijau
    elif code == 106:
        robot_status = {"text": "ROBOT KEMBALI KE STATION", "color": "text-primary"} # Hijau
    elif code == 107:
        robot_status = {"text": "ROBOT MENGALAMI KENDALA", "color": "text-danger"} # Merah
        
    return robot_status

def get_status_elektronika(code):
    elektronika_status = {"text": "UNKNOWN", "color": "text-secondary"}
    
    if code == 201:
        elektronika_status = {"text": "TIDAK TERHUBUNG", "color": "text-danger"} # Merah
    elif code == 202:
        elektronika_status = {"text": "TERHUBUNG", "color": "text-warning"} # Amber
    elif code == 203:
        elektronika_status = {"text": "OK", "color": "text-success"} # Hijau
    elif code == 251:
        elektronika_status = {"text": "TIDAK TERHUBUNG", "color": "text-danger"} # Merah
    elif code == 252:
        elektronika_status = {"text": "TERHUBUNG", "color": "text-success"} # Hijau
    return elektronika_status

def get_status_paket(code):
    paket_status = {"text": "UNKNOWN", "color": "text-secondary"}
    
    if code == 301:
        paket_status = {"text": "ROBOT TIDAK TERSEDIA", "color": "text-danger"} # Merah
    elif code == 302:
        paket_status = {"text": "MENUNGGU PAKET", "color": "text-warning"} # Amber
    elif code == 303:
        paket_status = {"text": "PAKET DIANTAR", "color": "text-primary"} # Biru
    elif code == 304:
        paket_status = {"text": "PAKET TIBA", "color": "text-success"} # Hijau
        
    return paket_status