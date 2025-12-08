import heapq
import math

# === 1. DEFINISI GRAPH (JALUR DAN KONEKSI) ===
# Format: 'NODE_AWAL': {'NODE_TUJUAN': JARAK}
graph = {
    # --- AREA START & UTAMA ---
    'START': {'SIMPANG_UTAMA': 2},
    'SIMPANG_UTAMA': {'START': 2, 'SIMPANG_KIRI_1': 3, 'BELOKAN_KANAN_AWAL': 3},

    # --- JALUR KANAN (MENUJU 11B, 12A, 12B) ---
    'BELOKAN_KANAN_AWAL': {'SIMPANG_UTAMA': 3, 'SIMPANG_KANAN_1': 3},
    
    'SIMPANG_KANAN_1': {
        'BELOKAN_KANAN_AWAL': 3, 
        '11B': 2, '12A': 2, '12B': 2
    },
    '11B': {'SIMPANG_KANAN_1': 2},
    '12A': {'SIMPANG_KANAN_1': 2},
    '12B': {'SIMPANG_KANAN_1': 2},

    # --- JALUR KIRI (MENUJU 10A, 10B, 11A) ---
    'SIMPANG_KIRI_1': {
        'SIMPANG_UTAMA': 3,
        'SIMPANG_KIRI_2': 2,     # Kanan (naik)
        'BELOKAN_MENUJU_SK3': 2  # Lurus (kiri)
    },

    # Sub-Jalur Kiri Atas (Menuju 11A)
    'SIMPANG_KIRI_2': {
        'SIMPANG_KIRI_1': 2,
        'BELOKAN_11A': 2,
        'SIMPANG_KIRI_3': 3
    },
    'BELOKAN_11A': {'SIMPANG_KIRI_2': 2, '11A': 2},
    '11A': {'BELOKAN_11A': 2},

    # Sub-Jalur Kiri Bawah (Menuju 10A, 10B)
    'BELOKAN_MENUJU_SK3': {'SIMPANG_KIRI_1': 2, 'SIMPANG_KIRI_3': 2},
    
    'SIMPANG_KIRI_3': {
        'BELOKAN_MENUJU_SK3': 2,
        '10A': 2, '10B': 2,
        'SIMPANG_KIRI_2': 3
    },
    '10A': {'SIMPANG_KIRI_3': 2},
    '10B': {'SIMPANG_KIRI_3': 2}
}

# === 2. KOORDINAT (X, Y) UNTUK LOGIKA BELOKAN ===
coords = {
    'START':           (10, 0),
    'SIMPANG_UTAMA':   (10, 3),

    # Area Kanan
    'BELOKAN_KANAN_AWAL': (16, 3),
    'SIMPANG_KANAN_1':    (16, 8),
    '11B':                (14, 8),
    '12A':                (16, 11),
    '12B':                (18, 8),

    # Area Kiri
    'SIMPANG_KIRI_1':     (4, 3),
    'SIMPANG_KIRI_2':     (4, 8),
    'BELOKAN_11A':        (4, 12),
    '11A':                (6, 12),
    'BELOKAN_MENUJU_SK3': (1, 3),
    'SIMPANG_KIRI_3':     (1, 8),
    '10A':                (-1, 8),
    '10B':                (1, 11)
}

# === 3. FUNGSI A* (Standar) ===
def heuristic(node, goal):
    if node not in coords or goal not in coords: return 999
    x1, y1 = coords[node]
    x2, y2 = coords[goal]
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def a_star_search(start, goal):
    start, goal = start.upper(), goal.upper()
    if start not in graph or goal not in graph: return None, "Lokasi tidak ada"
    queue = [(0, start, [])]
    visited = set()
    while queue:
        cost, current, path = heapq.heappop(queue)
        path = path + [current]
        if current == goal: return path, "OK"
        if current in visited: continue
        visited.add(current)
        for neighbor, weight in graph[current].items():
            if neighbor not in visited:
                heapq.heappush(queue, (cost + weight + heuristic(neighbor, goal), neighbor, path))
    return None, "Jalur Tidak Ditemukan"