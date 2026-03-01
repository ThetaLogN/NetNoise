import os
import hmac
import hashlib
from argon2.low_level import hash_secret_raw, Type

class HMAC_DRBG:
    def __init__(self, seed: bytes):
        self.K = b"\x00" * 32
        self.V = b"\x01" * 32
        self._update(seed)

    def _hmac(self, key: bytes, data: bytes) -> bytes:
        return hmac.new(key, data, hashlib.sha256).digest()

    def _update(self, provided_data: bytes = b""):
        self.K = self._hmac(self.K, self.V + b"\x00" + provided_data)
        self.V = self._hmac(self.K, self.V)
        if provided_data:
            self.K = self._hmac(self.K, self.V + b"\x01" + provided_data)
            self.V = self._hmac(self.K, self.V)

    def random_bytes(self, n=32) -> bytes:
        output = b""
        while len(output) < n:
            self.V = self._hmac(self.K, self.V)
            output += self.V
        self._update()
        return output[:n]


def generate_random_from_pow(previous_hash: str, difficulty: int = 2**248):
    """
    Genera random usando chain-linking.
    
    Args:
        previous_hash: Hash del blocco precedente (hex string)
                      Per genesis block: "0" * 64
        difficulty: Target di difficoltà
    
    Entropia da:
    1. os.urandom (seed iniziale)
    2. nonce vincente (trovato dal mining)
    3. hash Argon2 finale (risultato del PoW)
    
    - Salt di Argon2 = previous_hash
    - Ogni blocco legato al precedente
    """
    
    print("="*60)
    print("GENERAZIONE RANDOM CON CHAIN-LINKING")
    print("="*60)
    

    print("\n[1/3] Seed iniziale da OS...")
    seed = os.urandom(64)
    print(f"    Seed: {seed.hex()[:32]}...")
    

    print(f"\n[2/3] Mining PoW (difficoltà: {difficulty})...")
    print(f"    Previous hash: {previous_hash[:32]}...")
    
    #Salt = hash del blocco precedente
    salt = bytes.fromhex(previous_hash)[:16] 
    print(f"    Salt (da previous_hash): {salt.hex()}")
    
    nonce = 0
    winning_hash = None
    
    while True:
        # Combina seed + nonce
        nonce_bytes = nonce.to_bytes(8, "big")
        mining_input = seed + nonce_bytes
        
        # Argon2 PoW con salt = previous_hash
        hash_bytes = hash_secret_raw(
            secret=mining_input,
            salt=salt,  
            time_cost=3,
            memory_cost=65536, 
            parallelism=1,
            hash_len=32,
            type=Type.ID
        )
        
        # Verifica difficoltà
        hash_int = int.from_bytes(hash_bytes, "big")
        
        if hash_int < difficulty:
            winning_hash = hash_bytes
            print(f"    Blocco trovato!")
            print(f"    Nonce vincente: {nonce}")
            print(f"    Hash: {hash_bytes.hex()[:32]}...")
            break
        
        nonce += 1
        
        if nonce % 100 == 0:
            print(f"    Mining... {nonce} tentativi")
    

    print(f"\n[3/3] Generazione random finale...")
    
    # - seed originale
    # - nonce vincente
    # - hash Argon2 vincente
    combined_entropy = seed + nonce.to_bytes(8, "big") + winning_hash
    
    # Espandi con HMAC-DRBG
    drbg = HMAC_DRBG(combined_entropy)
    final_random = drbg.random_bytes(32)
    
    print(f"    Random finale: {final_random.hex()}")
    print(f"\n{'='*60}")
    print(f"    GENERAZIONE COMPLETATA")
    print(f"{'='*60}")
    
    return final_random, nonce, winning_hash


if __name__ == "__main__":

    
    difficulty = 2**250 
    blocks = []
    
   
    print("\n" + "=" * 30)
    print("BLOCCO 0 (GENESIS)")
    print("=" * 30)
    
    genesis_previous = "0" * 64  
    
    random_0, nonce_0, hash_0 = generate_random_from_pow(
        previous_hash=genesis_previous,
        difficulty=difficulty
    )
    
    blocks.append({
        'index': 0,
        'previous_hash': genesis_previous,
        'block_hash': hash_0.hex(),
        'random': random_0.hex(),
        'nonce': nonce_0
    })
    
   
    print("\n" + "=" * 30)
    print("BLOCCO 1")
    print("=" * 30)
    
    random_1, nonce_1, hash_1 = generate_random_from_pow(
        previous_hash=hash_0.hex(),  
        difficulty=difficulty
    )
    
    blocks.append({
        'index': 1,
        'previous_hash': hash_0.hex(),
        'block_hash': hash_1.hex(),
        'random': random_1.hex(),
        'nonce': nonce_1
    })
    
  
    print("\n" + "=" * 30)
    print("BLOCCO 2")
    print("=" * 30)
    
    random_2, nonce_2, hash_2 = generate_random_from_pow(
        previous_hash=hash_1.hex(), 
        difficulty=difficulty
    )
    
    blocks.append({
        'index': 2,
        'previous_hash': hash_1.hex(),
        'block_hash': hash_2.hex(),
        'random': random_2.hex(),
        'nonce': nonce_2
    })
    
   
    print("\n" + "="*60)
    print("BLOCKCHAIN COMPLETA")
    print("="*60)
    
    for block in blocks:
        print(f"\nBlocco #{block['index']}:")
        print(f"  Previous Hash: {block['previous_hash'][:32]}...")
        print(f"  Block Hash:    {block['block_hash'][:32]}...")
        print(f"  Random:        {block['random'][:32]}...")
        print(f"  Nonce:         {block['nonce']}")
    

    print("\n" + "="*60)
    print("VERIFICA CHAIN-LINKING")
    print("="*60)
    
    print("\n   Catena corretta:")
    print(f"  Blocco 0 hash: {blocks[0]['block_hash'][:16]}...")
    print(f"  Blocco 1 previous: {blocks[1]['previous_hash'][:16]}...")
    print(f"  Match: {blocks[0]['block_hash'] == blocks[1]['previous_hash']}")
    
    print(f"\n  Blocco 1 hash: {blocks[1]['block_hash'][:16]}...")
    print(f"  Blocco 2 previous: {blocks[2]['previous_hash'][:16]}...")
    print(f"  Match: {blocks[1]['block_hash'] == blocks[2]['previous_hash']}")
    
    print("\n   Conseguenza:")
    print("   Se modifichi Blocco 0, il suo hash cambia")
    print("   → Salt di Blocco 1 cambia")
    print("   → Hash Argon2 di Blocco 1 non è più valido")
    print("   → Devi rimine Blocco 1, 2, 3, ...")
    print("   → Immutabilità garantita!")