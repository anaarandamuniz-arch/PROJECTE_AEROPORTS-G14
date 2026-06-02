import os
import math
import matplotlib.pyplot as plt
from airport import LoadAirports, SetSchengen

#---------------------------------------------------------
#CLASSE AIRCRAFT I FUNCIONS DE CARREGA
#---------------------------------------------------------
#definim la classe per als avions posant les variables inicials com a textos buits
class Aircraft:
    def __init__(self, aircraft_id, airline_company, origin_airport, time_of_landing):
        self.aircraft_id = str(aircraft_id).strip()
        self.airline_company = str(airline_company).strip()
        self.origin_airport = str(origin_airport).strip().upper()
        self.time_of_landing = str(time_of_landing).strip()
        #afegim els camps nous de la versio 4 per preparar l'avio per a les sortides
        self.destination_airport = ""
        self.time_of_departure = ""

#funcio per carregar l'archiu d'arribades fent un recorrido linia a linia i tallant els trossos de text per guardar cada dada
def LoadArrivals(filename):
    aircrafts = []
    if os.path.isfile(filename):
        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            #assegurem que la linia no estigui buida perque no doni errors
            if len(line) > 0:
                #ignorem la primera linia que nomes te text informatiu de la capcalera
                if not line.upper().startswith("AIRCRAFT"):
                    parts = line.split()
                    if len(parts) >= 4:
                        a_id = parts[0]
                        orig = parts[1]
                        time = parts[2]
                        comp = parts[3]

                        te_dos_punts = False
                        k = 0
                        #comprovem si el format de l'hora es valid fent una busqueda dels dos punts
                        while k < len(time) and te_dos_punts == False:
                            if time[k] == ':':
                                te_dos_punts = True
                            k = k + 1

                        if te_dos_punts == True:
                            a = Aircraft(a_id, comp, orig, time)
                            aircrafts.append(a)
            i = i + 1
    return aircrafts

#nova funcio v4 per llegir les sortides, fem un bucle igual de facil pero ara guardem la destinacio en lloc de l'origen
def LoadDepartures(filename):
    aircrafts = []
    if os.path.isfile(filename):
        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if len(line) > 0:
                if not line.upper().startswith("AIRCRAFT"):
                    parts = line.split()
                    if len(parts) >= 4:
                        a_id = parts[0]
                        dest = parts[1]
                        time = parts[2]
                        comp = parts[3]

                        te_dos_punts = False
                        k = 0
                        while k < len(time) and te_dos_punts == False:
                            if time[k] == ':':
                                te_dos_punts = True
                            k = k + 1

                        if te_dos_punts == True:
                            #creem l'avio buit d'arribades i l'omplim amb les dades de les sortides
                            a = Aircraft(a_id, comp, "", "")
                            a.destination_airport = dest.upper()
                            a.time_of_departure = time
                            aircrafts.append(a)
            i = i + 1
    return aircrafts

#---------------------------------------------------------
#FUNCIO MERGEMOVEMENTS I NOCTURNS
#---------------------------------------------------------
#nova funcio v4 per ajuntar les arribades i sortides fent un doble bucle de busqueda
def MergeMovements(arrivals, departures):
    merged = []
    errors = []

    #primer copiem totes les arribades a la llista nova fent un bucle rapid
    i = 0
    while i < len(arrivals):
        merged.append(arrivals[i])
        i = i + 1

    #ara fem un altre bucle per les sortides per veure quines ajuntem o quines borrem
    j = 0
    while j < len(departures):
        dep = departures[j]
        k = 0
        trobat = False
        es_error = False

        while k < len(merged) and trobat == False:
            #busquem l'avio que tingui la mateixa matricula i que encara no tingui sortida posada
            if merged[k].aircraft_id == dep.aircraft_id and merged[k].time_of_departure == "":
                arr_parts = merged[k].time_of_landing.split(':')
                dep_parts = dep.time_of_departure.split(':')

                if len(arr_parts) == 2 and len(dep_parts) == 2:
                    minuts_arr = (int(arr_parts[0]) * 60) + int(arr_parts[1])
                    minuts_dep = (int(dep_parts[0]) * 60) + int(dep_parts[1])

                    #REGLA ESTRICTA: l'hora de sortida HA DE SER mes tard que l'arribada
                    if minuts_arr < minuts_dep:
                        merged[k].destination_airport = dep.destination_airport
                        merged[k].time_of_departure = dep.time_of_departure
                        trobat = True
                    else:
                        #ERROR DIRECTE: si surt abans d'arribar, el borrem per sempre
                        #aqui solucionem l'error del viatge en el temps: algunes dades del txt tenien incongruencies i l'avio sortia hores abans d'arribar.
                        es_error = True
                        trobat = True
                        errors.append(dep.aircraft_id)
                        del merged[k]

            #nomes passem al seguent si no l'hem trobat encara
            if trobat == False:
                k = k + 1

        #si no em trobat cap arribada d'abans i no es un error, vol dir que l'avio ja era alla de nit
        if trobat == False and es_error == False:
            merged.append(dep)

        j = j + 1

    return merged, errors

