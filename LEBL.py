import os
from airport import IsSchengenAirport


#definim les classes per fer lestructura de les portes i l'aeroport de Barcelona
class Gate:
    def __init__(self, name):
        self.name = str(name)
        self.occupied = False  #de moment la porta esta lliure
        self.aircraft_id = ""  #no hi ha cap avio a la porta encara


class BoardingArea:
    def __init__(self, name, area_type):
        self.name = str(name)
        self.type = str(area_type)  #aqui guardem si es schengen o no
        self.gates = []  #una llista on aniran les portes d'aquesta zona


class Terminal:
    def __init__(self, name):
        self.name = str(name)
        self.boarding_areas = []  #llista de les zones de la terminal (A, B, C...)
        self.airlines = []  #aqui guardarem les companyies que treballen en aquesta terminal


class BarcelonaAP:
    def __init__(self, code):
        self.code = str(code)
        self.terminals = []  #l'aeroport te les dues terminals (T1 i T2)


#funcio per crear les portes d'una zona segons els numeros que ens donen a l'archiu
def SetGates(area, init_gate, end_gate, prefix):
    resultat = -1
    #conprovem que el numero final sigui mes gran que el de principi
    if end_gate >= init_gate:
        area.gates = []  #netejem les portes si n'hi havia d'abans
        i = init_gate
        while i <= end_gate:
            #muntem el nom de la porta sumant el prefix i el numero
            g = Gate(prefix + str(i))
            area.gates.append(g)
            i = i + 1
        resultat = 0  #si tot ha anat be retornem un zero
    return resultat


#carreguem les companyies que van a cada terminal des del fitxer de text de les airlines
def LoadAirlines(terminal, filename):
    resultat = -1
    #mirem que el archiu existeixi abans de fer res
    if os.path.isfile(filename):
        terminal.airlines = []
        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()  #fem servir el .strip per treure els espais i salts de linia
            if len(line) > 0:
                #separem per espais i agafem l'ultim que es el codi de la companyia (ex: VLG)
                parts = line.split()
                if len(parts) >= 2:
                    code = parts[-1].strip().upper()
                    terminal.airlines.append(code)
            i = i + 1
        resultat = 0
    else:
        print("Avis: No s'ha trobat el archiu", filename)  #si no hi es el fitxer donem un avis
    return resultat


#llegim l'arxiu de les terminals per muntar tot l'esquelet de l'aeroport a la memoria
def LoadAirportStructure(filename):
    bcn = None
    if os.path.isfile(filename):
        #aixo es una dreçera per saber on estan els fitxers de les companyies guardats
        directori = os.path.dirname(filename)

        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        if len(lines) > 0:
            #la primera linia ens diu el codi de l'aeroport (LEBL)
            code = lines[0].strip()
            bcn = BarcelonaAP(code)

            i = 1
            while i < len(lines):
                line = lines[i].strip()
                #si la linia comença per Terminal, creem una terminal nova
                if line.startswith("Terminal"):
                    parts = line.split()
                    if len(parts) >= 3:
                        t_name = parts[1]
                        num_areas = int(parts[2])
                        t = Terminal(t_name)

                        #busquem el archiu de les companyies de la terminal T1 o T2
                        ruta_airlines = os.path.join(directori, t_name + "_Airlines.txt")
                        LoadAirlines(t, ruta_airlines)

                        #bucle per llegir totes les zones (boarding areas) que te la terminal
                        j = 0
                        while j < num_areas:
                            i = i + 1
                            if i < len(lines):
                                a_line = lines[i].strip()
                                a_parts = a_line.split()
                                #conprovem que hi hagi prou dades a la linia
                                if len(a_parts) >= 7:
                                    a_name = a_parts[0] + " " + a_parts[1]
                                    a_type = a_parts[2]  #aqui sabem si es schengen
                                    init_g = int(a_parts[4])
                                    end_g = int(a_parts[6])

                                    ba = BoardingArea(a_name, a_type)
                                    #creem el nom que thinkran les portes (ex: T1BAaG1)
                                    prefix = t_name + "BA" + a_parts[1].lower() + "G"
                                    SetGates(ba, init_g, end_g, prefix)
                                    t.boarding_areas.append(ba)
                            j = j + 1
                        bcn.terminals.append(t)
                i = i + 1
    return bcn  #retornem el aeroport sencer muntat


#mirem com estan les portes de buides o plenes i fem una llista amb tot el que hi ha
def GateOccupancy(bcn):
    res = []
    if bcn is not None:
        #entrem a cada terminal, despres a cada zona i finalment a cada porta
        i = 0
        while i < len(bcn.terminals):
            t = bcn.terminals[i]
            j = 0
            while j < len(t.boarding_areas):
                ba = t.boarding_areas[j]
                k = 0
                while k < len(ba.gates):
                    g = ba.gates[k]
                    #guardem el nom, si esta plena i el id del avio que hi ha
                    res.append([g.name, g.occupied, g.aircraft_id])
                    k = k + 1
                j = j + 1
            i = i + 1
    return res


#mirem si una companyia d'avions esta en una terminal concreta
def IsAirlineInTerminal(terminal, name):
    trobat = False
    if terminal is not None and name != "":
        i = 0
        #busquem dins de la llista de companyies de la terminal
        while i < len(terminal.airlines) and trobat == False:
            if terminal.airlines[i] == name:
                trobat = True
            i = i + 1
    return trobat


#busquem a quina terminal ha d'anar un avio segons la seva companyia
def SearchTerminal(bcn, name):
    t_name = ""
    if bcn is not None and name != "":
        i = 0
        trobat = False
        while i < len(bcn.terminals) and trobat == False:
            #si la companyia esta en aquesta terminal ja la hem trobat
            if IsAirlineInTerminal(bcn.terminals[i], name) == True:
                trobat = True
                t_name = bcn.terminals[i].name
            i = i + 1
    return t_name


#l'algoritme per posar el avio a una porta lliure segons si es schengen o no
def AssignGate(bcn, aircraft):
    resultat = -1
    if bcn is not None and aircraft is not None:
        #primer busquem la terminal on ha d'anar el avio segons la companyia
        t_name = SearchTerminal(bcn, aircraft.airline_company)
        if t_name != "":
            #conprovem si el aeroport de origen es de schengen
            is_sch = IsSchengenAirport(aircraft.origin_airport)
            if is_sch == True:
                req_type = "Schengen"
            else:
                req_type = "non-Schengen"

            #busquem el objecte terminal que toca
            i = 0
            trobat_t = False
            t = None
            while i < len(bcn.terminals) and trobat_t == False:
                if bcn.terminals[i].name == t_name:
                    trobat_t = True
                    t = bcn.terminals[i]
                i = i + 1

            #si hem trobat la terminal mirem quina porta de la zona correcta esta lliure
            if trobat_t == True:
                j = 0
                gate_assigned = False
                while j < len(t.boarding_areas) and gate_assigned == False:
                    ba = t.boarding_areas[j]
                    #mirem que la zona sigui del tipus que necessitem (schengen o no)
                    if ba.type == req_type:
                        k = 0
                        while k < len(ba.gates) and gate_assigned == False:
                            g = ba.gates[k]
                            #si trobem una porta que no estigui ocupada la omplim
                            if g.occupied == False:
                                g.occupied = True
                                g.aircraft_id = aircraft.aircraft_id
                                gate_assigned = True
                            k = k + 1
                    j = j + 1

                if gate_assigned == True:
                    resultat = 0
    return resultat