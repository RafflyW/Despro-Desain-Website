from flask import Blueprint, render_template, request
from website.database_management import read_statuses, update_tujuan_db
from .route_calculation import a_star_search, coords
from .route_instructions import generate_instructions

views = Blueprint('views', __name__)

@views.route('/')
def home():
    context = read_statuses()
    return render_template("dashboard_home.html", **context)

@views.route('/send', methods=['GET', 'POST'])
def send_page():
    hasil_rute = ""
    status_rute = ""
    warna_status = ""
    list_instruksi = [] # Variabel baru untuk menampung instruksi
    
    if request.method == 'POST':
        tujuan = request.form.get('pilihan').upper()
        nama = request.form.get('nama')
        
        path, msg = a_star_search('START', tujuan)
        
        if path:
            rute_str = " -> ".join(path)
            hasil_rute = rute_str
            status_rute = "RUTE OK!"
            warna_status = "text-success"
            
            # --- GENERATE INSTRUKSI ---
            # Panggil fungsi dari file route_instructions.py
            list_instruksi = generate_instructions(path, coords)
            
            # Simpan ke DB termasuk instruksinya
            update_tujuan_db(tujuan, nama, rute_str, list_instruksi)
        else:
            hasil_rute = "Lokasi tidak ditemukan."
            status_rute = "TIDAK TERSEDIA"
            warna_status = "text-danger"

    return render_template("dashboard_send.html", 
                           hasil_rute=hasil_rute, 
                           status_rute=status_rute,
                           warna_status=warna_status,
                           instruksi=list_instruksi) # Kirim ke HTML