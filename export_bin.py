import json
import binascii

def export_to_binary(json_filename, bin_filename):
    print(f"Lettura di {json_filename}...")
    try:
        with open(json_filename, 'r') as f:
            data = json.load(f)
            
        print(f"Trovati {len(data['chain'])} blocchi.")
        
        with open(bin_filename, 'wb') as f_out:
            for block in data['chain']:
                # Prendiamo l'Entropia Grezza (o l'hash se preferisci)
                # L'entropia è hex string, la convertiamo in byte puri
                hex_data = block['entropy']
                byte_data = binascii.unhexlify(hex_data)
                f_out.write(byte_data)
                
        print(f"✅ Fatto! Creato '{bin_filename}' pronto per Dieharder.")
        
    except FileNotFoundError:
        print("❌ Errore: blockchain.json non trovato.")
    except Exception as e:
        print(f"❌ Errore: {e}")

if __name__ == "__main__":
    export_to_binary("blockchain.json", "random.bin")