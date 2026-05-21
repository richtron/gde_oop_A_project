from abc import ABC, abstractmethod
from datetime import date, datetime, timedelta
import tkinter as tk
from tkinter import messagebox, ttk


class KolcsonzoHiba(Exception):
    """Az autokolcsonzo rendszer sajat hibaja."""


class Auto(ABC):
    def __init__(self, rendszam: str, tipus: str, berleti_dij: int):
        self.rendszam = rendszam
        self.tipus = tipus
        self.berleti_dij = berleti_dij

    @property
    def rendszam(self) -> str:
        return self.__rendszam

    @rendszam.setter
    def rendszam(self, ertek: str) -> None:
        ertek = ertek.strip().upper()
        if len(ertek) < 5:
            raise ValueError("A rendszam tul rovid.")
        self.__rendszam = ertek

    @property
    def tipus(self) -> str:
        return self.__tipus

    @tipus.setter
    def tipus(self, ertek: str) -> None:
        ertek = ertek.strip()
        if not ertek:
            raise ValueError("A tipus nem lehet ures.")
        self.__tipus = ertek

    @property
    def berleti_dij(self) -> int:
        return self.__berleti_dij

    @berleti_dij.setter
    def berleti_dij(self, ertek: int) -> None:
        if ertek <= 0:
            raise ValueError("A berleti dij csak pozitiv szam lehet.")
        self.__berleti_dij = ertek

    @abstractmethod
    def adatok(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.rendszam} - {self.tipus}, {self.berleti_dij} Ft/nap"


class Szemelyauto(Auto):
    def __init__(self, rendszam: str, tipus: str, berleti_dij: int, ulesek_szama: int):
        super().__init__(rendszam, tipus, berleti_dij)
        self.ulesek_szama = ulesek_szama

    @property
    def ulesek_szama(self) -> int:
        return self.__ulesek_szama

    @ulesek_szama.setter
    def ulesek_szama(self, ertek: int) -> None:
        if ertek < 2:
            raise ValueError("Egy szemelyautoban legalabb 2 ulesnek kell lennie.")
        self.__ulesek_szama = ertek

    def adatok(self) -> str:
        return f"Szemelyauto | {self} | ulesek: {self.ulesek_szama}"


class Teherauto(Auto):
    def __init__(self, rendszam: str, tipus: str, berleti_dij: int, teherbiras_kg: int):
        super().__init__(rendszam, tipus, berleti_dij)
        self.teherbiras_kg = teherbiras_kg

    @property
    def teherbiras_kg(self) -> int:
        return self.__teherbiras_kg

    @teherbiras_kg.setter
    def teherbiras_kg(self, ertek: int) -> None:
        if ertek <= 0:
            raise ValueError("A teherbiras csak pozitiv szam lehet.")
        self.__teherbiras_kg = ertek

    def adatok(self) -> str:
        return f"Teherauto   | {self} | teherbiras: {self.teherbiras_kg} kg"


class Berles:
    def __init__(self, auto: Auto, kezdo_datum: date, veg_datum: date, berlo_neve: str):
        self.auto = auto
        self.kezdo_datum = kezdo_datum
        self.veg_datum = veg_datum
        self.berlo_neve = berlo_neve

    @property
    def auto(self) -> Auto:
        return self.__auto

    @auto.setter
    def auto(self, ertek: Auto) -> None:
        if not isinstance(ertek, Auto):
            raise ValueError("A berleshez ervenyes auto szukseges.")
        self.__auto = ertek

    @property
    def kezdo_datum(self) -> date:
        return self.__kezdo_datum

    @kezdo_datum.setter
    def kezdo_datum(self, ertek: date) -> None:
        if not isinstance(ertek, date):
            raise ValueError("A berles kezdo datumahoz datumot kell megadni.")
        self.__kezdo_datum = ertek

    @property
    def veg_datum(self) -> date:
        return self.__veg_datum

    @veg_datum.setter
    def veg_datum(self, ertek: date) -> None:
        if not isinstance(ertek, date):
            raise ValueError("A berles vegdatumahoz datumot kell megadni.")
        self.__veg_datum = ertek

    @property
    def napok_szama(self) -> int:
        return (self.veg_datum - self.kezdo_datum).days + 1

    @property
    def teljes_ar(self) -> int:
        return self.napok_szama * self.auto.berleti_dij

    @property
    def berlo_neve(self) -> str:
        return self.__berlo_neve

    @berlo_neve.setter
    def berlo_neve(self, ertek: str) -> None:
        ertek = ertek.strip()
        if len(ertek) < 2:
            raise ValueError("A berlo neve tul rovid.")
        self.__berlo_neve = ertek

    def __str__(self) -> str:
        return (
            f"{self.auto.rendszam} - {self.auto.tipus} | "
            f"{self.kezdo_datum.isoformat()} - {self.veg_datum.isoformat()} | "
            f"berlo: {self.berlo_neve} | {self.teljes_ar} Ft"
        )


