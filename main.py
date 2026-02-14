import os
import time
import hmac
import hashlib
import threading


class EntropyEngine:
    """
    CSPRNG basato su HMAC-DRBG (NIST style)
    - Seed iniziale da OS
    - Reseed periodico
    - Forward secrecy
    - Thread-safe
    """

    def __init__(self, reseed_interval=60):
        self.lock = threading.Lock()
        self.reseed_interval = reseed_interval
        self.last_reseed = time.time()

        # Stato DRBG
        self.K = b"\x00" * 32
        self.V = b"\x01" * 32

        seed_material = os.urandom(64)
        self._update(seed_material)

    # -------------------------------------------------
    # INTERNAL UPDATE (HMAC-DRBG core)
    # -------------------------------------------------

    def _hmac(self, key, data):
        return hmac.new(key, data, hashlib.sha256).digest()

    def _update(self, provided_data=b""):
        self.K = self._hmac(self.K, self.V + b"\x00" + provided_data)
        self.V = self._hmac(self.K, self.V)

        if provided_data:
            self.K = self._hmac(self.K, self.V + b"\x01" + provided_data)
            self.V = self._hmac(self.K, self.V)

    # -------------------------------------------------
    # RESEED
    # -------------------------------------------------

    def reseed(self):
        with self.lock:
            seed_material = os.urandom(64)
            self._update(seed_material)
            self.last_reseed = time.time()

    # -------------------------------------------------
    # RANDOM OUTPUT
    # -------------------------------------------------

    def random_bytes(self, n=32):
        with self.lock:

            # Reseed automatico
            if time.time() - self.last_reseed > self.reseed_interval:
                self.reseed()

            output = b""

            while len(output) < n:
                self.V = self._hmac(self.K, self.V)
                output += self.V

            self._update()  # forward secrecy

            return output[:n]

    def random_hex(self, n=32):
        return self.random_bytes(n).hex()


if __name__ == "__main__":
    engine = EntropyEngine()

    print("EntropyEngine")

    for _ in range(5):
        print(engine.random_hex(32))
        time.sleep(1)