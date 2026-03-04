# NetNoise

**Decentralized Public Randomness Beacon with Cryptographic Chain-Linking**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Status: Research](https://img.shields.io/badge/status-research-orange.svg)]()

---

## Overview

**NetNoise** is a novel blockchain-based system for generating **verifiable public randomness** without trusted parties. Unlike existing solutions (NIST Beacon, Chainlink VRF, Drand), NetNoise combines:

- ✅ **Physical entropy** from OS sources
- ✅ **Memory-hard Proof-of-Work** (Argon2id) for ASIC resistance
- ✅ **Cryptographic chain-linking via salt** (innovative contribution)
- ✅ **Distributed consensus** without centralized trust
- ✅ **Public verifiability** with deterministic aggregation

### Key Innovation

NetNoise uses the **hash of the previous block as the salt parameter of Argon2id**, creating a mathematical dependency between consecutive blocks that is stronger than traditional Bitcoin-style chain-linking.
```python
# NetNoise:
block_N.salt = previous_hash[0:16]  # ← Salt derived from previous block
block_N.hash = Argon2id(seed || nonce, salt=block_N.salt)
```

This ensures that **altering any block requires re-mining all subsequent blocks**, with computational cost growing linearly with chain depth.

---


## Features

### Core Capabilities

- **Trustless Random Generation**: No trusted parties, committees, or setup ceremonies
- **Chain-Linking via Salt**: Cryptographic binding stronger than Bitcoin
- **ASIC Resistance**: Memory-hard Argon2id prevents mining centralization
- **Public Verifiability**: Anyone can verify randomness generation
- **Aggregate Randomness**: Combine multiple blocks for increased security
- **Physical Entropy**: Fresh entropy from OS in every block

### Technical Features

- **HMAC-DRBG**: NIST SP 800-90A compliant deterministic random bit generator
- **Argon2id PoW**: Time-memory trade-off resistant proof-of-work
- **Dynamic Difficulty**: PID-based difficulty adjustment for stable block times
- **Window-Based Aggregation**: Configurable multi-block randomness aggregation
- **Complete Verification**: Full block and randomness verification tools

---

## How It Works

NetNoise generates randomness in **three phases**:
```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: Physical Entropy Collection                   │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  seed ← os.urandom(64)    # 512 bits from OS entropy   │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: Proof-of-Work Mining (Chain-Linked)           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  salt ← previous_hash[0:16]                             │
│                                                         │
│  Find nonce such that:                                  │
│  hash = Argon2id(seed || nonce, salt) < target         │
│                                                         │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 3: Cryptographic Expansion                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  entropy = seed || nonce || hash                        │
│  final_random = HMAC-DRBG(entropy, 32 bytes)           │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Chain-Linking Mechanism

Each block's hash becomes the salt for the next block:
```
Block N-1:  hash = abc123...
              ↓ (used as salt)
Block N:    salt = abc123...[0:16]
            hash = Argon2(seed || nonce, salt=abc123...)
              ↓ (used as salt)
Block N+1:  salt = Argon2_output[0:16]
            ...
```

**Consequence**: Modifying Block N-1 invalidates all blocks N, N+1, N+2, ... requiring complete re-mining.

---

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Install Dependencies
```bash
# Clone the repository
git clone https://github.com/yourusername/netnoise.git
cd netnoise

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### Requirements
```
argon2-cffi>=21.3.0
```

---

## Architecture

### System Components
```
┌─────────────────────────────────────────────────────────┐
│                    NetNoise System                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │   Entropy    │  │    Mining    │  │  Aggregation │ │
│  │    Engine    │→ │    Engine    │→ │    Engine    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         ↓                  ↓                  ↓         │
│  ┌──────────────────────────────────────────────────┐  │
│  │            Blockchain Storage Layer              │  │
│  │         (Blocks with final_random)               │  │
│  └──────────────────────────────────────────────────┘  │
│         ↓                                               │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Verification & Query API                │  │
│  │    (Public interfaces for verification)          │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Block Structure
```python
Block {
    index: int,              # Block height
    timestamp: int,          # Unix timestamp
    seed: str,               # Initial entropy (hex)
    nonce: int,              # Winning nonce from PoW
    previous_hash: str,      # Hash of previous block (hex)
    block_hash: str,         # Argon2 hash of this block (hex)
    final_random: str,       # Final randomness (hex, 32 bytes)
    difficulty: int,         # Mining difficulty
    mining_time: float       # Time taken to mine (seconds)
}
```

---

### Abstract

> We present NetNoise, a decentralized system for generating verifiable public randomness without trusted parties. The main contribution is the use of the previous block's hash as the salt parameter of Argon2id, creating explicit mathematical dependencies between consecutive blocks. We prove formal security properties (unpredictability, grinding resistance, computational immutability) and demonstrate practical performance on a 50-node testnet.

**[📑 Read Full Paper](./docs/paper.pdf)** *(coming soon)*

---

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
```
MIT License

Copyright (c) 2026 Giorgio Martucci

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

```
