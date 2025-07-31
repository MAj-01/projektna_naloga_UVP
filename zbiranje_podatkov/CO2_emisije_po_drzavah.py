import csv
import os
import requests
import re

def podatki_o_CO2_po_drzavah():
    url = 'https://www.worldometers.info/co2-emissions/co2-emissions-by-country/'
    prevzem = requests.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "CO2_emisije_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le tabelo na tej spletni strani. To bomo naredili z regularnimi izrazi.   

    vzorec_tabele = r'<table class([\s\S]*?)</table>'
    match_tabele = re.search(vzorec_tabele, page_content, re.DOTALL)

    if not match_tabele:
        raise ValueError("Tabele ni bilo mogoče najti")
    
    tabela_content = match_tabele.group(1)


    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.

    seznam_slovarjev = []
    vrstice = re.findall(r'<tr id=(.*?)</tr>', tabela_content, flags=re.DOTALL)
    for vrstica in vrstice:
        drzava = re.search(r'data-country="([\s\S]*?)">([\s\S]*?)</a>', vrstica) 

        # Ker so naslednje štiri vrednosti v isti znacki, jih lahko pridobimo z enim vzorcem.
        match_znacka = re.findall(r'<td dir="ltr" class="px-2 border-e border-zinc-200 text-end py-1.5 border-b" data-order="([\s\S]*?)"> ([\s\S]*?) </td>', vrstica)
        CO2_emisije = match_znacka[0]
        letna_rast = match_znacka[1]
        CO2_na_prebivalca = match_znacka[3]
        delez_svetovnega_CO2 = match_znacka[4]

        seznam_slovarjev.append({
                'Država': drzava.group(2),
                'CO2 emisije': CO2_emisije[1],
                'Letna rast (v primerjavi s preteklim letom)': letna_rast[1],
                'CO2 emisije na prebivalca': CO2_na_prebivalca[1],
                'Delež svetovnega CO2': delez_svetovnega_CO2[1]
            })




    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.

    csv_path = os.path.join(folder_path, "CO2_emisije_po_drzavah.csv")     

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
    podatki_o_CO2_po_drzavah()
    