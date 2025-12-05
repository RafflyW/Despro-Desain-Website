from flask import Blueprint, render_template, request, redirect, url_for
from website.database_management import read_statuses, update_tujuan_db, ROBOT_STATUS_FILE
from .route_calculation import a_star_search, coords
from .route_instructions import generate_instructions
from .mockup_robot import run_robot_simulation # Import fungsi robot
from .status_book_callingcard import StatusRobot, StatusElektronika, StatusPaket
import threading # Wajib import ini
import json 
import os

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
            db_data = json.load(f)
            current_status = db_data.get('status_robot', int(StatusRobot.ROBOT_STANDBY_DISTATION))
            tujuan_sekarang = db_data.get('tujuan_sekarang', '-')
            rute_sekarang = db_data.get('rute_terakhir', '-')
            instruksi_sekarang = db_data.get('instruksi_navigasi', [])
            print(f"[VIEW] Current Robot Status: {current_status}")


    if current_status in [int(StatusRobot.ROBOT_TIDAK_AKTIF),int(StatusRobot.ROBOT_MENGANTAR_PAKET), int(StatusRobot.ROBOT_TELAH_MENGANTAR_PAKET), int(StatusRobot.ROBOT_MENUJU_STATION)]:
        return render_template("dashboard_send.html", 
                               mode="MONITOR", # Flag khusus untuk HTML
                               status_code=current_status,
                               tujuan=tujuan_sekarang,
                               rute=rute_sekarang,
                               instruksi=instruksi_sekarang)
    
    # --- HANDLER FORM (Hanya aktif jika status == 1 atau 0) ---
    hasil_rute = ""
    status_rute = ""
    warna_status = ""
    list_instruksi = []

    if request.method == 'POST':
        tujuan = request.form.get('pilihan').upper()
        nama = request.form.get('nama')
        
        # Validasi Input
        path, msg = a_star_search('START', tujuan)
        
        if path:
            rute_str = " -> ".join(path)
            hasil_rute = rute_str
            status_rute = "RUTE OK! ROBOT DILUNCURKAN"
            warna_status = "text-success"
            
            list_instruksi = generate_instructions(path, coords)
            
            # JALANKAN ROBOT DI BACKGROUND (THREADING)
            # args=(tujuan, pengirim, rute_text, instruksi)
            robot_thread = threading.Thread(target=run_robot_simulation, 
                                            args=(tujuan, nama, rute_str, list_instruksi))
            robot_thread.start()
            
            # Redirect ke halaman send lagi (GET) agar tampilan langsung berubah jadi MONITOR
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