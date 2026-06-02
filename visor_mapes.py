# ==============================================================================
# MÒDUL AVANÇAT: Visor de Mapes Integrat (Estil Google Earth)
# ==============================================================================
import tkinter as tk
import tkintermapview


class VisorGoogleIntegrat(tk.Toplevel):
    def __init__(self, master, aeroports, vols, vols_llargs):
        super().__init__(master)
        self.title("🌍 Visor de Satèl·lit Integrat (Google Earth Engine)")

        # --- TRUC PER OBRIR A PANTALLA COMPLETA ---
        self.geometry("1100x750")
        try:
            self.state('zoomed')  # A Windows ho fa pantalla completa automàticament
        except:
            self.attributes('-zoomed', True)  # Alternativa per a altres sistemes

        self.configure(bg="#2C2C2E")

        self.aeroports = aeroports
        self.vols = vols
        self.vols_llargs = vols_llargs

        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        header = tk.Label(self, text="SISTEMA DE GEOLOCALITZACIÓ EN TEMPS REAL",
                          font=("Arial", 16, "bold"), bg="#1A1A1C", fg="#FFFFFF", pady=15)
        header.grid(row=0, column=0, sticky="ew")

        self.mapa = tkintermapview.TkinterMapView(self, corner_radius=0)
        self.mapa.grid(row=1, column=0, sticky="nsew")

        self.mapa.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)

        self.lebl_coords = (41.297445, 2.0832941)
        self.mapa.set_position(self.lebl_coords[0], self.lebl_coords[1])
        self.mapa.set_zoom(4)

        frame_controls = tk.Frame(self, bg="#2C2C2E", pady=10)
        frame_controls.grid(row=2, column=0, sticky="ew")

        btn_estil = {"font": ("Arial", 10, "bold"), "bg": "#4A90E2", "fg": "white", "cursor": "hand2"}

        tk.Button(frame_controls, text="📍 Aeroports", command=self.dibuixar_aeroports, **btn_estil).pack(side=tk.LEFT,
                                                                                                         padx=15)
        tk.Button(frame_controls, text="✈️ Totes les Rutes", command=self.dibuixar_rutes_totes, **btn_estil).pack(
            side=tk.LEFT, padx=15)
        tk.Button(frame_controls, text="🚀 Rutes Llargues (>2000km)", command=self.dibuixar_rutes_llargues,
                  **btn_estil).pack(side=tk.LEFT, padx=15)
        tk.Button(frame_controls, text="🗑️ Netejar Mapa", command=self.netejar_mapa, **btn_estil).pack(side=tk.RIGHT,
                                                                                                       padx=15)

    def dibuixar_aeroports(self):
        self.mapa.delete_all_marker()
        for ap in self.aeroports:
            if ap.code:
                color = "#2ca02c" if getattr(ap, 'Schengen', False) else "#d62728"
                self.mapa.set_marker(ap.lat, ap.lon, text=ap.code, font=("Arial", 8), marker_color_circle=color,
                                     marker_color_outside=color)

    def dibuixar_rutes_totes(self):
        self._trazar_rutes(self.vols)

    def dibuixar_rutes_llargues(self):
        self._trazar_rutes(self.vols_llargs)

    def _trazar_rutes(self, llista_de_vols):
        self.mapa.delete_all_path()
        dicc_aeroports = {ap.code: ap for ap in self.aeroports if ap.code}

        for vol in llista_de_vols:
            ap_origen = dicc_aeroports.get(vol.origin_airport)
            if ap_origen:
                color = "#2ca02c" if getattr(ap_origen, 'Schengen', False) else "#d62728"
                self.mapa.set_path([(ap_origen.lat, ap_origen.lon), self.lebl_coords], color=color, width=2)

    def netejar_mapa(self):
        self.mapa.delete_all_marker()
        self.mapa.delete_all_path()