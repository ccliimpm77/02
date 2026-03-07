import requests
import xml.etree.ElementTree as ET
import os

# Configurazione
EPG_URL = "http://epg-guide.com/dttsat.xml"
CHANNELS_FILE = "canali.txt"  # Il file che contiene la tua lista
OUTPUT_FILE = "02.epg"

def filter_epg():
    # 1. Leggi i canali dal file txt
    if not os.path.exists(CHANNELS_FILE):
        print(f"Errore: Il file {CHANNELS_FILE} non esiste nel repository!")
        return

    with open(CHANNELS_FILE, "r", encoding="utf-8") as f:
        # Legge le righe, rimuove spazi bianchi e righe vuote
        target_channels = [line.strip() for line in f if line.strip()]

    if not target_channels:
        print("Il file canali.txt è vuoto.")
        return

    print(f"Canali caricati da {CHANNELS_FILE}: {len(target_channels)}")

    # 2. Scarica il file EPG originale
    print(f"Scaricamento EPG da {EPG_URL}...")
    try:
        response = requests.get(EPG_URL, timeout=60)
        response.raise_for_status()
    except Exception as e:
        print(f"Errore durante il download: {e}")
        return

    # 3. Parsa l'XML
    root = ET.fromstring(response.content)
    new_root = ET.Element("tv")
    
    # Copia gli attributi del tag radice <tv>
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

    print(f"Filtraggio completato: {count_channels}/{len(target_channels)} canali trovati, {count_progs} programmi aggiunti.")

    # 6. Salva il file finale
    tree = ET.ElementTree(new_root)
    with open(OUTPUT_FILE, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    
    print(f"File {OUTPUT_FILE} creato con successo.")

if __name__ == "__main__":
    filter_epg()
