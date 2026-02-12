import socket
import threading
import json
import time
import os
# Assicurati che chaos_pow.py sia nella stessa cartella e sia quello NUOVO
from chaos_pow import ChaosPoW

class BlockManager:
    def __init__(self):
        self.filename = "blockchain.json"
        self.target_time_per_block = 15.0  # Cerchiamo di avere un blocco ogni 15s
        self.retarget_epoch = 5 # Ogni quanti blocchi ricalcoliamo la difficoltà
        
        # Inizializziamo la difficoltà a 50 (valore sensato per il sistema numerico)
        self.difficulty = 300
        self.blocks = []
        self.last_adjustment_time = time.time()

        if os.path.exists(self.filename):
            self.load_chain()
        else:
            print("   [INIT] Nessuna blockchain trovata. Creazione GENESIS BLOCK...")
            self.create_genesis_block()

    def create_genesis_block(self):
        """Il primo blocco della storia"""
        genesis_block = {
            "index": 0,
            "timestamp": time.time(),
            "entropy": "GENESIS_CHAOS_MESH",
            "nonce": 0,
            "hash": "0" * 64, # Hash fittizio per il genesis
            "previous_hash": "0"
        }
        self.blocks.append(genesis_block)
        self.save_chain()

    def add_block(self, block_data):
        last_block = self.blocks[-1]
        
        full_block = {
            "index": len(self.blocks),
            "timestamp": time.time(),
            "entropy": block_data['entropy'],
            "nonce": block_data['nonce'],
            "hash": block_data['hash'],
            "previous_hash": last_block['hash'] 
        }
        
        self.blocks.append(full_block)
        print(f"   [CHAIN] Blocco #{full_block['index']} salvato. (Diff: {self.difficulty})")
        
        self.save_chain()
  
        # Controlliamo se è ora di aggiustare la difficoltà
        if len(self.blocks) % self.retarget_epoch == 0:
            self.adjust_difficulty()

    def save_chain(self):
        state = {
            "chain": self.blocks,
            "difficulty": self.difficulty,
            "last_adjustment_time": self.last_adjustment_time
        }
        try:
            with open(self.filename, 'w') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            print(f"⚠️ Errore salvataggio file: {e}")

    def load_chain(self):
        try:
            with open(self.filename, 'r') as f:
                state = json.load(f)
                self.blocks = state['chain']
                # Se nel file c'è una difficoltà vecchia (es. 1), la forziamo a 50
                loaded_diff = state.get('difficulty', 50)
                self.difficulty = max(10, loaded_diff) 
                
                self.last_adjustment_time = state.get('last_adjustment_time', time.time())
                print(f"   [INIT] Blockchain caricata! {len(self.blocks)} blocchi. Difficoltà: {self.difficulty}")
        except Exception as e:
            print(f"⚠️ Errore caricamento file: {e}. Riparto da zero.")
            self.blocks = []
            self.create_genesis_block()

    def adjust_difficulty(self):
        now = time.time()
        elapsed = now - self.last_adjustment_time
        # Tempo atteso per X blocchi
        expected = self.target_time_per_block * self.retarget_epoch
        
        print(f"\n   [RETARGET] Ultimi {self.retarget_epoch} blocchi in {elapsed:.2f}s (Target: {expected}s)")
        
        changed = False
        
        if elapsed < expected * 0.5: # Troppo veloce (< 50% del tempo)
            # Aumentiamo la difficoltà (il divisore diventa più grande -> target più piccolo)
            old_diff = self.difficulty
            self.difficulty = int(self.difficulty * 1.2) # +20%
            if self.difficulty == old_diff: self.difficulty += 1
            print(f"   📈 DIFFICULTY UP! {old_diff} -> {self.difficulty}")
            changed = True
        
        elif elapsed > expected * 1.5: # Troppo lento (> 150% del tempo)
            old_diff = self.difficulty
            self.difficulty = int(self.difficulty * 0.8) # -20%
            if self.difficulty < 10: self.difficulty = 10 # Minimo sindacale
            print(f"   📉 DIFFICULTY DOWN! {old_diff} -> {self.difficulty}")
            changed = True
        
        else:
            print(f"   Difficoltà bilanciata. Rimane {self.difficulty}")

        self.last_adjustment_time = now
        
        # Salviamo subito la nuova difficoltà nel file
        if changed:
            self.save_chain()

class ChaosServer:
    def __init__(self, host='0.0.0.0', port=5050):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Opzione per riutilizzare la porta subito se riavvii il server
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.sock.listen(5)
        self.manager = BlockManager()
        # Istanziamo il motore che sa fare i calcoli numerici
        self.pow_verifier = ChaosPoW()

    def start(self):
        print(f"--- ChaosMesh Server su porta 5050 (Difficoltà Numerica) ---")
        while True:
            client, addr = self.sock.accept()
            # Gestiamo ogni miner in un thread separato
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        try:
            # 1. SALUTO: Inviamo la difficoltà attuale al Miner
            welcome_packet = {"current_difficulty": self.manager.difficulty}
            client.send(json.dumps(welcome_packet).encode())
            
            # 2. RICEZIONE: Aspettiamo il blocco
            data = client.recv(4096).decode().strip()
            if not data: return
            
            try:
                block = json.loads(data)
                self.verify_and_add(block, client)
            except json.JSONDecodeError:
                pass # Dati sporchi ignorati
            
        except Exception as e:
            print(f"Errore client: {e}")
        finally:
            client.close()

    def verify_and_add(self, block, client):
        entropy = block.get("entropy")
        nonce = block.get("nonce")
        claimed_hash = block.get("hash")
        
        # La difficoltà richiesta è quella che ha il server ORA
        required_diff = self.manager.difficulty
        
        print(f"   Verifica Blocco (Nonce: {nonce})... ", end="")

        # --- VERIFICA NUOVA (NUMERICA) ---
        # Usiamo il metodo verify_mined_block di ChaosPoW
        # Questo controlla SIA che l'hash corrisponda (Argon2 verify)
        # SIA che il valore numerico sia sotto il target.
        is_valid = self.pow_verifier.verify_mined_block(
            entropy, 
            nonce, 
            claimed_hash, 
            required_diff
        )
        
        if is_valid:
            print("✅ VALIDO!")
            self.manager.add_block(block)
            client.send(b"ACCEPTED")
        else:
            print("❌ INVALIDO (Hash errato o Difficoltà non raggiunta)")
            client.send(b"REJECTED")

if __name__ == "__main__":
    ChaosServer().start()