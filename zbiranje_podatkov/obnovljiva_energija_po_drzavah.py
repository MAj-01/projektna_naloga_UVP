import csv
import os
import requests
import re

def podatki_o_obnovljivi_energiji_po_drzavah():
    url = 'https://en.wikipedia.org/wiki/List_of_countries_by_renewable_electricity_production'
    prevzem = requests.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "obnovljiva_energija_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le prvo tabelo na tej spletni strani. To bomo naredili z regularnimi izrazi.   
 
    vzorec = r'<table([\s\S]*?)</table>'
    zozani_html_path = os.path.join(folder_path, "nastarejsi_prebivalci_po_drzavah_zozani_obseg.html")
    match = re.search(vzorec, page_content, re.DOTALL | re.IGNORECASE)

    if not match:
        raise ValueError("Vzorca ni bilo mogoče najti")
    
    novi_page_content = match.group(1)


    vzorec_tabele = r'<table class="wikitable sortable">([\s\S]*?)</table>'
    match_tabele = re.search(vzorec_tabele, novi_page_content, re.DOTALL)

    if not match_tabele:
        raise ValueError("Tabele ni bilo mogoče najti")
    
    tabela_content = match_tabele.group(1)

    tabela_path = os.path.join(folder_path, "nastarejsi_prebivalci_po_drzavah_tabela.html")
    with open(tabela_path, 'w', encoding='utf-8') as f:
        f.write(tabela_content)

    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.

    seznam_slovarjev = []
    vrstice = re.findall(r'<tr.*?</tr>', tabela_content, flags=re.DOTALL)[1:]
    
    for vrstica in vrstice:
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        drzava = re.search(r'">([\s\S]*?)</a></td>', vrstica) 
        st_znack = re.search(r'<td>([\s\S]*?)</td>', vrstica)
        procent_pridobljene_obnovljive_energije = st_znack[1]

        seznam_slovarjev.append({
                'Država': drzava,
                'Procent pridobljene obnovljive energije': procent_pridobljene_obnovljive_energije
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
    