class Autokolcsonzo:
    def __init__(self, nev: str):
        self.nev = nev
        self.__autok: list[Auto] = []
        self.__berlesek: list[Berles] = []

    @property
    def nev(self) -> str:
        return self.__nev

    @nev.setter
    def nev(self, ertek: str) -> None:
        ertek = ertek.strip()
        if not ertek:
            raise ValueError("A kolcsonzo neve nem lehet ures.")
        self.__nev = ertek

    @property
    def autok(self) -> tuple[Auto, ...]:
        return tuple(self.__autok)

    @property
    def berlesek(self) -> tuple[Berles, ...]:
        return tuple(self.__berlesek)

    def auto_hozzaadasa(self, auto: Auto) -> None:
        if self.__auto_keresese(auto.rendszam) is not None:
            raise KolcsonzoHiba("Ilyen rendszamu auto mar szerepel a rendszerben.")
        self.__autok.append(auto)

    def berles_letrehozasa(self, rendszam: str, kezdo_datum: date, veg_datum: date, berlo_neve: str) -> int:
        self.__idoszak_ellenorzese(kezdo_datum, veg_datum)
        auto = self.__auto_keresese(rendszam)
        if auto is None:
            raise KolcsonzoHiba("Nincs ilyen rendszamu auto.")
        if not self.auto_elerheto(auto.rendszam, kezdo_datum, veg_datum):
            raise KolcsonzoHiba("Ez az auto a megadott idoszakban mar foglalt.")

        berles = Berles(auto, kezdo_datum, veg_datum, berlo_neve)
        self.__berlesek.append(berles)
        return berles.teljes_ar

    def berles_lemondasa(self, rendszam: str, kezdo_datum: date, veg_datum: date) -> Berles:
        for berles in self.__berlesek:
            if (
                berles.auto.rendszam == rendszam.upper()
                and berles.kezdo_datum == kezdo_datum
                and berles.veg_datum == veg_datum
            ):
                self.__berlesek.remove(berles)
                return berles
        raise KolcsonzoHiba("Nem talalhato ilyen berles, ezert nem lehet lemondani.")

    def elerheto_autok(self, kezdo_datum: date, veg_datum: date) -> tuple[Auto, ...]:
        self.__idoszak_ellenorzese(kezdo_datum, veg_datum)
        return tuple(
            auto
            for auto in self.__autok
            if self.auto_elerheto(auto.rendszam, kezdo_datum, veg_datum)
        )

    def auto_elerheto(self, rendszam: str, kezdo_datum: date, veg_datum: date) -> bool:
        rendszam = rendszam.strip().upper()
        return all(
            berles.auto.rendszam != rendszam
            or not self.__idoszakok_atfedik_egymast(
                berles.kezdo_datum,
                berles.veg_datum,
                kezdo_datum,
                veg_datum,
            )
            for berles in self.__berlesek
        )

    def __auto_keresese(self, rendszam: str) -> Auto | None:
        rendszam = rendszam.strip().upper()
        for auto in self.__autok:
            if auto.rendszam == rendszam:
                return auto
        return None

    @staticmethod
    def __idoszakok_atfedik_egymast(elso_kezdet: date, elso_veg: date, masodik_kezdet: date, masodik_veg: date) -> bool:
        return elso_kezdet <= masodik_veg and masodik_kezdet <= elso_veg

    @staticmethod
    def __idoszak_ellenorzese(kezdo_datum: date, veg_datum: date) -> None:
        if kezdo_datum < date.today():
            raise KolcsonzoHiba("Multbeli datumra nem lehet autot berelni.")
        if veg_datum < kezdo_datum:
            raise KolcsonzoHiba("A berles vege nem lehet korabban, mint a kezdete.")


def datum_szovegbol(szoveg: str) -> date:
    try:
        return datetime.strptime(szoveg, "%Y-%m-%d").date()
    except ValueError as hiba:
        raise KolcsonzoHiba("Hibas datumformatum. Pelda: 2026-05-24") from hiba