#nova funcio v4 que fa un recorrido per tornar nomes els avions que van passar la nit a l'aeroport
def NightAircraft(aircrafts):
    night = []
    i = 0
    while i < len(aircrafts):
        a = aircrafts[i]
        #si te sortida pero no te arribada, aixo vol dir que ja hi era a la nit
        #aqui vam arreglar el gran bug on els avions nocturns (els que ja eren a l'aeroport a les 00:00) desapareixien perque no tenien hora d'arribada
        if a.time_of_landing == "" and a.time_of_departure != "":
            night.append(a)
        i = i + 1
    return night

#---------------------------------------------------------
#FUNCIONS DE GRAFICS I EXPORTACIO
#---------------------------------------------------------
#funcio per dibuixar el grafic d'hores d'arribada tallant una mica el text per treure els minuts i endreçant els numeros de menor a major
def PlotArrivals(aircrafts):
    if len(aircrafts) == 0:
        print("Error: Llista de vols buida.")
    else:
        hores = []
        num_vols = []
        i = 0
        while i < len(aircrafts):
            vol = aircrafts[i]
            hora_extreta = ""
            j = 0
            while j < len(vol.time_of_landing) and vol.time_of_landing[j] != ':':
                hora_extreta = hora_extreta + vol.time_of_landing[j]
                j = j + 1
            k = 0
            trobat = False
            while k < len(hores) and trobat == False:
                if hores[k] == hora_extreta:
                    trobat = True
                    num_vols[k] = num_vols[k] + 1
                k = k + 1
            if trobat == False:
                hores.append(hora_extreta)
                num_vols.append(1)
            i = i + 1
        n = len(hores)
        x = 0
        #fem un petit bucle doble per endreçar les hores trobades
        while x < n - 1:
            y = 0
            while y < n - x - 1:
                if int(hores[y]) > int(hores[y + 1]):
                    temp_h = hores[y]
                    hores[y] = hores[y + 1]
                    hores[y + 1] = temp_h
                    temp_v = num_vols[y]
                    num_vols[y] = num_vols[y + 1]
                    num_vols[y + 1] = temp_v
                y = y + 1
            x = x + 1
        plt.figure(figsize=(10, 5))
        plt.bar(hores, num_vols, color='skyblue')
        plt.xlabel("Hora del dia")
        plt.ylabel("Nombre d'arribades")
        plt.title("Freqüència d'arribades per hora")
        plt.show()

#funcio per separar vols Schengen o no Schengen fent una busqueda a la llista d'aeroports per veure d'on ve cadascun
def PlotFlightsType(aircrafts, airports_list=None):
    if len(aircrafts) == 0:
        print("Error: Llista de vols buida.")
    else:
        sch_count = 0
        no_sch_count = 0
        i = 0
        while i < len(aircrafts):
            vol = aircrafts[i]
            j = 0
            trobat = False
            es_schengen = False
            while j < len(airports_list) and trobat == False:
                if airports_list[j].code == vol.origin_airport:
                    trobat = True
                    es_schengen = airports_list[j].Schengen
                j = j + 1
            if trobat == True and es_schengen == True:
                sch_count = sch_count + 1
            else:
                no_sch_count = no_sch_count + 1
            i = i + 1
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(["Vols"], [sch_count], label="Schengen", color="#2ca02c")
        ax.bar(["Vols"], [no_sch_count], bottom=[sch_count], label="No Schengen", color="#d62728")
        ax.set_ylabel("Nombre de vols")
        ax.legend()
        plt.show()

#formula matematica de haversine que fa uns calculs per dir-nos els kilometres entre dos punts
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

