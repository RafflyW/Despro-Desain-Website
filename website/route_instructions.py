# website/route_instructions.py

def get_turn_direction(p1, p2, p3):
    """
    Menentukan arah belokan dari 3 titik (Previous, Current, Next).
    Menggunakan Cross Product 2D.
    p = (x, y)
    """
    # Vektor Masuk (p1 ke p2)
    dx1 = p2[0] - p1[0]
    dy1 = p2[1] - p1[1]
    
    # Vektor Keluar (p2 ke p3)
    dx2 = p3[0] - p2[0]
    dy2 = p3[1] - p2[1]
    
    # Rumus Cross Product: (x1*y2 - y1*x2)
    cross_product = (dx1 * dy2) - (dy1 * dx2)
    
    # Threshold untuk toleransi "Lurus" (menghindari sedikit miring dianggap belok)
    if -0.5 < cross_product < 0.5:
        return "Lurus"
    elif cross_product > 0:
        return "Belok Kiri"
    else:
        return "Belok Kanan"

def generate_instructions(path, coords):
    """
    path: list nama node ['START', 'SIMPANG', ...]
    coords: dictionary koordinat {'START': (10,5), ...}
    """
    if not path or len(path) < 2:
        return ["Diam di tempat"]

    instructions = []
    
    # Instruksi awal
    instructions.append(f"Mulai dari {path[0]}")
    
    # Iterasi node untuk mencari belokan
    for i in range(len(path) - 1):
        curr_node = path[i]
        next_node = path[i+1]
        
        # Jika ini adalah langkah pertama (START -> Node selanjutnya)
        if i == 0:
            instructions.append(f"Maju menuju {next_node}")
            continue
            
        # Untuk langkah selanjutnya, kita butuh 3 titik: Prev, Curr, Next
        prev_node = path[i-1]
        
        p1 = coords[prev_node]
        p2 = coords[curr_node]
        p3 = coords[next_node]
        
        # Cek arah belokan
        direction = get_turn_direction(p1, p2, p3)
        
        if direction == "Lurus":
             instructions.append(f"Lurus melewati {curr_node} ke {next_node}")
        else:
             instructions.append(f"{direction} di {curr_node} menuju {next_node}")

    instructions.append("Sampai di Tujuan")
    return instructions