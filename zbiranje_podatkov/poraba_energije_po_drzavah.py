import csv
import os
import requests
import re

def podatki_o_porabi_energije_po_drzavah():
    url = 'https://www.worldometers.info/energy/'
    prevzem = requests.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "poraba_energije_po_drzavah.html")
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
    vrstice = re.findall(r'<tr>(.*?)</tr>', tabela_content, flags=re.DOTALL)
    
    for vrstica in vrstice:
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        drzava = re.search(r'data-country="([\s\S]*?)">([\s\S]*?)</a>', vrstica) 

        # Dva podatka stas v enaki obliki značke, zato uporabimo nasledjo funkcijo.
        dva_podatka = re.findall(r'data-order=(.*?)</td>', vrstica)
        porabljena_energija = dva_podatka[0] 
        porabljena_energija_na_prebivalca = dva_podatka[1]

        # Pričakovana življenska doba - povprečje spolov.
        procent_porabe_enegije_na_drzavo = re.search(r'<td class="px-2 border-e border-zinc-200 text-end py-1.5 border-b font-bold"> (.*?) </td>', vrstica)

        seznam_slovarjev.append({
                'Država': drzava.group(2),
                'Porabljena energija na državo (letno)': porabljena_energija.group(2),
                'Procent porabe energije (svetovno)': procent_porabe_enegije_na_drzavo.group(1),
                'Prorabljena energija na prebivalca (letno)': porabljena_energija_na_prebivalca.group(2)
            })




    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.

    csv_path = os.path.join(folder_path, "poraba_energije_po_drzavah.csv")     

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
    podatki_o_porabi_energije_po_drzavah()