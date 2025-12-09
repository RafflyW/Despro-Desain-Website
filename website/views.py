from flask import Blueprint, render_template, request, redirect, url_for, jsonify # Added jsonify
from website.database_management import read_statuses, update_tujuan_db, ROBOT_STATUS_FILE
from .route_calculation import a_star_search, coords
from .route_instructions import generate_instructions
from .mockup_robot import run_robot_simulation # Function for simulation
from .status_book_callingcard import StatusRobot, StatusElektronika, StatusPaket
import threading
import json 
import os

views = Blueprint('views', __name__)

@views.route('/')
def home():
    context = read_statuses()
    return render_template("dashboard_home.html", **context)

# --- NEW API ENDPOINT FOR ESP32 ---
@views.route('/api/robot-data')
def api_robot_data():
    """
    ESP32 polls this to get the current status and route.
    """
    if os.path.exists(ROBOT_STATUS_FILE):
        with open(ROBOT_STATUS_FILE, 'r') as f:
            data = json.load(f)
            return jsonify(data)
    return jsonify({"error": "Database not found"}), 404

@views.route('/send', methods=['GET', 'POST'])
def send_page():
    # ... (Existing logic to read status) ...
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

    # If robot is busy, show MONITOR mode
    if current_status in [104, 105, 106, 107]: # Simplified list
         return render_template("dashboard_send.html", 
                               mode="MONITOR",
                               status_code=current_status,
                               tujuan=tujuan_sekarang,
                               rute=rute_sekarang,
                               instruksi=instruksi_sekarang)

    # --- HANDLER FORM ---
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
            status_rute = "RUTE OK! ROBOT DILUNCURKAN (SIMULASI)"
            warna_status = "text-success"
            
            # 1. Generate Instructions for ESP32
            list_instruksi = generate_instructions(path, coords)
            
            # 2. Start the Simulation Thread (This drives the database updates)
            # This will automatically change status 104 -> 105 -> 106 over time
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