# Autokolcsonzo Rendszer

Egyszeru, grafikus Python alkalmazas autok berlesere, berlesek lemondasara es az aktualis berlesek listazasara.

## Futtatas

```bash
python main.py
```

Windows alatt konzolablak nelkuli inditashoz:

```bash
autokolcsonzo_gui.pyw
```

## Funkciok

- autok listazasa
- auto berlese megadott kezdo- es vegdatummal
- meglevo berles lemondasa
- aktualis berlesek listazasa
- csak a megadott idoszakban elerheto autok listazasa
- rendszam es datum alapu adatvalidacio
- intervallum-utkozes ellenorzese, hogy foglalt autot ne lehessen berelni
- hibakezeles hibas bemenetekre
- Tkinter alapu grafikus felulet

## Projekt felepitese

- `Auto`: absztrakt alaposztaly
- `Szemelyauto`: szemelyauto tipus
- `Teherauto`: teherauto tipus
- `Berles`: egy auto kezdo- es vegdatumos berleset tarolja
- `Autokolcsonzo`: autokat es berleseket kezelo osztaly
- `main.py`: grafikus felhasznaloi felulet es kezdo adatok
