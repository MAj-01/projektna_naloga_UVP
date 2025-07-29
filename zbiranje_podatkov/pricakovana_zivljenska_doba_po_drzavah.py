import csv
import os
import requests
import re

def podatki_o_pricakovani_zivljenski_dobi_po_drzavah():
    url = 'https://www.worldometers.info/demographics/life-expectancy/'
    prevzem = requests.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "pricakovana_zivljenska_doba_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le tabelo na tej spletni strani. To bomo naredili z regularnimi izrazi.   

    vzorec_tabele = r'<table class([\s\S]*?)</table>'
    match_tabele = re.search(vzorec_tabele, page_content, re.DOTALL)

    if not match_tabele:
        raise ValueError("Tabele ni bilo mogoče najti")
    
    tabela_content = match_tabele.group(1)

    tabela_path = os.path.join(folder_path, "pricakovana_zivljenska_doba_po_drzavah_tabela.html")
    with open(tabela_path, 'w', encoding='utf-8') as f:
        f.write(tabela_content)

    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.

    seznam_slovarjev = []
    vrstice = re.findall(r'<tr id=(.*?)</tr>', tabela_content, flags=re.DOTALL)[1:]
    for vrstica in vrstice:
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        drzava = re.search(r'data-country="(\w)">(\w)</a>', vrstica) 

        # Pričakovana življenska doba - povprečje spolov.
        pricakovana_zivljenska_doba = re.search(r'<td class="r">(\d+)</td>', vrstica)

        # Pričakovana življenjska doba za ženske se pridobi iz istega vzorca.
        pricakovana_zivljenska_doba_zenske = re.search(r'<td class="r">(\d+)</td>', vrstica, re.DOTALL)

        # Pričakovana življenjska doba za moške se pridobi iz malo drugačnega vzorca, saj je razlika v barvi podatka.
        pricakovana_zivljenska_doba_moski = re.search(r'<td class="r">(\d+)</td>', vrstica, re.DOTALL)

        seznam_slovarjev.append({
                'drzava': drzava.group(2),
                'spol': spol.group(1) if spol else None,
                'datum rojstva': datum_rojstva,
                'datum smrti': datum_smrti,
                'starost (leta)': leta.group(1),
                'starost (dnevi)': dnevi.group(1)
            })

    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.

    csv_path = os.path.join(folder_path, "nastarejsi_prebivalci_po_drzavah.csv")     

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
    podatki_o_najstarejsih_prebivalcih_po_drzavah()
    