import os
import math
import matplotlib.pyplot as plt
from airport import LoadAirports, SetSchengen


#definim la classe per als avions
class Aircraft:
    def __init__(self, aircraft_id, airline_company, origin_airport, time_of_landing):
        self.aircraft_id = str(aircraft_id).strip()
        self.airline_company = str(airline_company).strip()
        self.origin_airport = str(origin_airport).strip().upper()
        self.time_of_landing = str(time_of_landing).strip()


#funció per carregar l'arxiu d'arribades
def LoadArrivals(filename):
    aircrafts = []

    #comprovem si el fitxer existeix, si no, tornem una llista buida
    if os.path.isfile(filename):

        f = open(filename, 'r', encoding='utf-8') #obre l'arxiu
        lines = f.readlines()
        f.close()

        #bucle per recórrer les línies
        i = 0
        while i < len(lines):
            line = lines[
                i].strip()  #aqui utilitzem el .strip, una eina molt útil per eliminar els salts de línia, és a dir, elimina la terminologia que té el compilador (suposo) per determinar el salt de línia, per tal que no s'agafi aquesta terminologia com a dada.

            #validem que les linies no estiguin buides ni siguin la capçalera de l'arxiu arrivals
            if len(line) > 0:
                if not line.upper().startswith("AIRCRAFT"):  #aquesta és una dreçera que ens permet "saltar-nos" la primera línia de les dades del fitxer arrivals que no és cap dada
                    parts = line.split()

                    #primer ens assegurem que hi ha 4 columnes d'informació:
                    if len(parts) >= 4:

                        #assignem les parts a les 4 variables:
                        a_id = parts[0]
                        orig = parts[1]
                        time = parts[2]
                        comp = parts[3]

                        #aqui validem el format d'hora buscant els dos punts (':')
                        te_dos_punts = False
                        k = 0
                        while k < len(time) and te_dos_punts == False:
                            if time[k] == ':':
                                te_dos_punts = True
                            k = k + 1

                        #si ha trobat els ':' a l'hora, creem l'avió
                        #si la línia era defectuosa o no tenia ':', senzillament no entra aquí i salta a la següent línia
                        if te_dos_punts == True:
                            a = Aircraft(a_id, comp, orig, time)
                            aircrafts.append(a)

            i = i + 1

    return aircrafts


#funció per dibuixar el grafic d'hores d'arribada
def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        print("Error: Llista de vols buida.")
    else:
        #creem dues llistes una per guardar les hores que anem trobant i una altra per comptar quants vols hi ha a cada hora
        hores = []
        num_vols = []

        #anem mirant cada vol un per un
        i = 0
        while i < len(aircrafts):
            vol = aircrafts[i]
            hora_extreta = ""
            j = 0
            while j < len(vol.time_of_landing) and vol.time_of_landing[j] != ':':
                hora_extreta = hora_extreta + vol.time_of_landing[j]
                j = j + 1

            #mirem si aquesta hora ja la tenim guardada a la nostra llista
            k = 0
            trobat = False
            while k < len(hores) and trobat == False:
                if hores[k] == hora_extreta:
                    trobat = True
                    #si l'hora ja hi era, li sumem 1 vol més al comptador
                    num_vols[k] = num_vols[k] + 1
                k = k + 1

            #si no l'hem trobat, és una hora nova per tant l'afegim i diem que de moment hi ha 1 vol
            if trobat == False:
                hores.append(hora_extreta)
                num_vols.append(1)

            i = i + 1

        #endrecem les hores de la més petita a la més gran (00, 01, 02...), si no fessim això, al gràfic sortiran les hores barrejades tal com les anem llegint del fitxer de text
        n = len(hores)
        x = 0
        while x < n - 1:
            y = 0
            while y < n - x - 1:
                if int(hores[y]) > int(hores[y + 1]):
                    #això serivrà per moure l'hora de posició
                    temp_h = hores[y]
                    hores[y] = hores[y + 1]
                    hores[y + 1] = temp_h

                    #hem de fer el mateix amb el número de vols, i no, les hores i els vols es desquadren i el gràfic estaria malament.
                    temp_v = num_vols[y]
                    num_vols[y] = num_vols[y + 1]
                    num_vols[y + 1] = temp_v
                y = y + 1
            x = x + 1

        #ara pintem el gràfic de barres
        plt.figure(figsize=(10, 5))
        plt.bar(hores, num_vols, color='skyblue')
        plt.xlabel("Hora del dia")
        plt.ylabel("Nombre d'arribades")
        plt.title("Freqüència d'arribades per hora")
        plt.show()


#funció per separar vols Schengen o no Schengen buscant l'aeroport origen a la llista
def PlotFlightsType(aircrafts, airports_list=None):
    if len(aircrafts) == 0:
        print("Error: Llista de vols buida.")
    else:
        sch_count = 0
        no_sch_count = 0

        #recorrem tots els vols
        i = 0
        while i < len(aircrafts):
            vol = aircrafts[i]

            #per a cada vol, hem de buscar el seu aeroport a la llista
            j = 0
            trobat = False
            es_schengen = False

            while j < len(airports_list) and trobat == False:
                if airports_list[j].code == vol.origin_airport:
                    trobat = True
                    es_schengen = airports_list[j].Schengen
                j = j + 1

            #actualitzem el comptador segons si l'hem trobat i era Schengen
            if trobat == True and es_schengen == True:
                sch_count = sch_count + 1
            else:
                no_sch_count = no_sch_count + 1

            i = i + 1

        #codi de matplotlib per mostrar gràfic de barres apilades
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Vols"], [sch_count], label="Schengen", color="#2ca02c")
        ax.bar(["Vols"], [no_sch_count], bottom=[sch_count], label="No Schengen", color="#d62728")
        ax.set_ylabel("Nombre de vols")
        ax.legend()
        plt.show()


