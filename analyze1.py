import binascii
from collections import Counter
import math
import matplotlib.pyplot as plt
import time
from main import MultiSourceEntropy

# -----------------------------
# Funzioni statistiche
# -----------------------------
def shannon_entropy(byte_data):
    """Calcola l'entropia di Shannon in bit per byte"""
    if len(byte_data) == 0:
        return 0
    counts = Counter(byte_data)
    total = len(byte_data)
    entropy = -sum((count/total) * math.log2(count/total) for count in counts.values())
    return entropy

def bit_distribution(byte_data):
    """Conta quanti 0 e 1 ci sono in totale"""
    bits = bin(int(binascii.hexlify(byte_data), 16))[2:].zfill(len(byte_data)*8)
    counts = Counter(bits)
    return counts

def byte_distribution(byte_data):
    """Conta la frequenza di ogni byte (0-255)"""
    counts = Counter(byte_data)
    return counts

def plot_byte_histogram(byte_counts):
    plt.figure(figsize=(12,6))
    x = list(range(256))
    y = [byte_counts.get(i, 0) for i in x]
    plt.bar(x, y, color='skyblue')
    plt.title("Distribuzione dei byte (0-255)")
    plt.xlabel("Byte value")
    plt.ylabel("Frequenza")
    plt.show()

def plot_bit_histogram(bit_counts):
    plt.figure(figsize=(6,4))
    bits = ['0','1']
    counts = [bit_counts.get('0',0), bit_counts.get('1',0)]
    plt.bar(bits, counts, color='orange')
    plt.title("Distribuzione bit 0/1")
    plt.ylabel("Frequenza")
    plt.show()

# -----------------------------
# Generazione batch di campioni
# -----------------------------
def generate_samples(n_samples=10000):
    collector = MultiSourceEntropy()
    samples = []
    print(f"Generando {n_samples} campioni raw_entropy...")
    start_time = time.time()
    for i in range(n_samples):
        raw_hex = collector.generate_entropy()
        samples.append(raw_hex)
        if (i+1) % 50 == 0:
            print(f"- {i+1} campioni generati")
    duration = time.time() - start_time
    print(f"Fatto in {duration:.2f} secondi")
    return samples

# -----------------------------
# Salvataggio su file
# -----------------------------
def save_samples(filename, samples):
    with open(filename, "w") as f:
        for s in samples:
            f.write(s + "\n")
    print(f"Campioni salvati in {filename}")

# -----------------------------
# Analisi batch
# -----------------------------
def analyze_samples(samples):
    all_bytes = b"".join([bytes.fromhex(h) for h in samples])

    # Shannon
    entropy = shannon_entropy(all_bytes)
    print(f"\n🔹 Shannon entropy media (bit/byte): {entropy:.4f} (max 8.0)")

    # Distribuzione bit
    bits_count = bit_distribution(all_bytes)
    print(f"🔹 Distribuzione bit totale: 0: {bits_count.get('0',0)}, 1: {bits_count.get('1',0)}")
    plot_bit_histogram(bits_count)

    # Distribuzione byte
    bytes_count = byte_distribution(all_bytes)
    print("\n🔹 Distribuzione byte (primi 20 più frequenti)")
    for b, c in bytes_count.most_common(20):
        print(f"{b:02x}: {c}")
    plot_byte_histogram(bytes_count)

    # Report sintetico
    print("\n🔹 Report conclusivo:")
    print(f"- Campioni totali: {len(samples)}")
    print(f"- Byte totali: {len(all_bytes)}")
    print(f"- Entropia massima teorica: 8.0")
    print(f"- Entropia media osservata: {entropy:.4f}")
    print(f"- Distribuzione bit bilanciata: {'si' if abs(bits_count['0']-bits_count['1'])<len(all_bytes)*0.05 else 'no'}")

# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    N_SAMPLES = 10000
    FILENAME = "raw_entropy_samples.txt"

    # Genera
    samples = generate_samples(N_SAMPLES)

    # Salva
    save_samples(FILENAME, samples)

    # Analizza
    analyze_samples(samples)