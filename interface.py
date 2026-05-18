import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import platform
import subprocess

from airport import LoadAirports, SetSchengen, PlotAirports, MapAirports, AddAirport, RemoveAirport, Airport, \
    PrintAirport
#importem tot el necessari de aircraft.py (versió 2)
from aircraft import LoadArrivals, PlotArrivals, SaveFlights, PlotAirlines, PlotFlightsType, MapFlights, \
    LongDistanceArrivals
#importem tot el necessari de LEBL.py (versió 3)
from LEBL import LoadAirportStructure, AssignGate, GateOccupancy


class InterficieAeroports:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor d'Aeroports i Vols (Versió 3)")
        self.root.configure(bg="#F0F4F8")
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background="#F0F4F8", borderwidth=0)
        style.configure("TNotebook.Tab", background="#E1E5EA", font=("Helvetica", 10, "bold"), padding=[15, 5],
                        borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#0078D7")])

        self.aeroports = []
        self.vols = []
        self.bcn = None  #variable per a l'estructura de LEBL

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=15, pady=15)

        self.tab_aeroports = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_aeroports, text="Gestió d'Aeroports (V1)")

        self.tab_vols = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_vols, text="Arribades LEBL (V2)")

        # Pestanya per la Versió 3
        self.tab_portes = tk.Frame(self.notebook, bg="#FFFFFF")
        self.notebook.add(self.tab_portes, text="Gestió de Portes (V3)")

        self._construir_pestanya_aeroports()
        self._construir_pestanya_vols()
        self._construir_pestanya_portes()

    #PESTANYA 1: AEROPORTS
    def _construir_pestanya_aeroports(self):
        frame_top = tk.Frame(self.tab_aeroports, bg="#FFFFFF")
        frame_top.pack(padx=10, pady=20)

        #afegim l'estètica
        tk.Button(frame_top, text="Carregar aeroports", width=20, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.carregar).grid(row=0,
                                                                                                             column=0,
                                                                                                             padx=8,
                                                                                                             pady=8)
        tk.Button(frame_top, text="Mostrar gràfic", width=20, bg="#0078D7", fg="white", font=("Helvetica", 10, "bold"),
                  relief="flat", cursor="hand2", command=self.mostrar_grafic).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(frame_top, text="Mostrar a Google Earth", width=22, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.mostrar_mapa).grid(row=0,
                                                                                                                 column=2,
                                                                                                                 padx=8,
                                                                                                                 pady=8)

        self.label_estat_ap = tk.Label(self.tab_aeroports, text="Cap fitxer carregat", bg="#FFFFFF",
                                       font=("Helvetica", 10))
        self.label_estat_ap.pack(pady=10)

    def carregar(self):
        nom = filedialog.askopenfilename(
            title="Selecciona fitxer d'aeroports")  #obrirà el buscador d'arxius per tal que li introduim el fitxer d'aeroports
        if not nom: return
        self.aeroports = LoadAirports(nom)
        for a in self.aeroports: SetSchengen(a)
        self.label_estat_ap.config(text=f"Carregats {len(self.aeroports)} aeroports", fg="black")

    def mostrar_grafic(self):
        missatge_error = ""

        #comprovem si hi ha aeroports
        if len(self.aeroports) == 0:
            missatge_error = missatge_error + "No hi ha aeroports carregats. "

        #si la caixa d'errors que hem definit té text, ho mostrem i parem
        if len(missatge_error) > 0:
            self.label_estat_ap.config(text="ERROR: " + missatge_error, fg="red")
            return

        PlotAirports(self.aeroports)
        self.label_estat_ap.config(text="Gràfic mostrat correctament.", fg="black")

    def _obrir_kml(self, nom_fitxer):
        try:
            #agafem la ruta completa del fitxer
            ruta_absoluta = os.path.abspath(nom_fitxer)
            sistema = platform.system()

            if sistema == "Windows":
                os.startfile(ruta_absoluta)
            elif sistema == "Darwin":
                subprocess.call(["open", ruta_absoluta])
            else:
                subprocess.call(["xdg-open", ruta_absoluta])
        except Exception as e:
            messagebox.showwarning("Mapa", f"No s'ha pogut obrir Google Earth automàticament.\nError: {e}")

    def mostrar_mapa(self):
        missatge_error = ""

        if len(self.aeroports) == 0:
            missatge_error = missatge_error + "No hi ha aeroports carregats. "

        if len(missatge_error) > 0:
            self.label_estat_ap.config(text="ERROR: " + missatge_error, fg="red")
            return

        nom_arxiu = "mapa_aeroports_temp.kml"
        MapAirports(self.aeroports, nom_fitxer=nom_arxiu)
        self._obrir_kml(nom_arxiu)
        self.label_estat_ap.config(text="Mapa generat i obert a Google Earth.", fg="black")

    #PESTANYA 2: VOLS (VERSIÓ 2):
    def _construir_pestanya_vols(self):
        frame_controls = tk.Frame(self.tab_vols, bg="#FFFFFF")
        frame_controls.pack(padx=10, pady=20)

        #botons d'accions principals
        tk.Button(frame_controls, text="Load Arrivals", width=20, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.carregar_vols).grid(row=0,
                                                                                                                  column=0,
                                                                                                                  padx=8,
                                                                                                                  pady=8)
        tk.Button(frame_controls, text="Save Aircrafts", width=20, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.guardar_vols).grid(row=0,
                                                                                                                 column=1,
                                                                                                                 padx=8,
                                                                                                                 pady=8)

        #botons de gràfics
        tk.Button(frame_controls, text="Plot Arrivals (Hours)", width=20, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.grafic_hores).grid(row=1,
                                                                                                                 column=0,
                                                                                                                 padx=8,
                                                                                                                 pady=8)
        tk.Button(frame_controls, text="Plot Arrivals (Airlines)", width=22, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.grafic_aerolinies).grid(
            row=1, column=1, padx=8, pady=8)
        tk.Button(frame_controls, text="Plot Schengen vs Non", width=22, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.grafic_schengen).grid(
            row=1, column=2, padx=8, pady=8)

        #botons de Google Earth
        tk.Button(frame_controls, text="Map Trajectories", width=20, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.mapa_vols).grid(row=2,
                                                                                                              column=0,
                                                                                                              padx=8,
                                                                                                              pady=8)
        tk.Button(frame_controls, text="Map Long-Distance", width=22, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2",
                  command=self.mapa_vols_llarga_dist).grid(row=2, column=1, padx=8, pady=8)

        self.label_estat_vols = tk.Label(self.tab_vols, text="Cap fitxer de vols carregat", bg="#FFFFFF",
                                         font=("Helvetica", 10))
        self.label_estat_vols.pack(pady=15)

    def carregar_vols(self):
        nom = filedialog.askopenfilename(title="Selecciona fitxer Arrivals.txt")
        if not nom: return
        self.vols = LoadArrivals(nom)
        self.label_estat_vols.config(text=f"Carregats {len(self.vols)} vols", fg="black")

    def guardar_vols(self):
        missatge_error = ""

        if len(self.vols) == 0:
            missatge_error = missatge_error + "No hi ha vols carregats per guardar. "

        if len(missatge_error) > 0:
            self.label_estat_vols.config(text="ERROR: " + missatge_error, fg="red")
            return

        nom = filedialog.asksaveasfilename(defaultextension=".txt")
        if not nom:
            return  #si l'usuari tanca la finestra de guardar sense posar nom, no fem res

        SaveFlights(self.vols, nom)
        self.label_estat_vols.config(text="Vols desats correctament al fitxer.", fg="green")

    def grafic_hores(self):
        missatge_error = ""
        if len(self.vols) == 0:
            missatge_error = missatge_error + "Falten els vols. "

        if len(missatge_error) > 0:
            self.label_estat_vols.config(text="ERROR: " + missatge_error, fg="red")
            return

        PlotArrivals(self.vols)
        self.label_estat_vols.config(text="Gràfic d'hores mostrat correctament.", fg="black")

    def grafic_aerolinies(self):
        missatge_error = ""
        if len(self.vols) == 0:
            missatge_error = missatge_error + "Falten els vols. "

        if len(missatge_error) > 0:
            self.label_estat_vols.config(text="ERROR: " + missatge_error, fg="red")
            return

        PlotAirlines(self.vols)
        self.label_estat_vols.config(text="Gràfic d'aerolínies mostrat correctament.", fg="black")

    def grafic_schengen(self):
        #creem una "caixa" buida per anar guardant els errors que trobem
        missatge_error = ""

        #conprovem els aeroports. Si falten, afegim l'avís a la caixa
        if len(self.aeroports) == 0:
            missatge_error = missatge_error + "Falten els aeroports. "

        #ara comprovem els vols. Si falten, afegim l'avís a la mateixa caixa
        if len(self.vols) == 0:
            missatge_error = missatge_error + "Falten els vols. "

        #ara fem que es representen els errors
        if len(missatge_error) > 0:
            #si hi ha algun error (un o tots dos), ho mostrem tot junt i aturem la funció
            self.label_estat_vols.config(text="ERROR: " + missatge_error, fg="red")
            return

        PlotFlightsType(self.vols, self.aeroports)

        #tornem a posar el text normal avisant que tot ha anat bé si no hi ha errors
        self.label_estat_vols.config(text="Gràfic generat correctament.", fg="black")

    def mapa_vols(self):
        missatge_error = ""

        if len(self.aeroports) == 0:
            missatge_error = missatge_error + "Falten els aeroports. "
        if len(self.vols) == 0:
            missatge_error = missatge_error + "Falten els vols. "

        if len(missatge_error) > 0:
            self.label_estat_vols.config(text="ERROR: " + missatge_error, fg="red")
            return

        nom_arxiu = "trajectes_temp.kml"
        MapFlights(self.vols, self.aeroports, nom_arxiu)
        self._obrir_kml(nom_arxiu)
        self.label_estat_vols.config(text="Mapa de trajectòries obert a Google Earth.", fg="black")

    def mapa_vols_llarga_dist(self):
        missatge_error = ""

        if len(self.aeroports) == 0:
            missatge_error = missatge_error + "Falten els aeroports. "
        if len(self.vols) == 0:
            missatge_error = missatge_error + "Falten els vols. "

        if len(missatge_error) > 0:
            self.label_estat_vols.config(text="ERROR: " + missatge_error, fg="red")
            return

        #busquem els vols llargs
        vols_llargs = LongDistanceArrivals(self.vols, self.aeroports)
        if len(vols_llargs) == 0:
            self.label_estat_vols.config(text="No s'han trobat vols a més de 2000km.", fg="blue")
            return

        nom_arxiu = "trajectes_llargs_temp.kml"
        MapFlights(vols_llargs, self.aeroports, nom_arxiu)
        self._obrir_kml(nom_arxiu)
        self.label_estat_vols.config(text="Mapa de llarga distància obert a Google Earth.", fg="black")

    #PESTANYA 3 (V3): GESTIÓ DE PORTES
    def _construir_pestanya_portes(self):
        #creem un marc per posar els botons de la versio 3
        frame_controls = tk.Frame(self.tab_portes, bg="#FFFFFF")
        frame_controls.pack(padx=10, pady=20)

        #botons principals de la pestanya
        tk.Button(frame_controls, text="Construir Estructura LEBL", width=25, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.carregar_estructura).grid(
            row=0, column=0, padx=8, pady=8)

        tk.Button(frame_controls, text="Assignar Portes a Vols", width=25, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.assignar_portes).grid(
            row=0, column=1, padx=8, pady=8)

        tk.Button(frame_controls, text="Llista d'Ocupació", width=25, bg="#0078D7", fg="white",
                  font=("Helvetica", 10, "bold"), relief="flat", cursor="hand2", command=self.mostrar_ocupacio).grid(
            row=0, column=2, padx=8, pady=8)

        #etiqueta per avisar a l'usuari de com funciona tot aixo
        self.label_estat_portes = tk.Label(self.tab_portes, text="Recorda carregar primer Airports i Arrivals.",
                                           bg="#FFFFFF", font=("Helvetica", 10))
        self.label_estat_portes.pack(pady=5)

        #caixa de text gran on ensenyarem totes les portes
        self.text_ocupacio = tk.Text(self.tab_portes, height=12, width=70, bg="#F0F4F8", font=("Courier", 10))
        self.text_ocupacio.pack(pady=10)

    def carregar_estructura(self):
        #obrim el buscador d'arxius per triar el text de les terminals
        nom = filedialog.askopenfilename(title="Selecciona el fitxer de l'aeroport (ex: Terminals.txt)")
        if not nom: return
        self.bcn = LoadAirportStructure(nom)

        #si s'ha creat be l'aeroport ho diem en verd, sino tirem error en vermell
        if self.bcn is not None:
            self.label_estat_portes.config(text=f"Estructura de l'aeroport {self.bcn.code} construïda amb èxit.",
                                           fg="green")
        else:
            self.label_estat_portes.config(text="ERROR: No s'ha pogut leer el fitxer de l'estructura.", fg="red")

    def assignar_portes(self):
        #creem la caixa d'errors buida com feiem abans
        missatge_error = ""

        #conprovem que l'usuari hagi carregat tot el que necessitem abans de donarli al boto
        if self.bcn is None:
            missatge_error = missatge_error + "Has de carregar primer l'estructura LEBL. "
        if len(self.vols) == 0:
            missatge_error = missatge_error + "Falten els vols (Pestanya 2). "

        #si hi ha errors els ensenyem i parem el codi per no petar
        if len(missatge_error) > 0:
            self.label_estat_portes.config(text="ERROR: " + missatge_error, fg="red")
            return

        # variables per comptar els que aparquem be i els que fallen
        assignats_ok = 0
        assignats_error = 0

        #bucle per intentar aparcar tots els avions de la llista
        i = 0
        while i < len(self.vols):
            # cridem la funcio mestra del LEBL.py
            res = AssignGate(self.bcn, self.vols[i])
            if res == 0:
                assignats_ok = assignats_ok + 1
            else:
                assignats_error = assignats_error + 1
            i = i + 1

        self.label_estat_portes.config(
            text=f"Portes assignades: {assignats_ok} OK, {assignats_error} rebutjats (sense espai o informació).",
            fg="black")

    def mostrar_ocupacio(self):
        #primer mirem que tinguem l'aeroport a la memoria
        if self.bcn is None:
            self.label_estat_portes.config(text="ERROR: Estructura no carregada.", fg="red")
            return

        #cridem la funcio que ens fa la llista d'ocupacio
        ocupacio = GateOccupancy(self.bcn)

        #netejem la caixa de text sencera per no barrejar llistes velles si cliquem dos cops
        self.text_ocupacio.delete('1.0', tk.END)
        self.text_ocupacio.insert(tk.END, f"--- REPORTE D'OCUPACIÓ DE PORTES A {self.bcn.code} ---\n")

        #bucle per escriure linia a linia l'estat de cada porta
        i = 0
        while i < len(ocupacio):
            porta_info = ocupacio[i]
            nom_porta = porta_info[0]
            estat = porta_info[1]
            vol_id = porta_info[2]

            #mirem el boolea per saber si esta ocupada o lliure
            if estat == True:
                linia = f"Porta {nom_porta} : OCUPADA per vol [{vol_id}]\n"
            else:
                linia = f"Porta {nom_porta} : Lliure\n"

            #ho fiquem a la caixa de text de la pantalla
            self.text_ocupacio.insert(tk.END, linia)
            i = i + 1

        self.label_estat_portes.config(text="Llista d'ocupació generada amb èxit.", fg="green")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("750x450")
    app = InterficieAeroports(root)
    root.mainloop()