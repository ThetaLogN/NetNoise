import threading
import time
import socket
import hashlib
from chaos_pow import ChaosPoW 
import json
import socket

class EntropyCollector:
    def __init__(self):
        self.entropy_pool = []
        self.target_servers = ["8.8.8.8", "1.1.1.1", "9.9.9.9"] 
        self.counter = 0
        self.lock = threading.Lock()

    def get_network_jitter(self):
        """Fase 1: Misura lo scarto temporale dei pacchetti UDP"""
        for server in self.target_servers:
            t1 = time.perf_counter_ns()
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(0.5) # Timeout breve per non bloccare
            try:
                # Inviamo pacchetto vuoto porta 53 (DNS)
                sock.sendto(b"", (server, 53))
                sock.recvfrom(1024)
                t2 = time.perf_counter_ns()
                
                delta = t2 - t1
                # Prendiamo il modulo 16 per avere solo il "rumore" di fondo
                self.entropy_pool.append(str(delta % 16))
            except Exception:
                # Anche un errore/timeout è entropia (dipende dal carico di rete)
                self.entropy_pool.append(str(time.perf_counter_ns() % 16))
            finally:
                sock.close()

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
        
        execution_time = t_end - t_start
        self.entropy_pool.append(str(execution_time))

    def generate_true_random(self):
        """Fase 3: Raccolta e Whitening (SHA-3)"""
        # Puliamo il pool vecchio
        self.entropy_pool = []
        
        self.get_network_jitter()
        self.get_cpu_noise()
        
        # Uniamo tutto
        raw_data = "".join(self.entropy_pool).encode()
        
        # Hashing per uniformare la distribuzione
        clean_entropy = hashlib.sha3_256(raw_data).hexdigest()
        return clean_entropy


def run_miner_node():
    collector = EntropyCollector()
    pow_engine = ChaosPoW()
    
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5050

    print(f"--- NetNoise ---")

    while True:
        try:
            print("\n[1] Generazione Entropia...")
            raw_entropy = collector.generate_true_random()
            
            current_difficulty = 1 
            try:
                s_check = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s_check.connect((SERVER_IP, SERVER_PORT))
            
                response = s_check.recv(1024).decode()
                config = json.loads(response)
                current_difficulty = config['current_difficulty']
                s_check.close()
                
            except Exception as e:
                print(f"⚠️ Server non raggiungibile, uso difficoltà base (1). Err: {e}")

            print(f"[2] Mining con Difficoltà: {current_difficulty} (Target: '{'0'*current_difficulty}')...")
            start_t = time.time()
            
            
            full_hash, nonce = pow_engine.mine_block(raw_entropy, current_difficulty)
            
            duration = time.time() - start_t
            print(f">>> TROVATO in {duration:.2f}s! Nonce: {nonce}")

    
            print("[3] Invio soluzione...")
            payload = {
                "entropy": raw_entropy,
                "nonce": nonce,
                "hash": full_hash
            }
            
            s_send = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_send.connect((SERVER_IP, SERVER_PORT))
            
            s_send.recv(1024) 
            
            s_send.send(json.dumps(payload).encode())
            
            result = s_send.recv(1024).decode()
            if "ACCEPTED" in result:
                print("✅ Accettato!")
            else:
                print(f"❌ Rifiutato dal server: {result}")
            
            s_send.close()
 
            time.sleep(1)

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_miner_node()