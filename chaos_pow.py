from argon2 import PasswordHasher, Type
import base64

class ChaosPoW:
    TIME_COST = 2          
    MEMORY_COST = 65536    
    PARALLELISM = 1        
    HASH_LEN = 32          

    # Definiamo il numero massimo possibile (2^256, perché l'hash è 32 bytes)
    MAX_TARGET = 2**(HASH_LEN * 8) - 1

    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=self.TIME_COST,
            memory_cost=self.MEMORY_COST,
            parallelism=self.PARALLELISM,
            hash_len=self.HASH_LEN,
            type=Type.ID
        )

    def _check_hash(self, full_hash, difficulty):
        """
        Controlla se l'hash (convertito in numero) è minore del Target.
        Più alta è la difficoltà, più piccolo è il Target, più difficile è vincere.
        """
        try:
            # 1. Estraiamo la parte finale dell'hash (dopo l'ultimo $)
            b64_hash = full_hash.split("$")[-1]
            
            # 2. Aggiustiamo il padding Base64 (Python è pignolo)
            padding = '=' * ((4 - len(b64_hash) % 4) % 4)
            
            # 3. Decodifichiamo in Byte e poi in Numero Intero
            hash_bytes = base64.b64decode(b64_hash + padding)
            hash_int = int.from_bytes(hash_bytes, byteorder='big')
            
            # 4. Calcoliamo il bersaglio
            # Esempio: Se Difficoltà è 100, il bersaglio è 1/100 del massimo.
            target = self.MAX_TARGET // difficulty
            
            return hash_int <= target
        except Exception as e:
            return False

    def mine_block(self, entropy_data, difficulty):
        nonce = 0
        print(f"--- Mining Numerico (Difficoltà: {difficulty}) ---")
        
        while True:
            candidate_data = f"{entropy_data}{nonce}"
            full_hash = self.hasher.hash(candidate_data)
            
            # Usiamo la nuova verifica numerica
            if self._check_hash(full_hash, difficulty):
                return full_hash, nonce
            
            nonce += 1
            if nonce % 10 == 0:
                 print(f"\rTentativo {nonce}...", end="")

    def verify_mined_block(self, entropy_data, nonce, full_hash, difficulty):
        # 1. Verifica Crittografica (Argon2)
        try:
            candidate_data = f"{entropy_data}{nonce}"
            self.hasher.verify(full_hash, candidate_data)
        except:
            return False
            
        # 2. Verifica Numerica (Target)
        return self._check_hash(full_hash, difficulty)