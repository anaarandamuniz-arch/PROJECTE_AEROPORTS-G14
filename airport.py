#importem les llibreries necessàries
import os
import math
import matplotlib.pyplot as plt


#definim la classe Airport
class Airport:
    def __init__(self, code, lat, lon):
        #comprovem si el codi és nul (code is none) i li assignem un text buit si ho és
        if code is None:
            code = ""
        #assignem els valors a les variable, també traiem el \n (els canvis de linea) amb el .strip i posant-ho en majúscules amb el .upper()
        self.code = str(code).strip().upper()
        #convertim latitud i longitud a nombres decimals
        self.lat = float(lat)
        self.lon = float(lon)
        self.Schengen = False


#funció per determinar si el codi pertany a l'espai Schengen
def IsSchengenAirport(code):
    _SCHENGEN_PREFIXES = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
        'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    #creem la variable booleana que retornarem al final
    trobat = False

    #mirem que el codi no estigui buit abans de fer res
    if code:
        #netejem el codi rebut amb el .strip com he dit abans i posem amb majuscules el codi amb el .upper
        c = str(code).strip().upper()

        #només busquem si el codi té 2 lletres o més
        if len(c) >= 2:
            prefix = c[0] + c[1]

            #fem una cerca per veure si el prefix està a la llista
            i = 0
            #el bucle s'atura si arribem al final de la llista o si ja l'hem trobat
            while i < len(_SCHENGEN_PREFIXES) and trobat == False:
                #si la posició actual coincideix amb el prefix que busquem incrementem l'índex per mirar la següent posició
                if _SCHENGEN_PREFIXES[i] == prefix:
                    trobat = True
                i = i + 1

    return trobat


#funció per donar  l'atribut Schengen d'un aeroport
def SetSchengen(aeroport):
    #només fem el procés si l'aeroport no és nul
    if aeroport is not None:
        #cridem la funció anterior i li donem el resultat a l'atribut
        aeroport.Schengen = IsSchengenAirport(aeroport.code)


#funció per imprimir les dades d'un aeroport
def PrintAirport(aeroport):
    #mirem si l'aeroport existeix
    if aeroport is None:
        print("Aeroport buit")
    else:
        #imprimim línia a línia cadascun dels seus atributs
        print("Codi ICAO:", aeroport.code)
        print("Latitud: {:.6f}".format(aeroport.lat))
        print("Longitud: {:.6f}".format(aeroport.lon))
        print("Schengen:", aeroport.Schengen)


def _dms_str_a_decimal(dms_str):
    if not dms_str or len(dms_str) < 2:
        raise ValueError("Format DMS invàlid")
    hemi = dms_str[0].upper()
    nums = dms_str[1:]
    if len(nums) == 6:
        deg = int(nums[0:2])
        minu = int(nums[2:4])
        sec = int(nums[4:6])
    else:
        deg = int(nums[0:3])
        minu = int(nums[3:5])
        sec = int(nums[5:7])
    decimal = deg + minu / 60.0 + sec / 3600.0
    if hemi == 'S' or hemi == 'W':
        decimal = -decimal
    return decimal


def _decimal_a_dms_lat(value):
    hemi = 'N' if value >= 0 else 'S'
    v = abs(value)
    deg = int(math.floor(v))
    rem = (v - deg) * 60.0
    minu = int(math.floor(rem))
    sec = int(round((rem - minu) * 60.0))
    if sec == 60:
        sec = 0
        minu += 1
    if minu == 60:
        minu = 0
        deg += 1
    return "{}{:02d}{:02d}{:02d}".format(hemi, deg, minu, sec)


def _decimal_a_dms_lon(value):
    hemi = 'E' if value >= 0 else 'W'
    v = abs(value)
    deg = int(math.floor(v))
    rem = (v - deg) * 60.0
    minu = int(math.floor(rem))
    sec = int(round((rem - minu) * 60.0))
    if sec == 60:
        sec = 0
        minu += 1
    if minu == 60:
        minu = 0
        deg += 1
    return "{}{:03d}{:02d}{:02d}".format(hemi, deg, minu, sec)


#funció per carregar els aeroports des del fitxer de text
def LoadAirports(filename):
    #creem una llista buida on guardarem els aeroports
    aeroports = []

    #comprovem si l'arxiu existeix a l'ordinador. Si ho fa, entrem a llegir-lo.
    if os.path.isfile(filename):
        #obrim l'arxiu  illegim les línies
        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        #fe, un recorregut  línia per línia
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            #només processem la línia si no està buida i no és la capçalera
            if len(line) > 0:
                up = line.upper()
                #ignorem la línia si comença per CODE o ICAO
                if not (up.startswith("CODE ") or up.startswith("ICAO ")):
                    #separem els elements de la línia per espais
                    parts = line.split()
                    #hi han d'haver-hi almenys 3 elements (Codi, Lat, Lon)
                    if len(parts) >= 3:
                        code = parts[0].strip().upper()
                        lat_str = parts[1].strip()
                        lon_str = parts[2].strip()

                        #intentem fer la conversió matemàtica
                        try:
                            lat = _dms_str_a_decimal(lat_str)
                            lon = _dms_str_a_decimal(lon_str)
                            # creem el nou objecte Airport
                            a = Airport(code, lat, lon)
                            #i l'afegim al vector d'aeroports
                            aeroports.append(a)
                        except Exception:
                            #si hi ha un error de format, simplement saltem l'error i continuem amb la seguent linia
                            pass
            i = i + 1

    return aeroports


