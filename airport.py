import os
import math
import matplotlib.pyplot as plt

#---------------------------------------------------------
#CLASSE AIRPORT
#---------------------------------------------------------
#definim la classe Airport que guardara els valors de cadascun
class Airport:
    def __init__(self, code, lat, lon):
        #comprovem si el codi es nul i li posem un text buit si ho es per evitar fallos
        if code is None:
            code = ""
        #assignem els valors a la variable, tambe traiem l'espai sobrant amb el .strip i ho posem en majuscules
        self.code = str(code).strip().upper()
        self.lat = float(lat)
        self.lon = float(lon)
        self.Schengen = False

#funcio per mirar si un aeroport es de l'espai Schengen fent una busqueda dins d'una llista de lletres fixes
def IsSchengenAirport(code):
    _SCHENGEN_PREFIXES = [
        'LO', 'EB', 'LK', 'LC', 'EK', 'EE', 'EF', 'LF', 'ED', 'LG', 'EH', 'LH',
        'BI', 'LI', 'EV', 'EY', 'EL', 'LM', 'EN', 'EP', 'LP', 'LZ', 'LJ', 'LE', 'ES', 'LS'
    ]

    trobat = False

    if code:
        c = str(code).strip().upper()

        if len(c) >= 2:
            prefix = c[0] + c[1]

            i = 0
            while i < len(_SCHENGEN_PREFIXES) and trobat == False:
                if _SCHENGEN_PREFIXES[i] == prefix:
                    trobat = True
                i = i + 1

    return trobat

#funcio senzilla per posar si es Schengen o no a la variable
def SetSchengen(aeroport):
    if aeroport is not None:
        aeroport.Schengen = IsSchengenAirport(aeroport.code)

#funcio per imprimir per pantalla de manera neta i limitant els decimals a sis
def PrintAirport(aeroport):
    if aeroport is None:
        print("Aeroport buit")
    else:
        print("Codi ICAO:", aeroport.code)
        print("Latitud: {:.6f}".format(aeroport.lat))
        print("Longitud: {:.6f}".format(aeroport.lon))
        print("Schengen:", aeroport.Schengen)

#---------------------------------------------------------
#FUNCIONS DE CONVERSIO DMS
#---------------------------------------------------------
#passem el text a numeros decimals fent matematiques basiques i tallant les lletres
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

#funcions per tornar el numero decimal a text normal de lletres i numeros per poder-ho guardar al fitxer
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

#fem aixo exactament igual per a la longitud
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

#---------------------------------------------------------
#FUNCIONS GESTIO AEROPORTS
#---------------------------------------------------------
#funcio per carregar els aeroports des del fitxer obrint la ruta i llegint
def LoadAirports(filename):
    aeroports = []

    if os.path.isfile(filename):
        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if len(line) > 0:
                up = line.upper()
                if not (up.startswith("CODE ") or up.startswith("ICAO ")):
                    parts = line.split()
                    if len(parts) >= 3:
                        code = parts[0].strip().upper()
                        lat_str = parts[1].strip()
                        lon_str = parts[2].strip()

                        #fem un bloque try except perque si hi ha una linia rara al txt no crashegi tot el programa de cop
                        try:
                            lat = _dms_str_a_decimal(lat_str)
                            lon = _dms_str_a_decimal(lon_str)
                            a = Airport(code, lat, lon)
                            aeroports.append(a)
                        except Exception:
                            pass
            i = i + 1

    return aeroports

#funcio per posar un aeroport nou a la llista evitant repetits amb un bucle
def AddAirport(aeroports, aeroport):
    resultat = -1

    if aeroport is not None:
        code = aeroport.code

        i = 0
        trobat = False
        while i < len(aeroports) and trobat == False:
            if aeroports[i].code == code:
                trobat = True
            i = i + 1

        if trobat == True:
            resultat = 1
        else:
            aeroports.append(aeroport)
            resultat = 0

    return resultat

#funcio per esborrar buscant manualment per la llista i fent servir el del de python per trencar-lo de debó
def RemoveAirport(aeroports, code):
    resultat = -1

    if code:
        c = str(code).strip().upper()
        i = 0
        trobat = False

        while i < len(aeroports) and trobat == False:
            if getattr(aeroports[i], "code", "").upper() == c:
                del aeroports[i]
                trobat = True
            else:
                i = i + 1

        if trobat == True:
            resultat = 0

    return resultat

#---------------------------------------------------------
#FUNCIONS DE MAPES I EXPORTACIO
#---------------------------------------------------------
#funcio per fer el grafic on mirem la llista d'aeroports un per un per veure qui es Schengen i qui no ho es
def PlotAirports(aeroports):
    schengen = 0
    no_schengen = 0

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

#funcio per crear la llista de punts que demana el Google Earth escrivint text un darrera l'altre
def MapAirports(aeroports, nom_fitxer="mapa_aeroports.kml"):
    kml_lines = []
    kml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    kml_lines.append('<kml xmlns="http://www.opengis.net/kml/2.2">')
    kml_lines.append('<Document>')
    kml_lines.append('<name>Mapa Aeroports</name>')

    kml_lines.append(
        '<Style id="schengenStyle"><IconStyle><color>ff00ff00</color><scale>1.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>')
    kml_lines.append(
        '<Style id="noschengenStyle"><IconStyle><color>ff0000ff</color><scale>1.2</scale><Icon><href>http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png</href></Icon></IconStyle></Style>')

    i = 0
    while i < len(aeroports):
        a = aeroports[i]
        code = a.code
        lat = a.lat
        lon = a.lon
        sch = a.Schengen

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

    f = open(nom_fitxer, 'w', encoding='utf-8')
    j = 0
    while j < len(kml_lines):
        f.write(kml_lines[j] + "\n")
        j = j + 1
    f.close()
    print("Fitxer KML generat:", nom_fitxer)

#funcio de guardat final on fem un bucle molt rapid per treure nomes aquells que son de Schengen
def SaveSchengenAirports(aeroports, nom_fitxer):
    resultat = -1

    if len(aeroports) > 0:

        te_schengen = False
        i = 0
        while i < len(aeroports) and te_schengen == False:
            if aeroports[i].Schengen == True:
                te_schengen = True
            i = i + 1

        if te_schengen == True:
            f = open(nom_fitxer, 'w', encoding='utf-8')
            f.write("CODE LAT LON\n")

            j = 0
            while j < len(aeroports):
                if aeroports[j].Schengen == True:
                    lat_str = _decimal_a_dms_lat(aeroports[j].lat)
                    lon_str = _decimal_a_dms_lon(aeroports[j].lon)

                    linia = aeroports[j].code + " " + lat_str + " " + lon_str + "\n"
                    f.write(linia)
                j = j + 1

            f.close()
            resultat = 0

    return resultat

