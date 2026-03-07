import requests
import xml.etree.ElementTree as ET
import os
import sys

# Configurazione
EPG_URL = "http://epg-guide.com/dttsat.xml"
CHANNELS_FILE = "canali.txt"
OUTPUT_FILE = "02.epg"

def filter_epg():
    # 1. Leggi i canali dal file txt
    if not os.path.exists(CHANNELS_FILE):
        print(f"ERRORE: Il file {CHANNELS_FILE} non è stato trovato nel repository!")
        sys.exit(1)

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        # Pulizia profonda: rimuove spazi, ritorni a capo e il carattere invisibile BOM
        target_channels = [line.strip().lstrip('\ufeff') for line in f if line.strip()]

    if not target_channels:
        print("ERRORE: Il file canali.txt sembra vuoto!")
        sys.exit(1)

    print(f"--- CANALI DA FILTRARE (letti da {CHANNELS_FILE}) ---")
    for c in target_channels:
        print(f"CERCO: '{c}'")
    print(f"Totale: {len(target_channels)} canali.")
    print("--------------------------------------------------")

    # 2. Scarica il file EPG originale
    print(f"Scaricamento EPG da {EPG_URL}...")
    try:
        r = requests.get(EPG_URL, timeout=60)
        r.raise_for_status()
        print("Download completato con successo.")
    except Exception as e:
        print(f"Errore durante il download: {e}")
        sys.exit(1)

    # 3. Parsa l'XML
    try:
        root = ET.fromstring(r.content)
    except Exception as e:
        print(f"Errore nel parsing XML: {e}")
        sys.exit(1)

    # Crea il nuovo XML radice <tv>
    new_root = ET.Element("tv")
    for key, value in root.attrib.items():
        new_root.set(key, value)

    # 4. Filtra i tag <channel>
    count_ch = 0
    for channel in root.findall("channel"):
        channel_id = channel.get("id")
        if channel_id in target_channels:
            new_root.append(channel)
            count_ch += 1

    # 5. Filtra i tag <programme>
    count_pg = 0
    for programme in root.findall("programme"):
        prog_channel = programme.get("channel")
        if prog_channel in target_channels:
            new_root.append(programme)
            count_pg += 1

    print(f"RISULTATO: Trovati {count_ch} canali e {count_pg} programmi.")

    # 6. Salva il file
    tree = ET.ElementTree(new_root)
    with open(OUTPUT_FILE, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    
    print(f"File {OUTPUT_FILE} salvato correttamente nel repository.")

if __name__ == "__main__":
    filter_epg()