#funcio per descartar avions fent un bucle que mira la distancia i guarda nomes els que venen de mes de 2000 km
def LongDistanceArrivals(aircrafts, airports_list=None):
    llarga_distancia = []
    if airports_list is None:
        airports_list = LoadAirports("Airports.txt")
    lebl_lat = 41.297445
    lebl_lon = 2.0832941
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
        if trobat == True and ap_origen is not None:
            dist = haversine(lebl_lat, lebl_lon, ap_origen.lat, ap_origen.lon)
            if dist > 2000:
                llarga_distancia.append(vol)
        i = i + 1
    return llarga_distancia

#funcio per guardar tota la llista de vols en un fitxer de text obrint i escrivint linia a linia molt rapidament
def SaveFlights(aircrafts, filename):
    resultat = -1
    if len(aircrafts) > 0:
        f = open(filename, 'w', encoding='utf-8')
        f.write("AIRCRAFT ORIGIN ARRIVAL AIRLINE\n")
        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]
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
            f.write(a_id + " " + orig + " " + time + " " + comp + "\n")
            i = i + 1
        f.close()
        resultat = 0
    return resultat

#funcio per fer el grafic de les aerolinies que fa un recompte manual amb un bucle
def PlotAirlines(aircrafts, nomes_top5=False):
    import matplotlib.pyplot as plt
    if len(aircrafts) == 0:
        print("Error: Llista de vols buida.")
    else:
        cies_uniques = []
        recompte = []
        i = 0
        while i < len(aircrafts):
            cia = aircrafts[i].airline_company
            j = 0
            trobat = False
            while j < len(cies_uniques) and trobat == False:
                if cies_uniques[j] == cia:
                    trobat = True
                    recompte[j] = recompte[j] + 1
                j = j + 1
            if trobat == False:
                cies_uniques.append(cia)
                recompte.append(1)
            i = i + 1

        x = 0
        while x < len(recompte) - 1:
            y = 0
            while y < len(recompte) - x - 1:
                if recompte[y] < recompte[y + 1]:
                    temp_r = recompte[y]
                    recompte[y] = recompte[y + 1]
                    recompte[y + 1] = temp_r

                    temp_c = cies_uniques[y]
                    cies_uniques[y] = cies_uniques[y + 1]
                    cies_uniques[y + 1] = temp_c
                y = y + 1
            x = x + 1

        if nomes_top5 == True and len(cies_uniques) > 5:
            cies_top5 = []
            rec_top5 = []
            k = 0
            while k < 5:
                cies_top5.append(cies_uniques[k])
                rec_top5.append(recompte[k])
                k = k + 1
            cies_uniques = cies_top5
            recompte = rec_top5

        plt.figure(figsize=(10, 5))
        plt.bar(cies_uniques, recompte, color='#4A90E2')

        if nomes_top5 == True:
            plt.xticks(rotation=45, fontsize=10)
            plt.title("Top 5 Aerolínies")
        else:
            plt.xticks(rotation=90, fontsize=6)
            plt.title("Totes les Aerolínies")

        plt.xlabel("Aerolínia")
        plt.ylabel("Nombre de vols")
        plt.tight_layout()

        #--- EL TRUC DE LA PANTALLA COMPLETA ---
        #aqui ens va costar molt adonar-nos que haviem de posar la finestra en zoomed perque el grafic de totes les aerolinies fos llegible
        if nomes_top5 == False:
            manager = plt.get_current_fig_manager()
            try:
                manager.window.state('zoomed')
            except:
                pass

        plt.show()

#funcio per crear l'archiu per al mapa escrivint textos amb etiquetes estranyes que necessita el Google Earth
def MapFlights(aircrafts, airports_list=None, filename="mapa_vols.kml"):
    if len(aircrafts) > 0:
        lebl_lat = 41.297445
        lebl_lon = 2.0832941
        f = open(filename, 'w', encoding='utf-8')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n')
        f.write('<Style id="schLine"><LineStyle><color>ff00ff00</color><width>2</width></LineStyle></Style>\n')
        f.write('<Style id="nonschLine"><LineStyle><color>ff0000ff</color><width>2</width></LineStyle></Style>\n')
        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]
            j = 0
            trobat = False
            ap_origen = None
            while j < len(airports_list) and trobat == False:
                if airports_list[j].code == a.origin_airport:
                    trobat = True
                    ap_origen = airports_list[j]
                j = j + 1
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