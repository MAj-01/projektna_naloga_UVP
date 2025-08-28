import csv
import os
import requests
import re

def podatki_o_najstarejsih_prebivalcih_po_drzavah():
    url = 'https://en.wikipedia.org/wiki/List_of_the_oldest_people_by_country'
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

    # Shranimo podatke v html datoteko.
    html_path = os.path.join(folder_path, "najstarejsi_prebivalci_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le tabelo na tej spletni strani.
    # To bomo naredili z regularnim izrazom.    
    vzorec_tabele = r'<table class([\s\S]*?)</table>'
    match_tabele = re.findall(vzorec_tabele, page_content, re.DOTALL)

    if not match_tabele:
        raise ValueError("Tabele ni bilo mogoče najti")
    
    tabela_content = match_tabele[0]
    
    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.
    seznam_slovarjev = []
    vrstice = re.findall(r'<tr.*?</tr>', tabela_content, flags=re.DOTALL)[1:]
    prejsnja_drzava = None
    for vrstica in vrstice:
        celice = re.findall(r'<td.*?>(.*?)</td>', vrstica, flags=re.DOTALL)

        # Definiramo funkcijo za čiščenje podatkov, ki oznake HTML zamenja s praznimi nizi.
        def ocisti_podatek(podatek):
            return re.sub(r'<.*?>', '', podatek).strip()
        
        # Državo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo države.
        # Podatek o državi pa ni v vsaki vrstici (podatki o najstarejših prebivalcih so
        # v podkategoriji držav, zato je podatek o državi le pri prvi osebi), zato moramo
        # izbrati prejšnjo državo v vrsticah, ki ne vsebujejo podatka o državi.
        if "Flag_of_" in celice[0]:
            drzava = ocisti_podatek(celice[0])
        else:   
            drzava = prejsnja_drzava
        prejsnja_drzava = drzava 

        # Spol osebe, datum rojstva in datum smrti so v vrstici zapisani vsak v svoji celici.
        # Vse tri lahko pridobimo na isti način
        spol = ocisti_podatek(celice[-4])
        datum_rojstva = ocisti_podatek(celice[-3])
        datum_smrti = ocisti_podatek(celice[-2])
        datum_smrti= re.sub(r'&#\d+;', '', datum_smrti)  # Odstranimo morebitne HTML oznake.
 
        # Določimo še starost osebe v letih in dnevih. Podatka najdemo v zadnji celici.       
        match_datum = re.search(r'</span>(.*?)&#160;years, (.*?)&#160;days', celice[-1])

        seznam_slovarjev.append({
                'Država': (
                    drzava if '&#160;' not in drzava
                    else drzava.replace('&#160;', '')
                ),
                'Spol': spol,
                'Datum rojstva': datum_rojstva,
                'Datum smrti': datum_smrti,
                'Starost (leta)': match_datum.group(1),
                'Starost (dnevi)': match_datum.group(2)
            })

    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.
    csv_path = os.path.join(folder_path, "najstarejsi_prebivalci_po_drzavah.csv")     

    if seznam_slovarjev:
        fieldnames = list(seznam_slovarjev[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(seznam_slovarjev)
        return f"Podatki shranjeni v {csv_path}"
    else:
        return "Ni podatkov za shranjevanje"        
        
