import csv
import os
import requests
import re

def podatki_o_obnovljivi_energiji_po_drzavah():
    url = 'https://en.wikipedia.org/wiki/List_of_countries_by_renewable_electricity_production'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        'AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/91.0.4472.124 Safari/537.36'
    }
    prevzem = requests.get(url, headers=headers, timeout=10)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "obnovljiva_energija_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le prvo tabelo na tej spletni strani.
    # To bomo naredili z regularnimi izrazi.   
    vzorec = r'<table([\s\S]*?)</table>'
    match = re.findall(vzorec, page_content, re.DOTALL | re.IGNORECASE)

    if not match:
        raise ValueError("Vzorca ni bilo mogoče najti")
    
    # Izberemo pravo tabelo.
    tabela_content = match[2]
    tabela_path = os.path.join(folder_path, "nastarejsi_prebivalci_po_drzavah_tabela.html")
    with open(tabela_path, 'w', encoding='utf-8') as f:
        f.write(tabela_content)

    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.
    seznam_slovarjev = []
    vrstice = re.findall(r'<tr.*?</tr>', tabela_content, flags=re.DOTALL)[1:]
    
    # Ustvarimo funkcijo za čiščenje podatkov, ki oznake HTML zamenja s praznimi nizi.
    def ocisti_podatek(podatek):
        return re.sub(r'<.*?>', '', podatek).strip()

    for vrstica in vrstice[1:]:
        celice = re.findall(r'<td.*?>(.*?)</td>', vrstica, flags=re.DOTALL)
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        drzava = ocisti_podatek(celice[0])
        drzava = re.sub(r'&#160;', '', drzava)
        procent_pridobljene_obnovljive_energije = ocisti_podatek(celice[1])

        seznam_slovarjev.append({
                'Država': drzava,
                'Odstotek pridobljene obnovljive energije': procent_pridobljene_obnovljive_energije
            })

    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.
    csv_path = os.path.join(folder_path, "obnovljiva_energija_po_drzavah.csv")     

    if seznam_slovarjev:
        fieldnames = list(seznam_slovarjev[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(seznam_slovarjev)
        return f"Podatki shranjeni v {csv_path}"
    else:
        return "Ni podatkov za shranjevanje"        
        
if __name__ == '__main__':
    podatki_o_obnovljivi_energiji_po_drzavah()
    