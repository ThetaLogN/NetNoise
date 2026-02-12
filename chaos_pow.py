from argon2 import PasswordHasher, Type
import secrets

class ChaosPoW:
    # Parametri Base 
    TIME_COST = 2          
    MEMORY_COST = 65536    # 64 MB
    PARALLELISM = 1        
    HASH_LEN = 32          

    def __init__(self):
        self.hasher = PasswordHasher(
            time_cost=self.TIME_COST,
            memory_cost=self.MEMORY_COST,
            parallelism=self.PARALLELISM,
            hash_len=self.HASH_LEN,
            type=Type.ID
        )

    def mine_block(self, entropy_data, difficulty_zeros):
        """
        [MINING LOOP]
        Continua a provare diversi 'Nonce' finché l'hash generato
        non inizia con un numero sufficiente di Zeri.
        """
        nonce = 0
        prefix_target = "0" * difficulty_zeros 
        
        print(f"--- Inizio Mining (Target: hash che inizia con '{prefix_target}') ---")
        
        while True:
            # Uniamo i dati: Entropia + Un numero che cambia sempre (Nonce)
            candidate_data = f"{entropy_data}{nonce}"
            
            # Calcoliamo l'hash 
            full_hash = self.hasher.hash(candidate_data)
            
            hashed_value = full_hash.split("$")[-1]
            
            # CONTROLLO LOTTERIA: Inizia con gli zeri richiesti?
            # Nota: In un sistema reale si converte in binario, qui usiamo stringhe per semplicità
            if hashed_value.startswith(prefix_target):
                return full_hash, nonce
            
            # Se non va bene, incrementiamo il nonce e riproviamo
            nonce += 1
            
            # (Opzionale) Feedback visivo ogni 10 tentativi
            if nonce % 10 == 0:
                 print(f"\rTentativo {nonce}... (Ultimo hash: {hashed_value[:5]}...)", end="")
