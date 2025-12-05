import heapq
import math

# 1. DEFINISI PETA (GRAPH) SESUAI GAMBAR DENAH
# Kita tambahkan node 'Invisible' (SIMPANG) agar jalur terlihat nyata
# Struktur:
# START -> SIMPANG_UTAMA
# SIMPANG_UTAMA -> (Naik) -> J_ATAS -> Area 10 & 11
# SIMPANG_UTAMA -> (Diagonal) -> J_BAWAH -> Area 12 & 13

graph = {
    'START': {'SIMPANG_UTAMA': 2},
    'SIMPANG_UTAMA': {'START': 2, 'J_ATAS': 3, 'J_BAWAH': 3},
    
    # Area Atas (10A, 10B, 11A, 11B)
    'J_ATAS': {'SIMPANG_UTAMA': 3, '10B': 2, '10A': 2, '11B': 2},
    '10B': {'J_ATAS': 2},
    '10A': {'J_ATAS': 2},
    '11B': {'J_ATAS': 2, '11A': 2}, # 11A ada di ujung setelah 11B
    '11A': {'11B': 2},

    # Area Bawah (12A, 12B, 13A, 13B)
    'J_BAWAH': {'SIMPANG_UTAMA': 3, '13A': 2},
    '13A': {'J_BAWAH': 2, '13B': 1},
    '13B': {'13A': 1, '12A': 2, '12B': 2}, # 13B adalah persimpangan kecil ke 12
    '12A': {'13B': 2},
    '12B': {'13B': 2}
}

# Koordinat (X, Y) Imajiner untuk hitungan Heuristik (Jarak Garis Lurus)
# Dibuat berdasarkan posisi visual di gambar denah Anda
coords = {
    'START': (10, 5),
    'SIMPANG_UTAMA': (8, 5),
    'J_ATAS': (8, 8),
    '10A': (6, 8),
    '10B': (2, 7),
    '11B': (2, 9),
    '11A': (0, 9),
    'J_BAWAH': (6, 3),
    '13A': (5, 3),
    '13B': (4, 3),
    '12A': (2, 4),
    '12B': (2, 2)
}

def heuristic(node, goal):
    # Rumus Euclidean Distance
    if node not in coords or goal not in coords:
        return 999 # Jika node tidak dikenal, beri nilai tinggi
    x1, y1 = coords[node]
    x2, y2 = coords[goal]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def a_star_search(start, goal):
    # Normalisasi input agar huruf besar semua (misal user ketik 11a jadi 11A)
    start = start.upper()
    goal = goal.upper()

    if start not in graph or goal not in graph:
        return None, "Lokasi tidak ada di Peta"

    queue = [(0, start, [])]
    visited = set()
    
    while queue:
        cost, current, path = heapq.heappop(queue)
        path = path + [current]
        
        if current == goal:
            return path, "OK"
        
        if current in visited:
            continue
        visited.add(current)
        
        for neighbor, weight in graph[current].items():
            if neighbor not in visited:
                g_cost = cost + weight
                h_cost = heuristic(neighbor, goal)
                f_cost = g_cost + h_cost
                heapq.heappush(queue, (f_cost, neighbor, path))
                
    return None, "Jalur Tidak Ditemukan"