import csv
import glob
import os

abs_path = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(abs_path, "..", "podatki")
csv_path = os.path.join(folder_path, "zdruzeni_podatki.csv")  
pot_do_datotek = glob.glob('podatki/*.csv')  

with open(csv_path, 'w', newline='', encoding='utf-8') as izhod:
    writer = csv.writer(izhod)
    for datoteka in pot_do_datotek:
        if datoteka == 'najstarejsi_prebivalci_po_drzavah.csv':
            with open(datoteka, 'r', newline='', encoding='utf-8') as vhod:
                reader = csv.reader(vhod)
                header = next(reader)
                writer.writerow(header)
                for vrstica in reader:
                    writer.writerow(vrstica)
        if datoteka not in 'pricakovana_zivljenska_doba_po drzavah.csv':
            with open(datoteka, 'r', newline='', encoding='utf-8') as vhod:

                reader = csv.reader(vhod)
                if i == 0:
                    # Zapiši glavo samo prvič
                    header = next(reader)
                    writer.writerow(header)
                else:
                    # Preskoči glavo v nadaljnjih datotekah
                    next(reader)
                for vrstica in reader:
                    writer.writerow(vrstica)