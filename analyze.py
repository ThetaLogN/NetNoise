import json
import math
from collections import Counter
import matplotlib.pyplot as plt

def load_data(filename):
    print(f"--- Caricamento {filename} ---")
    with open(filename, 'r') as f:
        data = json.load(f)
    
    hex_stream = ""
    
    for block in data['chain'][1:]: 
        
        if len(block['entropy']) > 20: 
            hex_stream += block['entropy']
        
    return hex_stream

def shannon_entropy(hex_string):
    bytes_data = bytes.fromhex(hex_string)
    counts = Counter(bytes_data)
    total_len = len(bytes_data)
    
    entropy = 0
    for count in counts.values():
        p_x = count / total_len
        if p_x > 0:
            entropy += - p_x * math.log2(p_x)
            
    return entropy

def monte_carlo_pi(hex_string, num_points=5000):
    bytes_data = bytes.fromhex(hex_string)
    points_inside = 0
    total_points = min(num_points, len(bytes_data) // 8)
    
    x_coords = []
    y_coords = []
    
    for i in range(total_points):
        offset = i * 8
        x_bytes = bytes_data[offset : offset+4]
        y_bytes = bytes_data[offset+4 : offset+8]
        
        x = int.from_bytes(x_bytes, 'big') / (2**32 - 1)
        y = int.from_bytes(y_bytes, 'big') / (2**32 - 1)
        
        if (x**2 + y**2) <= 1.0:
            points_inside += 1
            
        if i < 1000:
            x_coords.append(x)
            y_coords.append(y)
            
    pi_estimate = 4 * points_inside / total_points
    return pi_estimate, x_coords, y_coords

# --- ESECUZIONE ---
try:
    stream = load_data("blockchain.json")
    print(f"Dati caricati: {len(stream)//2} bytes totali.")
    
    # 1. Shannon
    ent = shannon_entropy(stream)
    print(f"\n[1] Entropia di Shannon (Ideale: 8.0): {ent:.5f}")
    if ent < 7.5: print("   ⚠️ ATTENZIONE: Entropia bassa!")
    else: print("   ✅ Entropia Eccellente.")

    # 2. Monte Carlo
    print(f"\n[2] Stima Monte Carlo di Pi (Ideale: 3.14159...):")
    pi_val, xs, ys = monte_carlo_pi(stream)
    print(f"   Risultato: {pi_val:.5f}")
    err = abs(pi_val - 3.14159) / 3.14159 * 100
    print(f"   Errore: {err:.2f}%")
    
    # Grafico
    plt.figure(figsize=(6,6))
    plt.scatter(xs, ys, s=1, alpha=0.5)
    plt.title(f"Distribuzione Casuale (Monte Carlo)\nPi stimato: {pi_val:.4f}")
    plt.show()

except FileNotFoundError:
    print("Errore: File blockchain.json non trovato. Lancia prima il miner!")
except Exception as e:
    print(f"Errore: {e}")