from flask import Blueprint, render_template, request, redirect, url_for
from website.database_management import read_statuses, update_tujuan_db, ROBOT_STATUS_FILE
from .route_calculation import a_star_search, coords
from .route_instructions import generate_instructions
from .mockup_robot import run_robot_simulation 
from .status_book_callingcard import StatusRobot, StatusElektronika, StatusPaket
<<<<<<< Updated upstream
import threading 
=======
from .mqtt_connection import initialize_mqtt_client, send_instructions_via_mqtt
import threading # Wajib import ini
>>>>>>> Stashed changes
import json 
import os

# Initialize MQTT client when module loads
try:
    initialize_mqtt_client()
except Exception as e:
    print(f"[WARNING] Failed to initialize MQTT: {e}")

views = Blueprint('views', __name__)

@views.route('/')
def home():
    context = read_statuses()
    return render_template("dashboard_home.html", **context)

@views.route('/send', methods=['GET', 'POST'])
def send_page():

    current_status = int(StatusRobot.ROBOT_AKTIF)
    tujuan_sekarang = ""
    rute_sekarang = ""
    instruksi_sekarang = []

    if os.path.exists(ROBOT_STATUS_FILE):
        with open(ROBOT_STATUS_FILE, 'r') as f:
            try:
                db_data = json.load(f)
                current_status = db_data.get('status_robot', 103)
                tujuan_sekarang = db_data.get('tujuan_sekarang', '-')
                rute_sekarang = db_data.get('rute_terakhir', '-')
                instruksi_sekarang = db_data.get('instruksi_navigasi', [])
            except: pass


    if current_status in [104, 105, 106, 107]:
        return render_template("dashboard_send.html", 
                               mode="MONITOR", 
                               status_code=current_status,
                               tujuan=tujuan_sekarang,
                               rute=rute_sekarang,
                               instruksi=instruksi_sekarang)
    
    hasil_rute = ""
    status_rute = ""
    warna_status = ""
    list_instruksi = []

    if request.method == 'POST':
        tujuan = request.form.get('pilihan').upper()
        nama = request.form.get('nama')
        
        path, msg = a_star_search('START', tujuan)
        
        if path:
            rute_str = " -> ".join(path)
            hasil_rute = rute_str
            status_rute = "RUTE OK! ROBOT DILUNCURKAN"
            warna_status = "text-success"
            
            # === PERBAIKAN PENTING DI SINI ===
            # Kita pisah hasil (Teks, Kode)
            instruksi_text, instruksi_code = generate_instructions(path, coords)
            
<<<<<<< Updated upstream
            # Yang ditampilkan ke Web cuma Teks
            list_instruksi = instruksi_text
            
            # Thread Simulasi dijalankan pakai Teks saja (supaya mockup tidak error)
=======
            # KIRIM INSTRUKSI KE ESP32 VIA MQTT
            try:
                send_instructions_via_mqtt(list_instruksi, tujuan, rute_str)
            except Exception as e:
                print(f"[ERROR] Gagal mengirim instruksi via MQTT: {e}")
            
            # JALANKAN ROBOT DI BACKGROUND (THREADING)
            # args=(tujuan, pengirim, rute_text, instruksi)
>>>>>>> Stashed changes
            robot_thread = threading.Thread(target=run_robot_simulation, 
                                            args=(tujuan, nama, rute_str, list_instruksi))
            robot_thread.start()
            
            return redirect(url_for('views.send_page'))
            
        else:
            hasil_rute = "Lokasi tidak valid!"
            status_rute = "ERROR"
            warna_status = "text-danger"

    return render_template("dashboard_send.html", 
                           mode="INPUT",
                           hasil_rute=hasil_rute, 
                           status_rute=status_rute,
                           warna_status=warna_status,
                           instruksi=list_instruksi)