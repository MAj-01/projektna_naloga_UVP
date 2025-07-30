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


    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.

    seznam_slovarjev = []
    vrstice = re.findall(r'<tr id=(.*?)</tr>', tabela_content, flags=re.DOTALL)
    for vrstica in vrstice:
        # Drzavo iz vrstice lahko pridobimo le iz linka slike, ki predstavlja zastavo drzave.
        drzava = re.search(r'data-country="([\s\S]*?)">([\s\S]*?)</a>', vrstica) 

        # Pričakovana življenska doba - povprečje spolov.
        pricakovana_zivljenska_doba = re.search(r'<td dir="ltr" class="px-2 border-e border-zinc-200 text-end py-1.5 border-b font-bold" data-order="([\s\S]*?)"> ([\s\S]*?) </td>', vrstica)

        # Pričakovana življenjska doba za ženske se pridobi iz istega vzorca.
        pricakovana_zivljenska_doba_zenske = re.search(r'<td dir="ltr" class="px-2 border-e border-zinc-200 text-end py-1.5 border-b bg-fuchsia-100" data-order="([\s\S]*?)"> ([\s\S]*?) </td>', vrstica)

        # Pričakovana življenjska doba za moške se pridobi iz malo drugačnega vzorca, saj je razlika v barvi podatka.
        pricakovana_zivljenska_doba_moski = re.search(r'<td dir="ltr" class="px-2 border-e border-zinc-200 text-end py-1.5 border-b bg-cyan-100" data-order="([\s\S]*?)"> ([\s\S]*?) </td>', vrstica)

        seznam_slovarjev.append({
                'Država': drzava.group(2),
                'Pričakovana življenska doba': pricakovana_zivljenska_doba.group(2),
                'Pričakovana življenska doba (ženske)': pricakovana_zivljenska_doba_zenske.group(2),
                'Pričakovana življenska doba (moški)': pricakovana_zivljenska_doba_moski.group(2)
            })




    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.

    csv_path = os.path.join(folder_path, "pricakovana_zivljenska_doba_po_drzavah.csv")     

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
    podatki_o_pricakovani_zivljenski_dobi_po_drzavah()
    