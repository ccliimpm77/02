import requests
import xml.etree.ElementTree as ET

# Configurazione
EPG_URL = "http://epg-guide.com/dttsat.xml"
TARGET_CHANNELS = ["la7cinema.it", "radioitaliatv.it"]
OUTPUT_FILE = "02.epg"

def filter_epg():
    print(f"Scaricamento EPG da {EPG_URL}...")
    try:
        response = requests.get(EPG_URL, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print(f"Errore durante il download: {e}")
        return

    # Parsa l'XML
    root = ET.fromstring(response.content)
    
    # Crea il nuovo elemento radice <tv>
    new_root = ET.Element("tv")
    for key, value in root.attrib.items():
        new_root.set(key, value)

    # Filtra i tag <channel>
    count_channels = 0
    for channel in root.findall("channel"):
        if channel.get("id") in TARGET_CHANNELS:
            new_root.append(channel)
            count_channels += 1

    # Filtra i tag <programme>
    count_progs = 0
    for programme in root.findall("programme"):
        if programme.get("channel") in TARGET_CHANNELS:
            new_root.append(programme)
            count_progs += 1

    print(f"Filtraggio completato: {count_channels} canali e {count_progs} programmi trovati.")

    # Salva il file
    tree = ET.ElementTree(new_root)
    with open(OUTPUT_FILE, "wb") as f:
        tree.write(f, encoding="utf-8", xml_declaration=True)
    
    print(f"File {OUTPUT_FILE} generato correttamente.")

if __name__ == "__main__":
    filter_epg()
