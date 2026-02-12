import threading
import time
import socket
import hashlib
import json
# Assicurati di avere il file chaos_pow.py aggiornato (versione numerica) nella stessa cartella!
from chaos_pow import ChaosPoW 

class EntropyCollector:
    def __init__(self):
        self.entropy_pool = []
        # Aggiunto timeout globale per evitare blocchi
        socket.setdefaulttimeout(1)
        self.target_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"] 
        self.counter = 0
        self.lock = threading.Lock()

    def get_network_jitter(self):
        """Fase 1: Misura lo scarto temporale dei pacchetti UDP"""
        for server in self.target_servers:
            t1 = time.perf_counter_ns()
            try:
                # Usa socket usa e getta per pulizia
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(b"", (server, 53))
                sock.recvfrom(1024)
                t2 = time.perf_counter_ns()
                delta = t2 - t1
                self.entropy_pool.append(str(delta % 16))
                sock.close()
            except Exception:
                self.entropy_pool.append(str(time.perf_counter_ns() % 16))

    def race_condition_worker(self):
        """Worker per creare collisioni sulla CPU"""
        for _ in range(1000):
            with self.lock:
                self.counter += 1

    def get_cpu_noise(self):
        """Fase 2: Genera rumore termico/scheduling CPU"""
        self.counter = 0
        threads = []
        t_start = time.perf_counter_ns()
        for _ in range(2):
            t = threading.Thread(target=self.race_condition_worker)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        t_end = time.perf_counter_ns()
        self.entropy_pool.append(str(t_end - t_start))

    def generate_true_random(self):
        """Fase 3: Raccolta e Whitening (SHA-3)"""
        self.entropy_pool = []
        self.get_network_jitter()
        self.get_cpu_noise()
        raw_data = "".join(self.entropy_pool).encode()
        return hashlib.sha3_256(raw_data).hexdigest()

def run_miner_node():
    collector = EntropyCollector()
    pow_engine = ChaosPoW()
    
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5050 # Assicurati che il server ascolti su questa porta

    print(f"--- NetNoise Miner ---")

    while True:
        try:
            # 1. GENERAZIONE ENTROPIA
            print("\n[1] Generazione Entropia...", end="\r")
            raw_entropy = collector.generate_true_random()
            
            # 2. RICHIESTA DIFFICOLTA'
            current_difficulty = 50
            try:
                s_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_check.connect((SERVER_IP, SERVER_PORT))
                response = s_check.recv(1024).decode()
                config = json.loads(response)
                current_difficulty = int(config.get('current_difficulty', 50))
                s_check.close()
            except Exception as e:
                print(f"\n⚠️ Server offline? Uso diff locale: {current_difficulty}")

            # 3. MINING (Logica Numerica)
            # Nota: Non stampiamo più gli '000', ma il divisore.
            print(f"[2] Mining... (Difficoltà: {current_difficulty})")
            
            start_t = time.time()
            
            # Qui chiamiamo la nuova funzione numerica
            full_hash, nonce = pow_engine.mine_block(raw_entropy, current_difficulty)
            
            duration = time.time() - start_t
            print(f">>> TROVATO in {duration:.2f}s! Nonce: {nonce}")

            # 4. INVIO SOLUZIONE
            print("[3] Invio soluzione...", end="")
            payload = {
                "entropy": raw_entropy,
                "nonce": nonce,
                "hash": full_hash
            }
            
            s_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_send.connect((SERVER_IP, SERVER_PORT))
            
            # Ignoriamo il messaggio di benvenuto (che contiene la difficulty)
            s_send.recv(1024) 
            
            # Inviamo il blocco
            s_send.send(json.dumps(payload).encode())
            
            result = s_send.recv(1024).decode()
            if "ACCEPTED" in result:
                print(" -> ✅ Accettato!")
            else:
                print(f" -> ❌ Rifiutato: {result}")
            
            s_send.close()
 
            # Piccola pausa per non fondere la CPU
            time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Mining interrotto dall'utente.")
            break
        except Exception as e:
            print(f"\n❌ Errore critico nel loop: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_miner_node()