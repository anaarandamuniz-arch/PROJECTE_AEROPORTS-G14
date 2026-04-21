from airport import Airport, SetSchengen, PlotAirports, MapAirports

def crear_exemple():
    l = []
    l.append(Airport("LEBL", 41.297445, 2.0832941))
    l.append(Airport("EGLL", 51.470020, -0.454295))
    l.append(Airport("LFPG", 49.009690, 2.547925))
    l.append(Airport("KJFK", 40.641311, -73.778139))
    l.append(Airport("LEMD", 40.472024, -3.560862))
    for a in l:
        SetSchengen(a)
    return l

if __name__ == "__main__":
    aeroports = crear_exemple()
    print("Mostrant gràfic...")
    PlotAirports(aeroports)
    print("Generant KML...")
    MapAirports(aeroports, nom_fitxer="mapa_aeroports_exemple.kml")
    print("Acabat. Obre 'mapa_aeroports_exemple.kml' amb Google Earth.")