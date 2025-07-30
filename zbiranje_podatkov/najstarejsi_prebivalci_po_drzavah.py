import csv
import os
import requests
import re

def podatki_o_najstarejsih_prebivalcih_po_drzavah():
    url = 'https://en.wikipedia.org/wiki/List_of_the_oldest_people_by_country'
    prevzem = requests.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "nastarejsi_prebivalci_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le prvo tabelo na tej spletni strani. To bomo naredili z regularnimi izrazi.   
 
    vzorec = r'<h2 id="Oldest_ever">Oldest ever</h2>([\s\S]*?)<h3 id="Territorial_and_overseas_regions_recordholders">Territorial and overseas regions recordholders</h3>'
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
    vrstice = re.findall(r'<tr>.*?</tr>', tabela_content, flags=re.DOTALL)[1:]
    prejsnja_drzava = None
    for vrstica in vrstice:
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        drzava = re.search(r'</span><a href="/wiki/([\s\S]*?)" title="([\s\S]*?)">([\s\S]*?)</a></td>', vrstica) 
        if "Flag_of_" in vrstica and re.findall(r'</span><a href="/wiki/([\s\S]*?)" title="([\s\S]*?)">([\s\S]*?)</a></td>', vrstica) == []:
            drzava = re.search(r'<a href="/wiki/([\s\S]*?)" title="([\s\S]*?)"><img alt="([\s\S]*?)"', vrstica)
        if drzava:
            drzava = drzava.group(2)  
        else:
            drzava = prejsnja_drzava
        prejsnja_drzava = drzava 

        # Spol osebe je v vrsti zapisan v razdelku center, ki je v html kodi zapisan kot <div class="center">
        spol = re.search(r'<div class="center">(.*?)</div></td>', vrstica)

        # Datum rojstva in datum smrti osebe je v html kodi strani zapisan zaporedoma pod istimi oznakami, 
        # zato uporabimo re.findall, da poiscemo oba zadetka
        st_znacka = re.findall(r'<td([\s\S]*?)</td>', vrstica)
        datum_smrti = None
        datum_rojstva = None
        if len(st_znacka) >= 5:
            if "nowrap" in vrstica:  # Preverimo v izvorni vrstici, ne v vsebini celice
                match_rojstvo = re.search(r'class="nowrap">(.*?)<', st_znacka[-3])
                if match_rojstvo:
                    datum_rojstva = match_rojstvo.group(1)
            
            # Datum smrti - zadnji stolpec
            if "Living" in st_znacka[-2]:
                datum_smrti = "Living"
            elif "reference" in st_znacka[-2]:
                match_smrt = re.search(r'>(.*?)<sup', st_znacka[-2])
                if match_smrt:
                    datum_smrti = match_smrt.group(1)
            else:
                # Če ni posebnih oznak, uporabimo celotno vsebino celice
                datum_smrti = st_znacka[-2]
        # if len(st_znacka) >= 5:
        #     if "nowrap" in st_znacka[-3]:
        #         datum_rojstva = re.search(r'<td class="nowrap">(.*?)<', st_znacka[-3])
        #         # datum_rojstva = datum_rojstva.group(1)
        #     elif "nowrap" in st_znacka[-2]:
        #         datum_smrti = re.search(r'<td class="nowrap">(.*?)<', st_znacka[-2])
        #         # datum_smrti = datum_smrti.group(1)
        #     elif "reference" in st_znacka[-2]:
        #         datum_smrti = re.search(r'<td>(.*?)<sup id="cite_ref-([\s\S]*?)" class="reference">', st_znacka[-2])
        #         # datum_smrti = datum_smrti.group(1)
        #     else:
        #         datum_smrti = re.search(r'<td>(.*?)</td>', st_znacka[-2])
        #         # datum_smrti = datum_smrti.group(1)
    
        # Starost
        if "<td>Living</td>" in vrstica:
            leta = re.search(r'<td>(.*?)&nbsp;years', vrstica)
            dnevi = re.search(r'years, (.*?)&nbsp;days', vrstica)
        else:    
            leta = re.search(r'</span>(.*?)&nbsp;years', vrstica)
            dnevi = re.search(r'years, (.*?)&nbsp;days', vrstica)
        
        seznam_slovarjev.append({
                'Država': drzava,
                'Spol': spol.group(1) if spol else None,
                'Datum rojstva': datum_rojstva,
                'Datum smrti': datum_smrti,
                'Starost (leta)': leta.group(1),
                'Starost (dnevi)': dnevi.group(1)
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
    