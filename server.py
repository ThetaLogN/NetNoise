import socket
import threading
import json
import time
from chaos_pow import ChaosPoW
import os

class BlockManager:
    def __init__(self):
        self.filename = "blockchain.json"
        self.target_time_per_block = 10 
        self.retarget_epoch = 5
        
        if os.path.exists(self.filename):
            self.load_chain()
        else:
            print("   [INIT] Nessuna blockchain trovata. Creazione GENESIS BLOCK...")
            self.blocks = []
            self.difficulty = 1
            self.last_adjustment_time = time.time()
            self.create_genesis_block()

    def create_genesis_block(self):
        """Il primo blocco della storia (non ha predecessori)"""
        genesis_block = {
            "index": 0,
            "timestamp": time.time(),
            "entropy": "GENESIS",
            "nonce": 0,
            "hash": "0" * 64,
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
        print(f"   [CHAIN] Blocco #{full_block['index']} save.")
        
        self.save_chain()
  
        if len(self.blocks) % self.retarget_epoch == 0:
            self.adjust_difficulty()

    def save_chain(self):
        """Scrive tutto lo stato su file JSON"""
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
        """Legge lo stato dal file JSON"""
        try:
            with open(self.filename, 'r') as f:
                state = json.load(f)
                self.blocks = state['chain']
                self.difficulty = state['difficulty']
                self.last_adjustment_time = state.get('last_adjustment_time', time.time())
                print(f"   [INIT] Blockchain caricata! {len(self.blocks)} blocchi. Difficoltà: {self.difficulty}")
        except Exception as e:
            print(f"⚠️ Errore caricamento file (corrotto?): {e}")
            self.blocks = []
            self.create_genesis_block()

    def adjust_difficulty(self):
        now = time.time()
        elapsed = now - self.last_adjustment_time
        expected = self.target_time_per_block * self.retarget_epoch
        
        print(f"\n   [RETARGET] Tempo trascorso: {elapsed:.2f}s (Atteso: {expected}s)")
        
        changed = False
        if elapsed < expected * 0.5:
            self.difficulty += 1
            print(f"   >>> DIFFICULTY UP! Nuova difficoltà: {self.difficulty}")
            changed = True
        elif elapsed > expected * 1.5:
            if self.difficulty > 1:
                self.difficulty -= 1
                print(f"   >>> DIFFICULTY DOWN! Nuova difficoltà: {self.difficulty}")
                changed = True
        
        self.last_adjustment_time = now
  
        if changed:
            self.save_chain()

class ChaosServer:
    def __init__(self, host='0.0.0.0', port=5050):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((host, port))
        self.sock.listen(5)
        self.manager = BlockManager()
        self.pow_verifier = ChaosPoW()

    def start(self):
        print(f"--- ChaosMesh Server su porta 5050 ---")
        while True:
            client, addr = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        try:
            # 1. Appena il miner si connette, GLI DICIAMO LA DIFFICOLTÀ ATTUALE
            welcome_packet = {"current_difficulty": self.manager.difficulty}
            client.send(json.dumps(welcome_packet).encode() + b"\n") 
            
            # 2. Riceviamo il blocco dal miner
            data = client.recv(4096).decode().strip()
            if not data: return
            
            block = json.loads(data)
            self.verify_and_add(block, client)
            
        except Exception as e:
            print(f"Errore: {e}")
        finally:
            client.close()

    def verify_and_add(self, block, client):
        # Estraiamo i dati
        entropy = block.get("entropy")
        nonce = block.get("nonce")
        claimed_hash = block.get("hash")
        
        # Il server usa la SUA difficoltà attuale per verificare, non quella del miner
        required_diff = self.manager.difficulty 
        target_prefix = "0" * required_diff
        
        # Verifica 1: Difficoltà
        hash_part = claimed_hash.split("$")[-1]
        if not hash_part.startswith(target_prefix):
            print(f"   ❌ RIFIUTATO: Difficoltà troppo bassa (Richiesto: {required_diff})")
            client.send(b"REJECTED_LOW_DIFF")
            return

        # Verifica 2: Crittografia (Argon2)
        try:
            candidate = f"{entropy}{nonce}"
            self.pow_verifier.hasher.verify(claimed_hash, candidate)
            
            print(f"   ✅ ACCETTATO! (Nonce: {nonce})")
            self.manager.add_block(block)
            client.send(b"ACCEPTED")
            
        except:
            print("   ❌ RIFIUTATO: Hash non valido.")
            client.send(b"REJECTED_BAD_HASH")

if __name__ == "__main__":
    ChaosServer().start()