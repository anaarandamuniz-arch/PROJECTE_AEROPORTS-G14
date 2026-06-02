import os
from airport import IsSchengenAirport

#---------------------------------------------------------
#ESTRUCTURA DE CLASSES I PORTES LEBL
#---------------------------------------------------------
#definim les classes per fer l'estructura de les portes de l'aeroport
class Gate:
    def __init__(self, name):
        self.name = str(name)
        self.occupied = False
        self.aircraft_id = ""

class BoardingArea:
    def __init__(self, name, area_type):
        self.name = str(name)
        self.type = str(area_type)
        self.gates = []

class Terminal:
    def __init__(self, name):
        self.name = str(name)
        self.boarding_areas = []
        self.airlines = []

class BarcelonaAP:
    def __init__(self, code):
        self.code = str(code)
        self.terminals = []

#funcio per crear les portes d'una zona fent un bucle amb els numeros que toquen directament de la llista
def SetGates(area, init_gate, end_gate, prefix):
    resultat = -1
    if end_gate >= init_gate:
        area.gates = []
        i = init_gate
        while i <= end_gate:
            g = Gate(prefix + str(i))
            area.gates.append(g)
            i = i + 1
        resultat = 0
    return resultat

#---------------------------------------------------------
#CARREGA DE DADES LEBL
#---------------------------------------------------------
#carreguem quines companyies van a cada terminal tallant el text per l'espai
def LoadAirlines(terminal, filename):
    resultat = -1
    if os.path.isfile(filename):
        terminal.airlines = []
        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if len(line) > 0:
                parts = line.split()
                if len(parts) >= 2:
                    code = parts[-1].strip().upper()
                    terminal.airlines.append(code)
            i = i + 1
        resultat = 0
    else:
        print("Avis: No s'ha trobat l'arxiu", filename)
    return resultat

#llegim l'archiu de les terminals amb un bucle llarg que va muntant totes les zones al seu lloc
def LoadAirportStructure(filename):
    bcn = None
    if os.path.isfile(filename):
        directori = os.path.dirname(filename)

        f = open(filename, 'r', encoding='utf-8')
        lines = f.readlines()
        f.close()

        if len(lines) > 0:
            code = lines[0].strip()
            bcn = BarcelonaAP(code)

            i = 1
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith("Terminal"):
                    parts = line.split()
                    if len(parts) >= 3:
                        t_name = parts[1]
                        num_areas = int(parts[2])
                        t = Terminal(t_name)

                        ruta_airlines = os.path.join(directori, t_name + "_Airlines.txt")
                        LoadAirlines(t, ruta_airlines)

                        j = 0
                        while j < num_areas:
                            i = i + 1
                            if i < len(lines):
                                a_line = lines[i].strip()
                                a_parts = a_line.split()
                                if len(a_parts) >= 7:
                                    a_name = a_parts[0] + " " + a_parts[1]
                                    a_type = a_parts[2]
                                    init_g = int(a_parts[4])
                                    end_g = int(a_parts[6])

                                    ba = BoardingArea(a_name, a_type)
                                    prefix = t_name + "BA" + a_parts[1].lower() + "G"
                                    SetGates(ba, init_g, end_g, prefix)
                                    t.boarding_areas.append(ba)
                            j = j + 1
                        bcn.terminals.append(t)
                i = i + 1
    return bcn

#---------------------------------------------------------
#GESTIO D'ASSIGNACIONS
#---------------------------------------------------------
#mirem com estan les portes de buides o plenes fent un recorrido per tota l'estructura una a una
def GateOccupancy(bcn):
    res = []
    if bcn is not None:
        i = 0
        while i < len(bcn.terminals):
            t = bcn.terminals[i]
            j = 0
            while j < len(t.boarding_areas):
                ba = t.boarding_areas[j]
                k = 0
                while k < len(ba.gates):
                    g = ba.gates[k]
                    res.append([g.name, g.occupied, g.aircraft_id])
                    k = k + 1
                j = j + 1
            i = i + 1
    return res

#mirem si una aerolinia esta a la llista d'una terminal fent una busqueda
def IsAirlineInTerminal(terminal, name):
    trobat = False
    if terminal is not None and name != "":
        i = 0
        while i < len(terminal.airlines) and trobat == False:
            if terminal.airlines[i] == name:
                trobat = True
            i = i + 1
    return trobat

#busquem a quina terminal ha d'anar un avio mirant on esta la seva companyia
def SearchTerminal(bcn, name):
    t_name = ""
    if bcn is not None and name != "":
        i = 0
        trobat = False
        while i < len(bcn.terminals) and trobat == False:
            if IsAirlineInTerminal(bcn.terminals[i], name) == True:
                trobat = True
                t_name = bcn.terminals[i].name
            i = i + 1
    return t_name

#l'algoritme per assignar una porta lliure segons si l'avio ve de Schengen o no
def AssignGate(bcn, aircraft):
    resultat = -1
    if bcn is not None and aircraft is not None:
        t_name = SearchTerminal(bcn, aircraft.airline_company)
        if t_name != "":
            is_sch = IsSchengenAirport(aircraft.origin_airport)
            if is_sch == True:
                req_type = "Schengen"
            else:
                req_type = "non-Schengen"

            i = 0
            trobat_t = False
            t = None
            while i < len(bcn.terminals) and trobat_t == False:
                if bcn.terminals[i].name == t_name:
                    trobat_t = True
                    t = bcn.terminals[i]
                i = i + 1

            if trobat_t == True:
                j = 0
                gate_assigned = False
                while j < len(t.boarding_areas) and gate_assigned == False:
                    ba = t.boarding_areas[j]
                    if ba.type == req_type:
                        k = 0
                        while k < len(ba.gates) and gate_assigned == False:
                            g = ba.gates[k]
                            if g.occupied == False:
                                g.occupied = True
                                g.aircraft_id = aircraft.aircraft_id
                                gate_assigned = True
                            k = k + 1
                    j = j + 1

                if gate_assigned == True:
                    resultat = 0
    return resultat

