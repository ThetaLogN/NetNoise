import math
from collections import Counter
from main import EntropyEngine

def start():
    engine = EntropyEngine()
    with open("entropy.txt", "wb") as f:
        for i in range(10000):
            print(i)
            data = engine.random_bytes(32)
            f.write(data)

def load_data(filename):
    with open(filename, "rb") as f:
        return f.read()

def shannon_entropy(data):
    freq = Counter(data)
    total = len(data)
    entropy = 0
    for count in freq.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

def min_entropy(data):
    freq = Counter(data)
    total = len(data)
    max_p = max(count / total for count in freq.values())
    return -math.log2(max_p)

def bit_distribution(data):
    bits = "".join(f"{byte:08b}" for byte in data)
    return bits.count("0"), bits.count("1")

def chi_square_test(data):
    freq = Counter(data)
    expected = len(data) / 256
    chi2 = 0
    for i in range(256):
        observed = freq.get(i, 0)
        chi2 += ((observed - expected) ** 2) / expected
    return chi2

def serial_correlation(data):
    n = len(data)
    if n < 2:
        return 0
    mean = sum(data) / n
    num = sum((data[i] - mean) * (data[i+1] - mean) for i in range(n-1))
    den = sum((byte - mean) ** 2 for byte in data)
    return num / den if den != 0 else 0

def analyze(filename):
    start();
    data = load_data(filename)

    print("🔹 Campioni totali:", len(data))
    print()

    print("🔹 Shannon entropy:", round(shannon_entropy(data), 4), "(max 8.0)")
    print("🔹 Min-Entropy:", round(min_entropy(data), 4), "(max 8.0)")
    print()

    zeros, ones = bit_distribution(data)
    print("🔹 Distribuzione bit")
    print("0:", zeros, "1:", ones)
    print()

    print("🔹 Chi-Square:", round(chi_square_test(data), 2))
    print("🔹 Serial Correlation:", round(serial_correlation(data), 6))
    print()

    freq = Counter(data)
    print("🔹 Byte più frequenti (top 20)")
    for byte, count in freq.most_common(20):
        print(f"{byte:02x}: {count}")

if __name__ == "__main__":
    analyze("entropy.txt")