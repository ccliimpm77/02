import requests
import xml.etree.ElementTree as ET
import os

# Configurazione
EPG_URL = "http://epg-guide.com/dttsat.xml"
CHANNELS_FILE = "canali.txt"  # Assicurati che questo file esista nel repo
OUTPUT_FILE = "02.epg"

def filter_epg():
    # 1. Carica i canali da tenere dal file txt
    if not os.path.exists(CHANNELS_FILE):
        print(f"Errore: {CHANNELS_FILE} non trovato!")
        return

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        # Crea una lista di ID canali puliti (senza spazi o invii)
        target_channels = set(line.strip() for line in f if line.strip())

    print(f"Canali da filtrare: {len(target_channels)}")

    # 2. Scarica il file EPG
    print(f"Scaricamento EPG da {EPG_URL}...")
    response = requests.get(EPG_URL)
    if response.status_code != 200:
        print("Errore nel download dell'EPG")
        return

    # 3. Parsa l'XML
    root = ET.fromstring(response.content)
    new_root = ET.Element("tv")
    
    # Copia gli attributi del root originale (generator, source, ecc.)
    for key, value in root.attrib.items():
        new_root.set(key, value)

    # 4. Filtra i tag <channel>
    count_channels = 0
    for channel in root.findall("channel"):
        channel_id = channel.get("id")
        if channel_id in target_channels:
            new_root.append(channel)
            count_channels += 1

    # 5. Filtra i tag <programme>
    count_progs = 0
    for programme in root.findall("programme"):
        prog_channel = programme.get("channel")
        if prog_channel in target_channels:
            new_root.append(programme)
            count_progs += 1

    print(f"Salvati {count_channels} canali e {count_progs} programmi.")

    # 6. Salva il file finale
    tree = ET.ElementTree(new_root)
    tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
    print(f"File {OUTPUT_FILE} creato con successo.")

if __name__ == "__main__":
    filter_epg()
