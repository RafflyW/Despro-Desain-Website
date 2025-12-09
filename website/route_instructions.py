# website/route_instructions.py

def get_turn_direction(p1, p2, p3):
    # Hitung vektor untuk menentukan belok Kiri (-1) atau Kanan (1)
    dx1, dy1 = p2[0] - p1[0], p2[1] - p1[1]
    dx2, dy2 = p3[0] - p2[0], p3[1] - p2[1]
    cross_product = (dx1 * dy2) - (dy1 * dx2)
    
    # Toleransi lurus 0.5
    if -0.5 < cross_product < 0.5:
        return "Lurus", 0
    elif cross_product > 0:
        return "Belok Kiri", -1
    else:
        return "Belok Kanan", 1

def generate_instructions(path, coords):
    if not path or len(path) < 2:
        return ["Diam di tempat"], [4]

    text_list = []
    code_list = []
    
    # Start (Default maju/lurus = 0)
    text_list.append(f"Mulai dari {path[0]}")
    code_list.append(0) 
    
    for i in range(len(path) - 1):
        curr_node = path[i]
        next_node = path[i+1]
        
        if i == 0:
            text_list.append(f"Maju menuju {next_node}")
            continue
            
        prev_node = path[i-1]
        p1, p2, p3 = coords[prev_node], coords[curr_node], coords[next_node]
        
        direction_text, direction_code = get_turn_direction(p1, p2, p3)
        
        # Simpan Teks
        if direction_code == 0:
             text_list.append(f"Lurus di {curr_node} ke {next_node}")
        else:
             text_list.append(f"{direction_text} di {curr_node} menuju {next_node}")
        
        # Simpan Kode (Belokan + Lurus setelah belok)
        code_list.append(direction_code)
        if i < len(path) - 2:
            code_list.append(0)

    # Finish (Stop = 4)
    text_list.append("Sampai di Tujuan")
    code_list.append(4)
    
    return text_list, code_list

def generate_return_instructions(current_node, coords):
    from .route_calculation import a_star_search
    path, _ = a_star_search(current_node, 'START')
    if path:
        # Menangkap 2 output (text, code)
        text, codes = generate_instructions(path, coords)
        text.insert(0, "--- MODE PULANG ---")
        # Mengembalikan 3 hal: Teks, Kode, String Rute
        return text, codes, " -> ".join(path)
    return [], [], ""