#fórmula de haversine (annex 2)
def haversine(lat1, lon1, lat2, lon2):

    R = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


#funció per filtrar els vols de llarga distància
def LongDistanceArrivals(aircrafts, airports_list=None):
    llarga_distancia = []

    if airports_list is None:
        airports_list = LoadAirports("Airports.txt")

    #coordenades base per defecte (LEBL)
    lebl_lat = 41.297445
    lebl_lon = 2.0832941

    #recorrem els vols
    i = 0
    while i < len(aircrafts):
        vol = aircrafts[i]

        j = 0
        trobat = False
        ap_origen = None

        while j < len(airports_list) and trobat == False:
            if airports_list[j].code == vol.origin_airport:
                trobat = True
                ap_origen = airports_list[j]
            j = j + 1

        #si hem trobat l'aeroport d'origen, calculem la distància amb Haversine
        if trobat == True and ap_origen is not None:
            dist = haversine(lebl_lat, lebl_lon, ap_origen.lat, ap_origen.lon)
            #si supera els 2000km el guardem
            if dist > 2000:
                llarga_distancia.append(vol)

        i = i + 1

    return llarga_distancia


#funció per guardar els vols en un fitxer de text
def SaveFlights(aircrafts, filename):
    #si la llista està buida, retornem error (-1)
    resultat = -1

    if len(aircrafts) > 0:
        #obrim el fitxer en mode escriptura
        f = open(filename, 'w', encoding='utf-8')
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n") #\n és per canviar de línia (enter)

        #recorrem la llista de vols un a un
        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]

            #validem manualment que els camps no estiguin buits, si ho estan, hi posem dues cometes simples ''
            if len(a.aircraft_id) > 0:
                a_id = a.aircraft_id
            else:
                a_id = "''"

            if len(a.origin_airport) > 0:
                orig = a.origin_airport
            else:
                orig = "''"

            if len(a.time_of_landing) > 0:
                time = a.time_of_landing
            else:
                time = "''"

            if len(a.airline_company) > 0:
                comp = a.airline_company
            else:
                comp = "''"

            #escrivim la línia amb la informació que tenim
            f.write(a_id + " " + orig + " " + time + " " + comp + "\n")
            i = i + 1

        f.close()
        resultat = 0

    return resultat


#funció per fer el gràfic de les aerolínie
def PlotAirlines(aircrafts):
    if len(aircrafts) == 0:
        print("Error: Llista de vols buida.")
    else:
        #creem dues llistes
        cies_uniques = []
        recompte = []

        #recórrem tots els vols
        i = 0
        while i < len(aircrafts):
            cia = aircrafts[i].airline_company

            #bucle secundari per veure si l'aerolínia està a la nostra llista
            j = 0
            trobat = False
            while j < len(cies_uniques) and trobat == False:
                if cies_uniques[j] == cia:
                    trobat = True
                    #si hi és, li sumem 1 al recompte
                    recompte[j] = recompte[j] + 1
                j = j + 1

            #si no hi fos, l'afegim com a nova i comptem 1
            if trobat == False:
                cies_uniques.append(cia)
                recompte.append(1)

            i = i + 1

        plt.figure(figsize=(12, 6))
        plt.bar(cies_uniques, recompte, color='coral')
        plt.xticks(rotation=90)
        plt.xlabel("Aerolínia")
        plt.ylabel("Nombre de vols")
        plt.title("Arribades per Aerolínia")
        plt.tight_layout()
        plt.show()


#funció per crear l'arxiu del mapa de vols
def MapFlights(aircrafts, airports_list=None, filename="mapa_vols.kml"):
    if len(aircrafts) > 0:
        #coordenades fixes del Prat
        lebl_lat = 41.297445
        lebl_lon = 2.0832941

        f = open(filename, 'w', encoding='utf-8')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')

        #color verd per Schengen i vermell per no Schengen
        f.write('<Style id="schLine"><LineStyle><color>ff00ff00</color><width>2</width></LineStyle></Style>\n')
        f.write('<Style id="nonschLine"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle></Style>\n')

        #bucle principal de vols
        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]

            #bucle secundari per trobar l'aeroport origen a la llista d'aeroports
            j = 0
            trobat = False
            ap_origen = None
            while j < len(airports_list) and trobat == False:
                if airports_list[j].code == a.origin_airport:
                    trobat = True
                    ap_origen = airports_list[j]
                j = j + 1

            #sii hem trobat l'aeroport, posem la línia al mapa
            if trobat == True and ap_origen is not None:
                es_schengen = ap_origen.Schengen
                if es_schengen == True:
                    style = "#schLine"
                else:
                    style = "#nonschLine"

                f.write('<Placemark>\n')
                f.write('<name>' + a.aircraft_id + ' (' + a.origin_airport + '-LEBL)</name>\n')
                f.write('<styleUrl>' + style + '</styleUrl>\n')
                f.write('<LineString><coordinates>\n')
                f.write(str(ap_origen.lon) + ',' + str(ap_origen.lat) + ',0\n')
                f.write(str(lebl_lon) + ',' + str(lebl_lat) + ',0\n')
                f.write('</coordinates></LineString>\n')
                f.write('</Placemark>\n')

            i = i + 1

        f.write('</Document>\n</kml>\n')
        f.close()