#funció per afegir un nou aeroport si no existeix prèviament
def AddAirport(aeroports, aeroport):
    #variable de control per al return final
    resultat = -1

    #només fem coses si l'aeroport no és nul
    if aeroport is not None:
        #accedim a l'atribut del nou aeroport directament amb el punt
        code = aeroport.code

        #cerca  per comprovar si ja existeix a la llista
        i = 0
        trobat = False
        while i < len(aeroports) and trobat == False:
            #llegim el codi de cada aeroport de la llista directament
            if aeroports[i].code == code:
                trobat = True
            i = i + 1

        #si l'hem trobat, el resultat serà 1 (ja existeix)
        if trobat == True:
            resultat = 1
        #si no, l'afegim al final de la llista i el resultat serà 0 (èxit)
        else:
            aeroports.append(aeroport)
            resultat = 0

    return resultat


#funció per esborrar un aeroport cercant el seu codi
def RemoveAirport(aeroports, code):
    resultat = -1

    #només executem si el codi no està buit
    if code:
        c = str(code).strip().upper()  #fem servir el .strip i el .upper com abans
        i = 0
        trobat = False

        #recorregut per buscar l'element a eliminar
        while i < len(aeroports) and trobat == False:
            if getattr(aeroports[i], "code", "").upper() == c:
                #esborrem l'element a la posició 'i'
                del aeroports[i]
                trobat = True
            else:
                i = i + 1

        #si l'hem esborrat el resultat és 0
        if trobat == True:
            resultat = 0

    return resultat


#funció per dibuixar el gràfic de barres d'aeroports
def PlotAirports(aeroports):
    schengen = 0
    no_schengen = 0

    #recorrem tots els aeroports comptant quants són de cada tipus
    i = 0
    while i < len(aeroports):
        if aeroports[i].Schengen == True:
            schengen = schengen + 1
        else:
            no_schengen = no_schengen + 1
        i = i + 1

    labels = ["Aeroports"]
    sch_vals = [schengen]
    no_vals = [no_schengen]

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(labels, sch_vals, label="Schengen", color="#2ca02c")
    ax.bar(labels, no_vals, bottom=sch_vals, label="No Schengen", color="#d62728")
    ax.set_ylabel("Nombre d'aeroports")
    ax.set_title("Comparació d'aeroports Schengen i no Schengen")
    ax.legend()
    plt.tight_layout()
    plt.show()


#funció per mapear al Google Earth
def MapAirports(aeroports, nom_fitxer="mapa_aeroports.kml"):
    kml_lines = []
    kml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    kml_lines.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_lines.append('<Document>')
    kml_lines.append('<name>Mapa Aeroports</name>')

    #fefinim els estils dels punts (verd = Schengen, vermell = No Schengen)
    kml_lines.append(
        '<Style id="schengenStyle"><IconStyle><color>ff00ff00</color><scale>1.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>')
    kml_lines.append(
        '<Style id="noschengenStyle"><IconStyle><color>ff0000ff</color><scale>1.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>')

    #recorrem la llista afegint cada punt
    i = 0
    while i < len(aeroports):
        a = aeroports[i]
        code = a.code
        lat = a.lat
        lon = a.lon
        sch = a.Schengen

        #si l'aeroport té un codi vàlid (no està buit), el dibuixem
        if code != "":
            kml_lines.append('<Placemark>')
            kml_lines.append('<name>{}</name>'.format(code))
            if sch == True:
                kml_lines.append('<styleUrl>#schengenStyle</styleUrl>')
            else:
                kml_lines.append('<styleUrl>#noschengenStyle</styleUrl>')
            kml_lines.append('<Point>')
            kml_lines.append('<coordinates>{:.6f},{:.6f},0</coordinates>'.format(lon, lat))
            kml_lines.append('</Point>')
            kml_lines.append('</Placemark>')
        i = i + 1

    kml_lines.append('</Document>')
    kml_lines.append('</kml>')

    #escrivim tot el resultat al fitxer KML (el del google earth)
    f = open(nom_fitxer, 'w', encoding='utf-8')
    j = 0
    while j < len(kml_lines):
        f.write(kml_lines[j] + "\n")
        j = j + 1
    f.close()
    print("Fitxer KML generat:", nom_fitxer)


#funció per guardar només els aeroports Schengen en un fitxer de text
def SaveSchengenAirports(aeroports, nom_fitxer):
    resultat = -1

    #comprovem que la llista no estigui buida
    if len(aeroports) > 0:

        #cerca per veure si n'hi ha algun de Schengen
        te_schengen = False
        i = 0
        while i < len(aeroports) and te_schengen == False:
            if aeroports[i].Schengen == True:
                te_schengen = True
            i = i + 1

        #si n'hem trobat algun, llavors sí, procedim a crear i escriure l'arxiu
        if te_schengen == True:
            f = open(nom_fitxer, 'w', encoding='utf-8')
            f.write("CODE LAT LON\n")

            j = 0
            while j < len(aeroports):
                if aeroports[j].Schengen == True:
                    #aqui canviem al format dms
                    lat_str = _decimal_a_dms_lat(aeroports[j].lat)
                    lon_str = _decimal_a_dms_lon(aeroports[j].lon)

                    #muntem la línia sumant els textos
                    linia = aeroports[j].code + " " + lat_str + " " + lon_str + "\n"
                    f.write(linia)
                j = j + 1

            f.close()
            resultat = 0

    return resultat