import csv
import os
import cloudscraper
import re

def podatki_o_GDP_po_drzavah():
    url = 'https://www.worldometers.info/gdp/gdp-by-country/'
    # Uporabimo cloudscraper, ker stran uporablja Cloudflare zaščito.
    scraper = cloudscraper.create_scraper(
        delay=2,  # Dodaten časovni zamik med zahtevami.                                  
        browser={
            'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                      'AppleWebKit/537.36 (KHTML, like Gecko)'
                      'Chrome/91.0.4472.124 Safari/537.36'
    }
    )
    prevzem = scraper.get(url)
    page_content = prevzem.text

    abs_path = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(abs_path, "..", "podatki")
    os.makedirs(folder_path, exist_ok=True)

    html_path = os.path.join(folder_path, "GDP_po_drzavah.html")
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(page_content)

    # Sedaj moramo iz kode izlusciti le tabelo na tej spletni strani.
    # To bomo naredili z regularnimi izrazi.   
    vzorec_tabele = r'<table class=([\s\S]*?)</table>'
    match_tabele = re.search(vzorec_tabele, page_content, re.DOTALL)

    if not match_tabele:
        raise ValueError("Tabele ni bilo mogoče najti")
    
    tabela_content = match_tabele.group(1)

    # Sestavimo novi vzorec, ki bo zajel iz vsake vrstice določene podatke.
    seznam_slovarjev = []
    vrstice = re.findall(r'<tr id=(.*?)</tr>', tabela_content, flags=re.DOTALL)
    for vrstica in vrstice:
        celice = re.findall(r'<td.*?>(.*?)</td>', vrstica, flags=re.DOTALL)
        # Definiramo funkcijo za čiščenje podatkov, ki oznake HTML zamenja s praznimi nizi.
        def ocisti_podatek(podatek):
            return re.sub(r'<.*?>', '', podatek).strip()
        
        # Država se nahaja v drugi celici, GDP rast v peti,
        # populacija v šesti, GDP na prebivalca v sedmi, delež svetovnega GDP pa v osmi.
        drzava = ocisti_podatek(celice[1])
        GDP_rast = ocisti_podatek(celice[4])
        populacija = ocisti_podatek(celice[5])
        GDP_na_prebivalca = ocisti_podatek(celice[6])
        delez_svetovnega_GDP = ocisti_podatek(celice[7])

        seznam_slovarjev.append({
                'Država': drzava,
                # Program ne zazna predznaka minus pred odstotkom, zato to ročno dodamo.
                'GDP rast (v odstotkih)':(
                    GDP_rast.replace('%', '') if 'â' not in GDP_rast 
                    else '-' + GDP_rast.replace('â', '').replace('%', '')
                ),
                'Populacija': populacija.replace(',', ''),
                'GDP na prebivalca (v dolarjih)': GDP_na_prebivalca.replace('$', '').replace(',', ''),
                'Delež svetovnega GDP (v odstotkih)': delez_svetovnega_GDP.replace('%', '')
            })
        
    # Funkcija nazadnje podatke iz seznama slovarjev pretvori v csv datoteko.
    csv_path = os.path.join(folder_path, "GDP_po_drzavah.csv")     

    if seznam_slovarjev:
        fieldnames = list(seznam_slovarjev[0].keys())
        with open(csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(seznam_slovarjev)
        return f"Podatki shranjeni v {csv_path}"
    else:
        return "Ni podatkov za shranjevanje"        
        

    