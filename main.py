import os
import time
import threading
import socket
import hashlib
import struct
import ctypes
from collections import Counter

# -----------------------------
# Controllo RDRAND support
# -----------------------------
def rdrand_supported():
    try:
        ctypes.CDLL(None).__builtin_ia32_rdrand64_step
        return True
    except AttributeError:
        return False

def rdrand64():
    """Ritorna un intero 64bit casuale tramite RDRAND"""
    val = ctypes.c_uint64()
    ok = ctypes.CDLL(None).__builtin_ia32_rdrand64_step(ctypes.byref(val))
    if ok != 1:
        raise RuntimeError("RDRAND fallito")
    return val.value

# -----------------------------
# Entropy Collector
# -----------------------------
class MultiSourceEntropy:
    def __init__(self):
        self.entropy_pool = []
        self.lock = threading.Lock()
        self.counter = 0
        socket.setdefaulttimeout(0.5)
        self.target_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"]

    # ---- Network jitter
    def network_entropy(self):
        for server in self.target_servers:
            t1 = time.perf_counter_ns()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"", (server, 53))
                sock.recvfrom(1024)
                t2 = time.perf_counter_ns()
                delta = t2 - t1
                self.entropy_pool.append(struct.pack(">Q", delta))
                sock.close()
            except:
                self.entropy_pool.append(struct.pack(">Q", time.perf_counter_ns() % (2**64)))

    # ---- CPU race / cache jitter
    def race_worker(self):
        for _ in range(1000):
            with self.lock:
                self.counter += 1

    def cpu_entropy(self):
        self.counter = 0
        threads = []
        t_start = time.perf_counter_ns()
        for _ in range(4):
            t = threading.Thread(target=self.race_worker)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        t_end = time.perf_counter_ns()
        self.entropy_pool.append(struct.pack(">Q", t_end - t_start))
        self.entropy_pool.append(struct.pack(">Q", self.counter))

    # ---- Clock drift
    def clock_entropy(self):
        self.entropy_pool.append(struct.pack(">Q", int(time.perf_counter_ns())))

    # ---- Disk / filesystem
    def disk_entropy(self):
        try:
            f = open("/tmp/.entropy_file", "rb")
            data = f.read(64)
            self.entropy_pool.append(data)
            f.close()
        except:
            self.entropy_pool.append(os.urandom(64))

    # ---- OS entropy
    def os_entropy(self):
        self.entropy_pool.append(os.urandom(64))

    # ---- RDRAND
    def rdrand_entropy(self):
        if rdrand_supported():
            for _ in range(4):
                val = rdrand64()
                self.entropy_pool.append(struct.pack(">Q", val))

    # ---- Raccolta completa
    def generate_entropy(self):
        self.entropy_pool = []

        self.network_entropy()
        self.cpu_entropy()
        self.clock_entropy()
        self.disk_entropy()
        self.os_entropy()
        self.rdrand_entropy()

        # Combine tutti i dati e whitening finale
        raw = b"".join(self.entropy_pool)
        final = hashlib.sha3_256(raw).digest()  # 256 bit uniformi
        #return final
        return raw

# -----------------------------
# Test rapido
# -----------------------------
if __name__ == "__main__":
    collector = MultiSourceEntropy()
    sample = collector.generate_entropy()
    print(f"✅ Entropy TRNG 256bit: {sample.hex()}")