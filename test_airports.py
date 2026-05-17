from airport import LoadAirports, SaveSchengenAirports, AddAirport, RemoveAirport, SetSchengen, PrintAirport, Airport
def provar_load(nom_fitxer):
    aeroports = LoadAirports(nom_fitxer)
    print("S'han carregat", len(aeroports), "aeroports de", nom_fitxer)
    for a in aeroports:
        SetSchengen(a)
    return aeroports

if __name__ == "__main__":

    nom = "Airports.txt"
    aeroports = provar_load(nom)


    i = 0
    while i < len(aeroports) and i < 5:
        PrintAirport(aeroports[i])
        print("----")
        i += 1


    nou = Airport("TEST", 10.0, 20.0)
    SetSchengen(nou)
    res = AddAirport(aeroports, nou)
    if res == 0:
        print("Aeroport TEST afegit")
    elif res == 1:
        print("Aeroport TEST ja existia")
    else:
        print("Error afegint TEST")

    res2 = RemoveAirport(aeroports, "TEST")
    if res2 == 0:
        print("Aeroport TEST eliminat")
    else:
        print("No s'ha trobat TEST per eliminar")


    res3 = SaveSchengenAirports(aeroports, "SchengenAirports.txt")
    if res3 == 0:
        print("Fitxer SchengenAirports.txt creat")
    else:
        print("No s'ha creat fitxer Schengen (llista buida o sense Schengen)")


from airport import crear_fitxer_examen


crear_fitxer_examen()


f = open("examen.txt", "r")
linies = f.readlines()

if len(linies) == 0:
    print("No s'ha trobat cap aeroport que compleixi les condicions.")
else:
    cnt = 0
    while cnt < len(linies):
        print("Trobat: " + linies[cnt].strip())
        cnt = cnt + 1
f.close()