#nova funcio v4 per assignar els avions nocturns fent servir les llistes per anar guardant-los
def AssignNightGates(bcn, aircrafts):
    resultat = -1
    if bcn is not None and len(aircrafts) > 0:
        from aircraft import NightAircraft
        nocturns = NightAircraft(aircrafts)
        i = 0
        while i < len(nocturns):
            AssignGate(bcn, nocturns[i])
            i = i + 1
        resultat = 0
    return resultat

#nova funcio v4 per treure un avio de la porta canviant els valors de la variable quan marxa
def FreeGate(bcn, aircraft_id):
    resultat = -1
    if bcn is not None and aircraft_id != "":
        i = 0
        trobat = False
        while i < len(bcn.terminals) and trobat == False:
            t = bcn.terminals[i]
            j = 0
            while j < len(t.boarding_areas) and trobat == False:
                ba = t.boarding_areas[j]
                k = 0
                while k < len(ba.gates) and trobat == False:
                    g = ba.gates[k]
                    if g.occupied == True and g.aircraft_id == aircraft_id:
                        g.occupied = False
                        g.aircraft_id = ""
                        trobat = True
                        resultat = 0
                    k = k + 1
                j = j + 1
            i = i + 1
    return resultat

#nova funcio mestra v4 que rep una hora (ex: "14:00") i va cridant les sortides i arribades depenent del moment
def AssignGatesAtTime(bcn, aircrafts, time):
    no_assignats = 0
    if bcn is not None and time != "":
        hora_actual = time.split(":")[0]

        i = 0
        while i < len(aircrafts):
            a = aircrafts[i]
            if a.time_of_departure != "":
                hora_sortida = a.time_of_departure.split(":")[0]
                if int(hora_sortida) < int(hora_actual):
                    FreeGate(bcn, a.aircraft_id)
            i = i + 1

        j = 0
        while j < len(aircrafts):
            a = aircrafts[j]
            if a.time_of_landing != "":
                hora_arribada = a.time_of_landing.split(":")[0]
                if int(hora_arribada) == int(hora_actual):
                    res = AssignGate(bcn, a)
                    if res == -1:
                        no_assignats = no_assignats + 1
            j = j + 1

    return no_assignats

#---------------------------------------------------------
#GRAFIC DE SIMULACIO 24H
#---------------------------------------------------------
#nova funcio v4 per simular tot el dia i pintar el grafic maco de colors guardant-ho en llistes
def PlotDayOccupancy(bcn, aircrafts):
    import matplotlib.pyplot as plt
    if bcn is not None:

        #AQUI SOLUCIONEM ELS AVIONS FANTASMES A LES GRAFIQUES
        #al fer la simulacio de les 24 hores (PlotDayOccupancy), va ser vital fer un bucle al principi per netejar i buidar totes les portes d'avions fantasmes de simulacions anteriors.
        #abans de fer aixo se'ns quedaven els avions de l'altra simulacio enganxats a la porta per sempre...
        i = 0
        while i < len(bcn.terminals):
            t = bcn.terminals[i]
            j = 0
            while j < len(t.boarding_areas):
                ba = t.boarding_areas[j]
                k = 0
                while k < len(ba.gates):
                    ba.gates[k].occupied = False
                    ba.gates[k].aircraft_id = ""
                    k = k + 1
                j = j + 1
            i = i + 1

        #fiquem els avions de nit directament
        AssignNightGates(bcn, aircrafts)

        hores = []
        ocupacio_t1 = []
        ocupacio_t2 = []
        rebutjats = []

        #simulem hora per hora el pas del temps fent un gran bucle de 0 a 24
        h = 0
        while h < 24:
            hora_str = str(h)
            if h < 10:
                hora_str = "0" + hora_str
            time_val = hora_str + ":00"
            hores.append(hora_str)

            no_assig = AssignGatesAtTime(bcn, aircrafts, time_val)
            rebutjats.append(no_assig)

            oc_t1 = 0
            oc_t2 = 0
            i = 0
            while i < len(bcn.terminals):
                t = bcn.terminals[i]
                j = 0
                while j < len(t.boarding_areas):
                    ba = t.boarding_areas[j]
                    k = 0
                    while k < len(ba.gates):
                        if ba.gates[k].occupied == True:
                            if t.name == "T1":
                                oc_t1 = oc_t1 + 1
                            elif t.name == "T2":
                                oc_t2 = oc_t2 + 1
                        k = k + 1
                    j = j + 1
                i = i + 1

            ocupacio_t1.append(oc_t1)
            ocupacio_t2.append(oc_t2)

            h = h + 1

        #pintem el grafic final
        plt.figure(figsize=(10, 5))
        plt.plot(hores, ocupacio_t1, label="T1 Ocupades", color="blue", marker="o")
        plt.plot(hores, ocupacio_t2, label="T2 Ocupades", color="green", marker="o")
        plt.plot(hores, rebutjats, label="Rebutjats (sense lloc)", color="red", linestyle="--")
        plt.xlabel("Hora del dia")
        plt.ylabel("Nombre de portes / avions")
        plt.title("Ocupació de l'aeroport per hores (Versió 4)")
        plt.legend()
        plt.grid(True)
        plt.show()