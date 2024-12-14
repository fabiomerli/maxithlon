import os
import csv

def storeFinalResult(fileName, list):
    # open file in write mode
    with open(fileName, 'w', encoding="utf-8") as fp:
        for item in list:
            row = str(item[0]) + ";" + str(item[1])
            fp.write(row + "\n")

def doLoadMappaIdEventi():
    ID_EVENTI_MAPPA = {}
    with open(os.getcwd()+"/Input/EventiID.csv") as csvfile:
        reader = csv.reader(csvfile)
        for evento in reader:
            ID_EVENTI_MAPPA[evento[0]]=evento[1]
    return ID_EVENTI_MAPPA

def doLoadMappaPunteggio():
    return loadByFile("/Input/Punteggio.csv")

def doLoadPremiContEu():
    return loadByFile("/Input/PremiContEu.csv")

def doLoadPremiContAmerica():
    return loadByFile("/Input/PremiContAmerica.csv")

def doLoadPremiContAsiaAfrica():
    return loadByFile("/Input/PremiContAsiaAfrica.csv")

def doLoadPremiIndividualiNazItalia():
    return loadByFile("/Input/PremiIndNazItalia.csv")

def doLoadMondiali():
    return loadByFile("/Input/PremiMondiali.csv")

def doLoadPremiPolonia():
    return loadByFile("/Input/PremiIndNazPol.csv")

def doLoadPremiU21Mondiali():
    return loadByFile("/Input/PremiMondialiU21.csv")

def loadByFile(filePath):
    PREMIO_MAPPA = {}
    with open(os.getcwd()+filePath) as csvfile:
        reader = csv.reader(csvfile)
        position = 1
        for punteggio in reader:
            PREMIO_MAPPA[position]=int(punteggio[0])
            position=position+1
    return PREMIO_MAPPA

def storeXmlToFile(fileName, content):
    with open(fileName, 'wb') as f: 
            f.write(content)