def kezdo_kolcsonzo_letrehozasa() -> Autokolcsonzo:
    kolcsonzo = Autokolcsonzo("Villam Auto Kolcsonzo")

    kolcsonzo.auto_hozzaadasa(Szemelyauto("ABC-123", "Toyota Corolla", 12000, 5))
    kolcsonzo.auto_hozzaadasa(Szemelyauto("DEF-456", "Volkswagen Golf", 14000, 5))
    kolcsonzo.auto_hozzaadasa(Teherauto("GHI-789", "Ford Transit", 22000, 1300))

    kolcsonzo.berles_letrehozasa("ABC-123", date(2026, 5, 22), date(2026, 5, 23), "Kovacs Anna")
    kolcsonzo.berles_letrehozasa("DEF-456", date(2026, 5, 22), date(2026, 5, 22), "Nagy Bela")
    kolcsonzo.berles_letrehozasa("GHI-789", date(2026, 5, 23), date(2026, 5, 25), "Toth Csaba")
    kolcsonzo.berles_letrehozasa("ABC-123", date(2026, 5, 25), date(2026, 5, 26), "Szabo Dora")

    return kolcsonzo


class AutokolcsonzoGUI:
    def __init__(self, kolcsonzo: Autokolcsonzo):
        self.__kolcsonzo = kolcsonzo
        self.__ablak = tk.Tk()
        self.__ablak.title(kolcsonzo.nev)
        self.__ablak.geometry("920x560")
        self.__ablak.minsize(820, 500)

        self.__rendszam_valtozo = tk.StringVar()
        self.__kezdo_datum_valtozo = tk.StringVar(value=date.today().isoformat())
        self.__veg_datum_valtozo = tk.StringVar(value=(date.today() + timedelta(days=1)).isoformat())
        self.__berlo_valtozo = tk.StringVar()

        self.__stilus_beallitasa()
        self.__felulet_felepitese()
        self.__elerheto_autok_frissitese()
        self.__berlesek_frissitese()

    def inditas(self) -> None:
        self.__ablak.mainloop()

    def __stilus_beallitasa(self) -> None:
        stilus = ttk.Style()
        stilus.theme_use("clam")
        stilus.configure("TFrame", background="#f4f6f8")
        stilus.configure("TLabelframe", background="#f4f6f8", padding=12)
        stilus.configure("TLabelframe.Label", background="#f4f6f8", font=("Segoe UI", 10, "bold"))
        stilus.configure("TLabel", background="#f4f6f8", font=("Segoe UI", 10))
        stilus.configure("TButton", font=("Segoe UI", 10), padding=6)
        stilus.configure("Heading.TLabel", font=("Segoe UI", 18, "bold"))

    def __felulet_felepitese(self) -> None:
        fo_keret = ttk.Frame(self.__ablak, padding=18)
        fo_keret.pack(fill=tk.BOTH, expand=True)

        fejlec = ttk.Label(fo_keret, text=self.__kolcsonzo.nev, style="Heading.TLabel")
        fejlec.pack(anchor=tk.W, pady=(0, 14))

        tartalom = ttk.Frame(fo_keret)
        tartalom.pack(fill=tk.BOTH, expand=True)
        tartalom.columnconfigure(0, weight=2)
        tartalom.columnconfigure(1, weight=3)
        tartalom.rowconfigure(0, weight=1)

        bal_oldal = ttk.Frame(tartalom)
        bal_oldal.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        bal_oldal.rowconfigure(1, weight=1)

        jobb_oldal = ttk.Frame(tartalom)
        jobb_oldal.grid(row=0, column=1, sticky="nsew")
        jobb_oldal.rowconfigure(1, weight=1)

        self.__urlap_letrehozasa(bal_oldal)
        self.__auto_lista_letrehozasa(bal_oldal)
        self.__berles_lista_letrehozasa(jobb_oldal)

    def __urlap_letrehozasa(self, szulo: ttk.Frame) -> None:
        urlap = ttk.LabelFrame(szulo, text="Auto berlese")
        urlap.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        urlap.columnconfigure(1, weight=1)

        ttk.Label(urlap, text="Rendszam").grid(row=0, column=0, sticky=tk.W, pady=4)
        self.__rendszam_mezo = ttk.Combobox(
            urlap,
            textvariable=self.__rendszam_valtozo,
            state="readonly",
            values=[auto.rendszam for auto in self.__kolcsonzo.autok],
        )
        self.__rendszam_mezo.grid(row=0, column=1, sticky="ew", pady=4)
        if self.__kolcsonzo.autok:
            self.__rendszam_valtozo.set(self.__kolcsonzo.autok[0].rendszam)

        ttk.Label(urlap, text="Kezdo datum").grid(row=1, column=0, sticky=tk.W, pady=4)
        kezdo_mezo = ttk.Entry(urlap, textvariable=self.__kezdo_datum_valtozo)
        kezdo_mezo.grid(row=1, column=1, sticky="ew", pady=4)
        kezdo_mezo.bind("<FocusOut>", self.__elerheto_autok_frissitese)

        ttk.Label(urlap, text="Vegdatum").grid(row=2, column=0, sticky=tk.W, pady=4)
        veg_mezo = ttk.Entry(urlap, textvariable=self.__veg_datum_valtozo)
        veg_mezo.grid(row=2, column=1, sticky="ew", pady=4)
        veg_mezo.bind("<FocusOut>", self.__elerheto_autok_frissitese)

        ttk.Label(urlap, text="Berlo neve").grid(row=3, column=0, sticky=tk.W, pady=4)
        ttk.Entry(urlap, textvariable=self.__berlo_valtozo).grid(row=3, column=1, sticky="ew", pady=4)

        gombok = ttk.Frame(urlap)
        gombok.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        gombok.columnconfigure(0, weight=1)
        gombok.columnconfigure(1, weight=1)
        gombok.columnconfigure(2, weight=1)

        ttk.Button(gombok, text="Elerheto autok", command=self.__elerheto_autok_frissitese).grid(
            row=0, column=0, sticky="ew", padx=(0, 5)
        )
        ttk.Button(gombok, text="Berles", command=self.__berles_letrehozasa).grid(
            row=0, column=1, sticky="ew", padx=5
        )
        ttk.Button(gombok, text="Kivalasztott berles lemondasa", command=self.__berles_lemondasa).grid(
            row=0, column=2, sticky="ew", padx=(5, 0)
        )

    def __auto_lista_letrehozasa(self, szulo: ttk.Frame) -> None:
        keret = ttk.LabelFrame(szulo, text="Elerheto autok a megadott idoszakban")
        keret.grid(row=1, column=0, sticky="nsew")
        keret.rowconfigure(0, weight=1)
        keret.columnconfigure(0, weight=1)

        oszlopok = ("rendszam", "tipus", "dij", "adat")
        self.__auto_tabla = ttk.Treeview(keret, columns=oszlopok, show="headings", height=8)
        self.__auto_tabla.heading("rendszam", text="Rendszam")
        self.__auto_tabla.heading("tipus", text="Tipus")
        self.__auto_tabla.heading("dij", text="Dij/nap")
        self.__auto_tabla.heading("adat", text="Extra adat")
        self.__auto_tabla.column("rendszam", width=85, anchor=tk.CENTER)
        self.__auto_tabla.column("tipus", width=150)
        self.__auto_tabla.column("dij", width=90, anchor=tk.E)
        self.__auto_tabla.column("adat", width=120)
        self.__auto_tabla.grid(row=0, column=0, sticky="nsew")
        self.__auto_tabla.bind("<<TreeviewSelect>>", self.__auto_kivalasztasa)

    def __berles_lista_letrehozasa(self, szulo: ttk.Frame) -> None:
        fejlec_sor = ttk.Frame(szulo)
        fejlec_sor.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        fejlec_sor.columnconfigure(0, weight=1)

        ttk.Label(fejlec_sor, text="Aktualis berlesek", style="Heading.TLabel").grid(row=0, column=0, sticky=tk.W)
        ttk.Button(fejlec_sor, text="Frissites", command=self.__berlesek_frissitese).grid(row=0, column=1)

        oszlopok = ("rendszam", "tipus", "kezdet", "veg", "berlo", "ar")
        self.__berles_tabla = ttk.Treeview(szulo, columns=oszlopok, show="headings", height=14)
        self.__berles_tabla.heading("rendszam", text="Rendszam")
        self.__berles_tabla.heading("tipus", text="Tipus")
        self.__berles_tabla.heading("kezdet", text="Kezdet")
        self.__berles_tabla.heading("veg", text="Vege")
        self.__berles_tabla.heading("berlo", text="Berlo")
        self.__berles_tabla.heading("ar", text="Ar")
        self.__berles_tabla.column("rendszam", width=90, anchor=tk.CENTER)
        self.__berles_tabla.column("tipus", width=150)
        self.__berles_tabla.column("kezdet", width=100, anchor=tk.CENTER)
        self.__berles_tabla.column("veg", width=100, anchor=tk.CENTER)
        self.__berles_tabla.column("berlo", width=140)
        self.__berles_tabla.column("ar", width=85, anchor=tk.E)
        self.__berles_tabla.grid(row=1, column=0, sticky="nsew")

    def __elerheto_autok_frissitese(self, _esemeny: tk.Event | None = None) -> None:
        self.__auto_tabla.delete(*self.__auto_tabla.get_children())
        try:
            kezdo_datum, veg_datum = self.__idoszak_bekerese()
            autok = self.__kolcsonzo.elerheto_autok(kezdo_datum, veg_datum)
        except KolcsonzoHiba as hiba:
            if _esemeny is None:
                messagebox.showerror("Hiba", str(hiba))
            autok = ()

        rendszamok = [auto.rendszam for auto in autok]
        self.__rendszam_mezo["values"] = rendszamok
        if self.__rendszam_valtozo.get() not in rendszamok:
            self.__rendszam_valtozo.set(rendszamok[0] if rendszamok else "")

        for auto in autok:
            extra_adat = self.__extra_auto_adat(auto)
            self.__auto_tabla.insert(
                "",
                tk.END,
                values=(auto.rendszam, auto.tipus, f"{auto.berleti_dij} Ft", extra_adat),
            )

    def __berlesek_frissitese(self) -> None:
        self.__berles_tabla.delete(*self.__berles_tabla.get_children())
        for berles in self.__kolcsonzo.berlesek:
            self.__berles_tabla.insert(
                "",
                tk.END,
                values=(
                    berles.auto.rendszam,
                    berles.auto.tipus,
                    berles.kezdo_datum.isoformat(),
                    berles.veg_datum.isoformat(),
                    berles.berlo_neve,
                    f"{berles.teljes_ar} Ft",
                ),
            )

    def __berles_letrehozasa(self) -> None:
        try:
            kezdo_datum, veg_datum = self.__idoszak_bekerese()
            ar = self.__kolcsonzo.berles_letrehozasa(
                self.__rendszam_valtozo.get(),
                kezdo_datum,
                veg_datum,
                self.__berlo_valtozo.get(),
            )
            self.__berlo_valtozo.set("")
            self.__elerheto_autok_frissitese()
            self.__berlesek_frissitese()
            messagebox.showinfo("Sikeres berles", f"A berles ara: {ar} Ft")
        except (KolcsonzoHiba, ValueError) as hiba:
            messagebox.showerror("Hiba", str(hiba))

    def __berles_lemondasa(self) -> None:
        kivalasztott = self.__berles_tabla.selection()
        if not kivalasztott:
            messagebox.showwarning("Nincs kivalasztas", "Valassz ki egy berlest a listabol.")
            return

        ertekek = self.__berles_tabla.item(kivalasztott[0], "values")
        rendszam = ertekek[0]
        kezdo_datum = datum_szovegbol(ertekek[2])
        veg_datum = datum_szovegbol(ertekek[3])

        try:
            torolt_berles = self.__kolcsonzo.berles_lemondasa(rendszam, kezdo_datum, veg_datum)
            self.__elerheto_autok_frissitese()
            self.__berlesek_frissitese()
            messagebox.showinfo("Berles lemondva", str(torolt_berles))
        except KolcsonzoHiba as hiba:
            messagebox.showerror("Hiba", str(hiba))

    def __idoszak_bekerese(self) -> tuple[date, date]:
        kezdo_datum = datum_szovegbol(self.__kezdo_datum_valtozo.get().strip())
        veg_datum = datum_szovegbol(self.__veg_datum_valtozo.get().strip())
        return kezdo_datum, veg_datum

    def __auto_kivalasztasa(self, _esemeny: tk.Event) -> None:
        kivalasztott = self.__auto_tabla.selection()
        if not kivalasztott:
            return
        ertekek = self.__auto_tabla.item(kivalasztott[0], "values")
        self.__rendszam_valtozo.set(ertekek[0])

    @staticmethod
    def __extra_auto_adat(auto: Auto) -> str:
        if isinstance(auto, Szemelyauto):
            return f"{auto.ulesek_szama} ules"
        if isinstance(auto, Teherauto):
            return f"{auto.teherbiras_kg} kg"
        return "-"


def main() -> None:
    kolcsonzo = kezdo_kolcsonzo_letrehozasa()
    alkalmazas = AutokolcsonzoGUI(kolcsonzo)
    alkalmazas.inditas()


if __name__ == "__main__":
    main()
