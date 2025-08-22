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
    
    for vrstica in vrstice[1:]:
        celice = re.findall(r'<td.*?>(.*?)</td>', vrstica, flags=re.DOTALL)
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        def ocisti_podatek(podatek):
            return re.sub(r'<.*?>', '', podatek).strip()
        
        # Država (običajno druga celica)
        drzava = ocisti_podatek(celice[1])
    
        # Poraba energije (tretja celica)
        poraba_energije = ocisti_podatek(celice[2])
        
        # Odstotek porabe energije (četrta celica)
        odstotek_porabe = ocisti_podatek(celice[3])
        
        # Poraba energije na prebivalca (peta celica)
        poraba_na_prebivalca = ocisti_podatek(celice[4])

    
        # drzava_match = re.search(r'data-country="(.*?)">(.*?)<', st_znack[1].group(2)) 
        # drzava = drzava_match.group(2) if drzava_match else "Neznana država"
# 
        # porabljena_energija = st_znack[2].group(2)
        # procent_porabe_enegije_na_drzavo = st_znack[3].group(2)
        # porabljena_energija_na_prebivalca = st_znack[4].group(2)

        seznam_slovarjev.append({
                'Država': drzava,
                'Porabljena energija na državo (letno)': poraba_energije,
                'Procent porabe energije (svetovno)': odstotek_porabe,
                'Porabljena energija na prebivalca (letno)': poraba_na_prebivalca
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