import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os
import platform
import subprocess


#esmentem aqui la trampa de matplotlib.use('TkAgg') per evitar finestres flotants lletges.
#amb aixo fiquem el grafic a dins del programa mateix.
import matplotlib

matplotlib.use('TkAgg')
#---------------------------------------------------------

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from airport import LoadAirports, SetSchengen, PlotAirports, MapAirports, AddAirport, RemoveAirport, Airport, \
    SaveSchengenAirports
from aircraft import LoadArrivals, LoadDepartures, MergeMovements, PlotArrivals, SaveFlights, PlotAirlines, \
    PlotFlightsType, MapFlights, LongDistanceArrivals
from LEBL import LoadAirportStructure, AssignGate, GateOccupancy, AssignNightGates, AssignGatesAtTime, PlotDayOccupancy

#preparem tot el disseny de la pantalla creant l'espai per les columnes de botons
class InterficieAeroports:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor d'Aeroports (Interfície Integrada)")

        try:
            self.root.state('zoomed')
        except:
            self.root.attributes('-zoomed', True)

        self.bg_color = "#F2EFE8"
        self.btn_color = "#E2DCCF"
        self.text_color = "#3A3027"

        self.root.configure(bg=self.bg_color)

        self.aeroports = []
        self.vols = []
        self.bcn = None
        self.departures = []
        self.merged_vols = []

        #Guardem la ruta de les arribades per recarregar-les netes al fer el merge
        self.ruta_arrivals = ""

        self.root.rowconfigure(0, weight=6)
        self.root.rowconfigure(1, weight=4)
        self.root.columnconfigure(0, weight=1)

        #=========================================================================
        #MEITAT SUPERIOR: GRAFICS I CONSOLA D'INFORMACIO
        #=========================================================================
        top_frame = tk.Frame(root, bg=self.bg_color)
        top_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        top_frame.columnconfigure(0, weight=6)
        top_frame.columnconfigure(1, weight=4)

        self.frame_grafic = tk.LabelFrame(top_frame, text=" Visualitzador de Gràfics ", font=("Arial", 10, "bold"),
                                          bg=self.bg_color, fg="#3E2723")
        self.frame_grafic.grid(row=0, column=0, sticky="nsew", padx=5)

        self.frame_console = tk.LabelFrame(top_frame, text=" Informació i Logs ", font=("Arial", 10, "bold"),
                                           bg=self.bg_color, fg="#3E2723")
        self.frame_console.grid(row=0, column=1, sticky="nsew", padx=5)

        scrollbar = tk.Scrollbar(self.frame_console)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_console = tk.Text(self.frame_console, bg="#FFFFFF", fg=self.text_color, font=("Courier", 10),
                                    yscrollcommand=scrollbar.set)
        self.text_console.pack(side=tk.LEFT, fill="both", expand=True, padx=5, pady=5)
        scrollbar.config(command=self.text_console.yview)

        self.text_console.config(state="disabled")

        #=========================================================================
        #MEITAT INFERIOR: 4 COLUMNES AMB REQUADRES ESTATS
        #=========================================================================
        bottom_frame = tk.Frame(root, bg=self.bg_color)
        bottom_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        bottom_frame.columnconfigure(0, weight=1, uniform="cols")
        bottom_frame.columnconfigure(1, weight=1, uniform="cols")
        bottom_frame.columnconfigure(2, weight=1, uniform="cols")
        bottom_frame.columnconfigure(3, weight=1, uniform="cols")

        #--- COLUMNA 1: AEROPORTS ---
        col1 = tk.LabelFrame(bottom_frame, text=" Aeroports ", font=("Arial", 11, "bold"), bg=self.bg_color,
                             fg="#3E2723", bd=2, relief="groove")
        col1.grid(row=0, column=0, sticky="nsew", padx=5, pady=2)

        self._crear_boto(col1, "Carregar aeroports des de fitxer", self.carregar_aeroports)
        self._crear_boto(col1, "Afegir manualment (Pop-up)", self.popup_afegir_aeroport)
        self._crear_boto(col1, "Eliminar seleccionat (Pop-up)", self.popup_eliminar_aeroport)
        self._crear_boto(col1, "Gràfic tipus d'aeroport", self.grafic_aeroports)
        self._crear_boto(col1, "KML Aeroports (Google Earth)", self.mapa_aeroports)
        self._crear_boto(col1, "Exportar Schengen (fitxer)", self.exportar_schengen_manual)

        #--- COLUMNA 2: ARRIBADES ---
        col2 = tk.LabelFrame(bottom_frame, text=" Arribades ", font=("Arial", 11, "bold"), bg=self.bg_color,
                             fg="#3E2723", bd=2, relief="groove")
        col2.grid(row=0, column=1, sticky="nsew", padx=5, pady=2)

        self._crear_boto(col2, "Carregar vols desde fitxer", self.carregar_arribades)
        self._crear_boto(col2, "Gràfic arribades/hora", self.grafic_hores)
        self._crear_boto(col2, "Gràfic aerolínies (Top 5)", self.grafic_aerolinies_top5)
        self._crear_boto(col2, "Gràfic aerolínies (Totes)", self.grafic_aerolinies_todas)
        self._crear_boto(col2, "Gràfic tipus de vol", self.grafic_schengen_vols)
        self._crear_boto(col2, "Exportar vols (fitxer)", self.exportar_vols_manual)

        #--- COLUMNA 3: SORTIDES ---
        col3 = tk.LabelFrame(bottom_frame, text=" Sortides ", font=("Arial", 11, "bold"), bg=self.bg_color,
                             fg="#3E2723", bd=2, relief="groove")
        col3.grid(row=0, column=2, sticky="nsew", padx=5, pady=2)

        self._crear_boto(col3, "Carregar sortides (i merge)", self.carregar_sortides)
        self._crear_boto(col3, "KML Totes les rutes", self.mapa_vols)
        self._crear_boto(col3, "KML Rutes > 2000km", self.mapa_vols_llarga)
        self._crear_boto(col3, "Visor Satèl·lit Natiu", self.obrir_visor_google)

        #--- COLUMNA 4: PORTES LEBL ---
        col4 = tk.LabelFrame(bottom_frame, text=" Portes LEBL ", font=("Arial", 11, "bold"), bg=self.bg_color,
                             fg="#3E2723", bd=2, relief="groove")
        col4.grid(row=0, column=3, sticky="nsew", padx=5, pady=2)

        self._crear_boto(col4, "Carregar estructura LEBL", self.carregar_estructura)
        self._crear_boto(col4, "Assignar Night Gates (00:00)", self.assignar_nocturns)
        self._crear_boto(col4, "Gràfic Ocupació 24h (Estàtic)", self.mostrar_grafic_dia)
        self._crear_boto(col4, "Simulació Animada (Slider)", self.animacio_portes_slider)

        self.escriure_consola("Interfície iniciada. Llista per carregar dades.")

    #=========================================================================
    #EL PATCH PER INCRUSTAR ELS GRAFICS
    #=========================================================================
    #aqui canviem el comportament de dibuixar grafics perque no s'obrin a fora
    def mostrar_al_canvas(self, funcio_grafic, dades1, dades2=None, dades3=None):
        show_original = plt.show

        def plt_show_buit():
            pass

        plt.show = plt_show_buit

        try:
            plt.close('all')

            if dades2 is None and dades3 is None:
                funcio_grafic(dades1)
            elif dades3 is None:
                funcio_grafic(dades1, dades2)
            else:
                funcio_grafic(dades1, dades2, dades3)

            figura = plt.gcf()
            figura.set_size_inches(7, 4)
            figura.tight_layout()

            fills = self.frame_grafic.winfo_children()
            i = 0
            while i < len(fills):
                fills[i].destroy()
                i = i + 1

            canvas = FigureCanvasTkAgg(figura, master=self.frame_grafic)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            self.escriure_consola("Gràfic incrustat correctament adaptat a la pantalla.")

        except Exception as e:
            self.escriure_consola("ERROR generant el gràfic: " + str(e))
        finally:
            plt.show = show_original
            plt.close('all')

    #=========================================================================
    #ESCRIURE A LA CONSOLA
    #=========================================================================
    #funcio per anar escrivint textos a la pantalleta dreta
    def escriure_consola(self, text):
        self.text_console.config(state="normal")
        self.text_console.insert(tk.END, text + "\n")
        self.text_console.see(tk.END)
        self.text_console.config(state="disabled")

    #funcio basica per crear botons facil i rapid sense repetir tant codi
    def _crear_boto(self, parent, text, command):
        btn = tk.Button(parent, text=text, bg=self.btn_color, fg=self.text_color, font=("Arial", 9, "bold"),
                        relief="raised", cursor="hand2", command=command)
        btn.pack(pady=7, padx=20, fill="both", expand=True, ipady=5)
        return btn

    #funcio per obrir la aplicacio de mapes (google earth)
    def _obrir_kml(self, nom_fitxer):
        try:
            ruta_absoluta = os.path.abspath(nom_fitxer)
            sistema = platform.system()
            if sistema == "Windows":
                os.startfile(ruta_absoluta)
            elif sistema == "Darwin":
                subprocess.call(["open", ruta_absoluta])
            else:
                subprocess.call(["xdg-open", ruta_absoluta])
            self.escriure_consola("Arxiu " + nom_fitxer + " obert externament a Google Earth.")
        except Exception as e:
            self.escriure_consola("Error obrint Google Earth: " + str(e))

    #=========================================================================
    #MOTOR DE VALIDACIO DE FITXERS
    #=========================================================================
    #funcio que llegeix nomes la primera linia del txt per comprovar si es l'archiu correcte abans de carregar res
    def _obtenir_ruta_validada(self, nom_fitxer_defecte, paraula_clau, titol_operacio):
        directori = os.path.dirname(os.path.abspath(__file__))
        ruta = os.path.join(directori, nom_fitxer_defecte)
        es_valid = False

        if os.path.isfile(ruta) == True:
            try:
                f = open(ruta, 'r', encoding='utf-8')
                primera_linia = f.readline().upper()
                f.close()
                if paraula_clau in primera_linia:
                    es_valid = True
                elif paraula_clau == "AEROPORTS" and (
                        "ARRIVAL" not in primera_linia and "DEPARTURE" not in primera_linia and "TERMINALS" not in primera_linia):
                    es_valid = True
                elif paraula_clau == "TERMINALS" and ("TERMINAL" in primera_linia or "LEBL" in primera_linia):
                    es_valid = True
            except:
                pass

        if es_valid == False:
            self.escriure_consola("Fitxer no trobat o invàlid. Selecciona'l manualment...")
            ruta = filedialog.askopenfilename(title=titol_operacio, filetypes=[("Text files", "*.txt")])

            if len(ruta) == 0:
                self.escriure_consola("Operació cancel·lada.")
                return ""

            try:
                f = open(ruta, 'r', encoding='utf-8')
                primera_linia = f.readline().upper()
                f.close()

                if paraula_clau in primera_linia:
                    es_valid = True
                elif paraula_clau == "AEROPORTS" and (
                        "ARRIVAL" not in primera_linia and "DEPARTURE" not in primera_linia and "TERMINALS" not in primera_linia):
                    es_valid = True
                elif paraula_clau == "TERMINALS" and ("TERMINAL" in primera_linia or "LEBL" in primera_linia):
                    es_valid = True
            except:
                pass

            if es_valid == False:
                messagebox.showerror("Fitxer Incorrecte",
                                     "El fitxer seleccionat no és de tipus " + paraula_clau.lower() + ".")
                self.escriure_consola("ERROR: Fitxer rebutjat per format incorrecte.")
                return ""

        return ruta

    #=========================================================================
    #ACCIONS DE LA INTERFICIE: POP-UPS ELEGANTS
    #=========================================================================
    #fem servir aixo per obrir una pantalleta petita on introduir coses a ma
    def popup_afegir_aeroport(self):
        finestra = tk.Toplevel(self.root)
        finestra.title("Afegir Aeroport")
        finestra.geometry("300x250")
        finestra.configure(bg=self.bg_color)

        tk.Label(finestra, text="Codi ICAO (4 lletres):", bg=self.bg_color, fg=self.text_color,
                 font=("Arial", 9, "bold")).pack(pady=(15, 2))
        ent_code = tk.Entry(finestra, justify="center")
        ent_code.pack()

        tk.Label(finestra, text="Latitud (Ex: 41.29):", bg=self.bg_color, fg=self.text_color,
                 font=("Arial", 9, "bold")).pack(pady=(10, 2))
        ent_lat = tk.Entry(finestra, justify="center")
        ent_lat.pack()

        tk.Label(finestra, text="Longitud (Ex: 2.08):", bg=self.bg_color, fg=self.text_color,
                 font=("Arial", 9, "bold")).pack(pady=(10, 2))
        ent_lon = tk.Entry(finestra, justify="center")
        ent_lon.pack()

        def desar_aeroport():
            code = ent_code.get().strip().upper()
            try:
                lat = float(ent_lat.get())
                lon = float(ent_lon.get())
            except Exception:
                messagebox.showerror("Error", "La Latitud i Longitud han de ser decimals.", parent=finestra)
                return

            if len(code) != 4:
                messagebox.showerror("Error", "El codi ICAO ha de tenir 4 lletres.", parent=finestra)
                return

            nou_ap = Airport(code, lat, lon)
            SetSchengen(nou_ap)
            res = AddAirport(self.aeroports, nou_ap)

            if res == 0:
                self.escriure_consola("Alta manual: Aeroport " + code + " afegit.")
            else:
                self.escriure_consola("Avís: L'aeroport " + code + " ja existia.")
            finestra.destroy()

        tk.Button(finestra, text="Afegir a Memòria", bg=self.btn_color, fg=self.text_color, font=("Arial", 9, "bold"),
                  command=desar_aeroport).pack(pady=20)

    #pantalleta per demanar quin text de l'aeroport volem esborrar
    def popup_eliminar_aeroport(self):
        finestra = tk.Toplevel(self.root)
        finestra.title("Eliminar Aeroport")
        finestra.geometry("300x150")
        finestra.configure(bg=self.bg_color)

        tk.Label(finestra, text="Codi ICAO a eliminar:", bg=self.bg_color, fg=self.text_color,
                 font=("Arial", 9, "bold")).pack(pady=(20, 5))
        ent_code = tk.Entry(finestra, justify="center")
        ent_code.pack()

        def esborrar_aeroport():
            code = ent_code.get().strip().upper()
            if len(code) > 0:
                res = RemoveAirport(self.aeroports, code)
                if res == 0:
                    self.escriure_consola("Baixa manual: Aeroport " + code + " eliminat.")
                else:
                    self.escriure_consola("Error: Aeroport " + code + " no trobat.")
            finestra.destroy()

        tk.Button(finestra, text="Eliminar de Memòria", bg=self.btn_color, fg=self.text_color,
                  font=("Arial", 9, "bold"), command=esborrar_aeroport).pack(pady=20)

    #=========================================================================
    #ACCIONS DE COLUMNA 1: AEROPORTS
    #=========================================================================
    #buidem la llista abans de carregar per si l'usuari clica dos cops el boto
    def carregar_aeroports(self):
        ruta = self._obtenir_ruta_validada("Airports.txt", "AEROPORTS", "Carregar Aeroports")
        if len(ruta) == 0: return

        if len(self.aeroports) > 0:
            self.aeroports.clear()

        self.aeroports = LoadAirports(ruta)

        i = 0
        while i < len(self.aeroports):
            SetSchengen(self.aeroports[i])
            i = i + 1

        if len(self.aeroports) > 0:
            self.escriure_consola(str(len(self.aeroports)) + " aeroports carregats.")

    #protegim la UI: comprovem si la llista d'aeroports esta buida abans de fer l'exportacio per evitar que la interficie crashegi perque a vegades donava error
    def exportar_schengen_manual(self):
        #aixi protegim el codi evitant que de errors si cliques sense carregar res
        if len(self.aeroports) == 0:
            self.escriure_consola("ERROR: No hi ha aeroports per exportar.")
            return
        nom = filedialog.asksaveasfilename(defaultextension=".txt", title="Exportar Schengen")
        if len(nom) > 0:
            SaveSchengenAirports(self.aeroports, nom)
            self.escriure_consola("Arxiu Schengen desat: " + nom)

    #mes validacions preventives per evitar que peti el programa si no hi ha dades abans de fer el grafic
    def grafic_aeroports(self):
        #mes proteccions per evitar caigudes del programa si les dades no hi son
        if len(self.aeroports) > 0:
            self.mostrar_al_canvas(PlotAirports, self.aeroports)
        else:
            self.escriure_consola("ERROR: Falten carregar els aeroports.")

    #igual per aqui, validem perque el programa no tingui errors
    def mapa_aeroports(self):
        if len(self.aeroports) == 0:
            self.escriure_consola("ERROR: Falten carregar els aeroports.")
            return
        nom = "mapa_aeroports_temp.kml"
        MapAirports(self.aeroports, nom)
        self._obrir_kml(nom)

    #=========================================================================
    #ACCIONS DE COLUMNA 2: ARRIBADES
    #=========================================================================
    #buidem la llista de vols per si es vol carregar mes d'un cop
    def carregar_arribades(self):
        ruta = self._obtenir_ruta_validada("Arrivals.txt", "ARRIVAL", "Carregar Arribades")
        if len(ruta) == 0: return

        self.ruta_arrivals = ruta
        if len(self.vols) > 0:
            self.vols.clear()

        self.vols = LoadArrivals(ruta)
        if len(self.vols) > 0:
            self.escriure_consola(str(len(self.vols)) + " vols d'arribada carregats.")

    #cridem per guardar els vols mirant sempre que n'hi hagi primer
    def exportar_vols_manual(self):
        if len(self.vols) == 0:
            self.escriure_consola("ERROR: No hi ha vols per exportar.")
            return
        nom = filedialog.asksaveasfilename(defaultextension=".txt", title="Guardar vuelos")
        if len(nom) > 0:
            SaveFlights(self.vols, nom)
            self.escriure_consola("Vols desats: " + nom)

    #enviem a dibuixar comprovant que no doni errors per estar buit
    def grafic_hores(self):
        if len(self.vols) > 0:
            self.mostrar_al_canvas(PlotArrivals, self.vols)
        else:
            self.escriure_consola("ERROR: Falten carregar els vols d'arribada.")

    #enviem a la funcio per veure els millors(amb més vols)
    def grafic_aerolinies_top5(self):
        if len(self.vols) > 0:
            self.mostrar_al_canvas(PlotAirlines, self.vols, True)
        else:
            self.escriure_consola("ERROR: Falten carregar els vols d'arribada.")

    #aquesta si que l'obrim fora perque puguem veure-la tota enorme
    def grafic_aerolinies_todas(self):
        if len(self.vols) > 0:
            self.escriure_consola("Obrint gràfic complet d'aerolínies en finestra externa maximitzada...")
            plt.close('all')
            PlotAirlines(self.vols, False)
        else:
            self.escriure_consola("ERROR: Falten carregar els vols d'arribada.")

    #cal tenir els dos archius per ajuntar informacio de l'espai Schengen
    def grafic_schengen_vols(self):
        if len(self.aeroports) > 0 and len(self.vols) > 0:
            self.mostrar_al_canvas(PlotFlightsType, self.vols, self.aeroports)
        else:
            self.escriure_consola("ERROR: Cal carregar tant els aeroports com els vols d'arribada.")

    #aqui hem de tenir tambe l'archiu dels llocs per saber a quin mapa van
    def mapa_vols(self):
        if len(self.aeroports) == 0 or len(self.vols) == 0:
            self.escriure_consola("ERROR: Cal carregar tant els aeroports com els vols d'arribada.")
            return
        nom = "trajectes_temp.kml"
        MapFlights(self.vols, self.aeroports, nom)
        self._obrir_kml(nom)

    #funcio per fer nomes el mapa amb l'avio que ve de lluny
    def mapa_vols_llarga(self):
        if len(self.aeroports) == 0 or len(self.vols) == 0:
            self.escriure_consola("ERROR: Cal carregar tant els aeroports com els vols d'arribada.")
            return
        vols_llargs = LongDistanceArrivals(self.vols, self.aeroports)
        nom = "trajectes_llargs_temp.kml"
        MapFlights(vols_llargs, self.aeroports, nom)
        self._obrir_kml(nom)

    #funcio per obrir la pestanya neta amb el google vist desde adalt
    def obrir_visor_google(self):
        if len(self.aeroports) == 0 or len(self.vols) == 0:
            self.escriure_consola("ERROR: Carrega els aeroports i vols d'arribada primer per obrir el mapa natiu.")
            return
        from visor_mapes import VisorGoogleIntegrat
        from aircraft import LongDistanceArrivals
        vols_llargs = LongDistanceArrivals(self.vols, self.aeroports)
        VisorGoogleIntegrat(self.root, self.aeroports, self.vols, vols_llargs)
        self.escriure_consola("Obrint el Visor Satèl·lit Integrat en una nova finestra...")

    #=========================================================================
    #ACCIONS DE COLUMNA 3: SORTIDES I MAPES
    #=========================================================================
    #funcio important que carrega les sortides
    def carregar_sortides(self):
        ruta = self._obtenir_ruta_validada("Departures.txt", "DEPARTURE", "Carregar Sortides")
        if len(ruta) == 0: return

        #--- EL TRUC MAGIC ANTI-DUPLICATS ---
        #la funcio MergeMovements tractava els objectes originals, i si l'usuari clicava dos cops el boto de merge, la llista creixia infinitament amb dades adicionals (repetides)
        #estem super orgullosos d'haver-nos adonat d'aixo. El gran truc va ser recarregar el fitxer Arrivals.txt de zero abans de cada merge per netejar la memoria i que no s'acumulessin.
        if hasattr(self, 'ruta_arrivals') and self.ruta_arrivals != "":
            self.vols = LoadArrivals(self.ruta_arrivals)
        else:
            self.vols = LoadArrivals("Arrivals.txt")
        #------------------------------------

        if len(self.departures) > 0:
            self.departures.clear()

        self.departures = LoadDepartures(ruta)

        if len(self.vols) == 0:
            self.escriure_consola("Error: Carrega arribades primer.")
            return

        if len(self.merged_vols) > 0:
            self.merged_vols.clear()

        self.merged_vols, errors = MergeMovements(self.vols, self.departures)

        #=====================================================================
        #SOLUCIO ALS AVIONS NOCTURNS (Reparteix be el Schengen a les 00:00)
        #=====================================================================
        i = 0
        while i < len(self.merged_vols):
            if self.merged_vols[i].origin_airport == "" or self.merged_vols[i].origin_airport == " ":
                self.merged_vols[i].origin_airport = self.merged_vols[i].destination_airport
            i = i + 1
        #=====================================================================

        if len(errors) > 0:
            self.escriure_consola("--- S'han descartat " + str(len(errors)) + " avions per incongruència ---")
        self.escriure_consola("Merge finalitzat. " + str(len(self.merged_vols)) + " avions purs preparats.")

    #=========================================================================
    #ACCIONS DE COLUMNA 4: PORTES LEBL
    #=========================================================================
    #obrim el document de text per fer-ho servir a l'aplicacio
    def carregar_estructura(self):
        ruta = self._obtenir_ruta_validada("Terminals.txt", "TERMINALS", "Carregar LEBL")
        if len(ruta) == 0: return
        self.bcn = LoadAirportStructure(ruta)
        if self.bcn is not None:
            self.escriure_consola("Estructura LEBL carregada.")

    #cridem la busqueda que vam fer per els avions que nomes es queden de nit a bcn
    def assignar_nocturns(self):
        if self.bcn is not None and len(self.merged_vols) > 0:
            AssignNightGates(self.bcn, self.merged_vols)
            self.escriure_consola("Night Gates (00:00) assignades correctament.")
        else:
            self.escriure_consola("ERROR: Cal carregar l'estructura LEBL i fer el Merge de sortides primer.")

    #fem una busqueda ràpida previament perque no estigui buit abans de dibuixar a pantalla
    def mostrar_grafic_dia(self):
        if self.bcn is not None and len(self.merged_vols) > 0:
            self.mostrar_al_canvas(PlotDayOccupancy, self.bcn, self.merged_vols)
        else:
            self.escriure_consola("ERROR: Cal carregar l'estructura LEBL i fer el Merge de sortides primer.")

    #=========================================================================
    #EL SISTEMA DE PATCHES AMB SLIDER
    #=========================================================================
    #fem aixo per dibuixar les terminals i posar la boleta lliscant a sota on podem canviar l'hora
    def animacio_portes_slider(self):
        if self.bcn is None or len(self.merged_vols) == 0:
            self.escriure_consola("ERROR: Cal carregar l'estructura LEBL i fer el Merge de sortides primer.")
            return

        plt.close('all')
        fig, ax = plt.subplots()

        fig.subplots_adjust(left=0.0, bottom=0.0, right=1.0, top=1.0, wspace=0.2, hspace=0.2)

        try:
            manager = plt.get_current_fig_manager()
            manager.window.state('zoomed')
        except:
            pass

        #creem el component lliscant a sota de la figura interactiva i establim els limits de 0 a 23 amb un salt d'1
        ax_hora = plt.axes([0.15, 0.02, 0.7, 0.03])
        slider_hora = Slider(ax_hora, 'Hora (0-23)', 0, 23, valinit=0, valstep=1)

        def update(val):
            ax.clear()
            ax.axis('off')

            ax.set_xlim(0, 40)
            ax.set_ylim(-40, 24)

            hora_num = int(val)
            hora_str = str(hora_num)
            if len(hora_str) == 1:
                hora_str = "0" + hora_str
            hora_str = hora_str + ":00"

            ax.text(20, 22, "ESTAT DE LES PORTES A LES " + hora_str, fontsize=24, fontweight="bold", ha='center',
                    color='#1D3557')

            idx_t = 0
            while idx_t < len(self.bcn.terminals):
                term = self.bcn.terminals[idx_t]
                idx_ba = 0
                while idx_ba < len(term.boarding_areas):
                    b_area = term.boarding_areas[idx_ba]
                    idx_g = 0
                    while idx_g < len(b_area.gates):
                        b_area.gates[idx_g].occupied = False
                        b_area.gates[idx_g].aircraft_id = ""
                        idx_g = idx_g + 1
                    idx_ba = idx_ba + 1
                idx_t = idx_t + 1

            AssignNightGates(self.bcn, self.merged_vols)

            h_sim = 0
            while h_sim <= hora_num:
                h_str = str(h_sim)
                if len(h_str) == 1:
                    h_str = "0" + h_str
                AssignGatesAtTime(self.bcn, self.merged_vols, h_str + ":00")
                h_sim = h_sim + 1

            y_pos = 15
            i = 0
            while i < len(self.bcn.terminals):
                t = self.bcn.terminals[i]

                rect_t = patches.Rectangle((0.5, y_pos - 1.25), 38, 2.5, linewidth=2, edgecolor='#1D3557',
                                           facecolor='#D0D5DB')
                ax.add_patch(rect_t)
                ax.text(19.5, y_pos, "TERMINAL " + t.name, fontsize=16, fontweight='bold', ha='center', va='center',
                        color='#1D3557')

                y_pos = y_pos - 3.5

                j = 0
                while j < len(t.boarding_areas):
                    ba = t.boarding_areas[j]

                    nom_zona = ""
                    paraules = ba.name.split()
                    if len(paraules) > 0:
                        nom_zona = paraules[-1]
                    else:
                        nom_zona = ba.name

                    ax.text(1, y_pos - 0.5, "Zona " + nom_zona + "\n(" + ba.type + ")", fontsize=10, fontweight='bold',
                            color='#457B9D')

                    x_pos = 5
                    k = 0
                    while k < len(ba.gates):
                        g = ba.gates[k]

                        if g.occupied == True:
                            color_porta = '#E63946'
                        else:
                            color_porta = '#2A9D8F'

                        rect = patches.Rectangle((x_pos, y_pos - 1.2), 2.5, 1.6, linewidth=1, edgecolor='black',
                                                 facecolor=color_porta)
                        ax.add_patch(rect)

                        nom_porta = ""
                        parts_porta = g.name.split('G')
                        if len(parts_porta) > 1:
                            nom_porta = parts_porta[-1]
                        else:
                            nom_porta = g.name

                        if g.occupied == True:
                            ax.text(x_pos + 1.25, y_pos - 0.2, "G" + nom_porta, color='white', ha='center', va='center',
                                    fontsize=9, fontweight='bold')
                            ax.text(x_pos + 1.25, y_pos - 0.8, g.aircraft_id, color='white', ha='center', va='center',
                                    fontsize=8)
                        else:
                            ax.text(x_pos + 1.25, y_pos - 0.2, "G" + nom_porta, color='white', ha='center', va='center',
                                    fontsize=9, fontweight='bold')
                            ax.text(x_pos + 1.25, y_pos - 0.8, "Lliure", color='#DDDDDD', ha='center', va='center',
                                    fontsize=8)

                        x_pos = x_pos + 2.8

                        if x_pos > 36:
                            x_pos = 5
                            y_pos = y_pos - 2.0

                        k = k + 1

                    y_pos = y_pos - 2.4
                    j = j + 1

                y_pos = y_pos - 1
                i = i + 1

            fig.canvas.draw_idle()

        slider_hora.on_changed(update)
        update(0)

        fig.slider_hora = slider_hora
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = InterficieAeroports(root)
    #esmentem la trampa de posar el KeyboardInterrupt al final per sortir netament d'espera (que no surti error a pycharm)
    #a vegades la pantalleta negra es quedava encallada o crashejava si tancaves malament. Aixi ens ha funcionat millor.
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass