import requests
import xml.etree.ElementTree as ET
import os

# Configurazione
EPG_URL = "http://epg-guide.com/dttsat.xml"
CHANNELS_FILE = "canali.txt"
OUTPUT_FILE = "02.epg"

def filter_epg():
    # 1. Leggi i canali dal file txt con pulizia caratteri speciali
    if not os.path.exists(CHANNELS_FILE):
        print(f"ERRORE: Il file {CHANNELS_FILE} non esiste!")
        return

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        # Pulizia: rimuove spazi, ritorni a capo (\r \n) e righe vuote
        target_channels = set(line.strip().replace('\r', '').replace('\n', '') for line in f if line.strip())

    print(f"--- CANALI CARICATI DA {CHANNELS_FILE} ---")
    for c in target_channels:
        print(f"ID da cercare: '{c}'")
    print(f"Totale canali da cercare: {len(target_channels)}")
    print("------------------------------------------")

    # 2. Scarica il file EPG
    print(f"Scaricamento EPG da {EPG_URL}...")
    try:
        response = requests.get(EPG_URL, timeout=60)
        response.raise_for_status()
        print("Download completato.")
    except Exception as e:
        print(f"Errore durante il download: {e}")
        return

    # 3. Parsa l'XML
    try:
        root = ET.fromstring(response.content)
    except Exception as e:
        print(f"Errore nel parsing XML: {e}")
        return

    # Crea il nuovo XML radice
    new_root = ET.Element("tv")
    for key, value in root.attrib.items():
        new_root.set(key, value)

    # 4. Filtra i tag <channel>
    found_channels = []
    for channel in root.findall("channel"):
        channel_id = channel.get("id")
        if channel_id in target_channels:
            new_root.append(channel)
            found_channels.append(channel_id)

    print(f"Canali <channel> trovati nell'XML: {len(found_channels)}")

    # 5. Filtra i tag <programme>
    # Usiamo un ciclo per aggiungere tutti i programmi che corrispondono ai canali trovati
    prog_count = 0
    for programme in root.findall("programme"):
        channel_id_prog = programme.get("channel")
        if channel_id_prog in target_channels:
            new_root.append(programme)
            prog_count += 1

    print(f"Programmi <programme> aggiunti: {prog_count}")

    # 6. Salva il file
    tree = ET.ElementTree(new_root)
    with open(OUTPUT_FILE, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    
    print(f"--- SUCCESS: File {OUTPUT_FILE} generato correttamente! ---")

if __name__ == "__main__":
    filter_epg()
