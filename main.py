from zbiranje_podatkov.CO2_emisije_po_drzavah import podatki_o_CO2_po_drzavah
from zbiranje_podatkov.GDP_po_drzavah import podatki_o_GDP_po_drzavah
from zbiranje_podatkov.kolicina_vode_po_drzavah import podatki_o_kolicini_vode_po_drzavah
from zbiranje_podatkov.najstarejsi_prebivalci_po_drzavah import podatki_o_najstarejsih_prebivalcih_po_drzavah
from zbiranje_podatkov.obnovljiva_energija_po_drzavah import podatki_o_obnovljivi_energiji_po_drzavah
from zbiranje_podatkov.podhranjenost_prebivalstva_po_drzavah import podatki_o_podhranjenosti_prebivalstva_po_drzavah
from zbiranje_podatkov.poraba_energije_po_drzavah import podatki_o_porabi_energije_po_drzavah
from zbiranje_podatkov.pricakovana_zivljenjska_doba_po_drzavah import podatki_o_pricakovani_zivljenjski_dobi_po_drzavah   

def main():
    CO2_emisije = podatki_o_CO2_po_drzavah()
    GDP = podatki_o_GDP_po_drzavah()
    kolicina_vode = podatki_o_kolicini_vode_po_drzavah()
    najstarejsi_prebivalci = podatki_o_najstarejsih_prebivalcih_po_drzavah()
    obnovljiva_energija = podatki_o_obnovljivi_energiji_po_drzavah()
    podhranjenost = podatki_o_podhranjenosti_prebivalstva_po_drzavah()
    poraba_energije = podatki_o_porabi_energije_po_drzavah()
    pricakovana_zivljenjska_doba = podatki_o_pricakovani_zivljenjski_dobi_po_drzavah()

if __name__ == '__main__':
    main()