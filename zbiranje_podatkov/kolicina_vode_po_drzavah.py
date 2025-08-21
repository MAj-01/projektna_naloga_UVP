import csv
import os
import requests
import re

def podatki_o_kolicini_vode():
    url = 'https://www.worldometers.info/water/'
    prevzem = requests.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "kolicina_vode.html")
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
        drzava = re.search(r'data-country="([\s\S]*?)">([\s\S]*?)</a>', vrstica) 
        litri_vode_na_prebivalca = re.search(r'data-order="([\s\S]*?)"> ([\s\S]*?) <', vrstica) 

        seznam_slovarjev.append({
                'Država': drzava.group(1),
                'Porabljena količina vode na prebivalca (dnevno)': litri_vode_na_prebivalca.group(2)
            })




    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.

    csv_path = os.path.join(folder_path, "kolicina_vode.csv")     

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
    podatki_o_kolicini_vode()
    