import requests
import xml.etree.ElementTree as ET
import os
import argparse
from datetime import datetime
import csv

from MaxithlonXmlHelper import *

session = requests.Session()
BASE_MAXITHLON_PATH = "https://www.maxithlon.com/maxi-xml/"
TEAM_FOLDER = './Output/Team/'
DATE_FORMAT = '%d-%m-%Y'
    
def loadXmlManifestazione():
    os.mkdir(FOLDER_NAME);
    COMPETITION_PATH = BASE_MAXITHLON_PATH+'competition.php?competitionid='+COMPETITION_ID
    print("Eseguo request per manifestazione: ", COMPETITION_PATH)
    responseManifestazione = session.get(COMPETITION_PATH)
    print('Response recupero manifestazione ' + str(responseManifestazione.status_code))
    storeXmlToFile(FOLDER_NAME + COMPETITION_ID+'.xml', responseManifestazione.content)

def downloadEventiFromManifestazione():
    root = ET.parse(FOLDER_NAME + COMPETITION_ID+'.xml').getroot()
    print("downloadEventiFromManifestazione")
    for eventTag in root.findall('event'):
        eventId = eventTag.attrib['id']
        #print("Scarico l'evento con id " + eventId)
        responseEvent = session.get(BASE_MAXITHLON_PATH+'event.php?eventid='+eventId)
        #print("response per download evento " + eventId + ": " + str(responseEvent.status_code))
        
        storeXmlToFile(FOLDER_NAME + 'Event-'+eventId+'.xml', responseEvent.content)

#PEr ogni evento mi creo una mappa con tutte le posizioni a "punteggio" per poi calcolare il punteggio dopo
def analizzoEvento(rootXml):
    for atleta in rootXml.findall('./heat/athlete'):
        placingAtleta = int(str(atleta.find('placing').text))
        scoreAtleta = int(str(atleta.find('score').text))
        #if atleta.find('teamId').text == "91120":
        #    print("placingAtleta " + str(placingAtleta))

        if placingAtleta >= 1:
            team = atleta.find('teamId').text
            if team in TEAM_MAP.keys():
                TEAM_MAP.get(team).append((placingAtleta, scoreAtleta))
            else:
                TEAM_MAP[team] = [(placingAtleta, scoreAtleta)]

    #Se la gara è una staffetta
    for relay in rootXml.findall('./heat/relay'):
        placingRelay = int(str(relay.find('placing').text))
        scoreRelay = int(str(relay.find('score').text))
        if placingRelay >= 1:
            team = relay.find('teamId').text
            if team in TEAM_MAP.keys():
                TEAM_MAP.get(team).append((placingRelay,scoreRelay))
            else:
                TEAM_MAP[team] = [(placingRelay,scoreRelay)]

def analizzaCompetizione():
    print("Inizio a scaricare gli eventi associati alla manifestazione")
    with os.scandir(FOLDER_NAME) as entries:
        for entry in entries:
            if(entry.name.startswith('Event-')):
                tree = ET.parse(FOLDER_NAME+entry.name)
                root = tree.getroot()
                typeId = root.find('typeId').text
                if str(typeId) in ID_EVENTI_MAPPA.keys():
                    print('Analizzo ' + entry.name + ' - ' + str(ID_EVENTI_MAPPA.get(str(typeId))))
                    analizzoEvento(root)
                #else:
                #    print('Scarto ' + entry.name + ' - ' + str(ID_EVENTI_MAPPA.get(str(typeId))))
    print("Fine download eventi - Inizio calcolo punteggio/Premi")
    print(TEAM_MAP)
    calcolaPunteggio()
    print("Fine calcolo punteggio/Premi")

def loadTeam(teamId, teamFilePath):
    responseEvent = session.get(BASE_MAXITHLON_PATH+ 'team.php?teamid='+teamId)
    storeXmlToFile(teamFilePath, responseEvent.content)

### Questo metodo verifica se la manifestazione è un campionato nazionale italiano
def checkIfisITANatInd():
    rootXml = ET.parse(FOLDER_NAME + COMPETITION_ID+'.xml').getroot()
    type = rootXml.find('./type').text
    nationId = rootXml.find('./nationId').text
    return type == "8" and nationId == "1"
    
def calcolaPunteggio():
    isCalcolaPrice = checkIfisITANatInd()
    
    if isCalcolaPrice:
        PREMIO_MAPPA = doLoadPremiIndividualiNazItalia()
    for teamId in TEAM_MAP:
        teamFilePath = TEAM_FOLDER + 'TeamId-' + teamId + '.xml'
        #print('Analizzo il team ' + teamId + ', cerco il file ' +teamFilePath)

        if not os.path.exists(TEAM_FOLDER): 
            os.makedirs(TEAM_FOLDER)

        #se il team non è presente in locale lo carico salvado il suo xml
        if not os.path.exists(teamFilePath):
            loadTeam(teamId, teamFilePath)

        teamName = ET.parse(teamFilePath).getroot().find('teamName').text

        punteggioTeam = 0
        premioTeam = 0
        scoreTeam = 0

        #Iteriamo per tutte le posizione salvate per ogni team e calcoliamo il relavtivo preio/punteggio
        for (position,score) in TEAM_MAP.get(teamId):
            if position in PUNTEGGIO_MAPPA.keys():
                punteggioTeam = punteggioTeam + PUNTEGGIO_MAPPA.get(position)
            if isCalcolaPrice and position in PREMIO_MAPPA.keys():
                premioTeam = premioTeam + PREMIO_MAPPA.get(position)
            scoreTeam = scoreTeam +  score

        if punteggioTeam > 0:
            PUNTEGGIO_TEAM_LIST.append((teamName, punteggioTeam));
        if premioTeam > 0:
            PRIZE_TEAM_LIST.append((teamName, premioTeam))
        if scoreTeam > 0:
            SCORE_TEAM_LIST.append((teamName, scoreTeam))
        
def getFirstEle(team):
    return team[1]
    
def doManifestazione(id_manifestazione, analizzaSolo, downloadSolo,):
    global TEAM_MAP
    global COMPETITION_ID
    global FOLDER_NAME

    #Queste 3 global vengono utilizzate per aggregare punteggio, score o premi per ogni team e poi stamparli
    global PUNTEGGIO_TEAM_LIST
    global PRIZE_TEAM_LIST
    global SCORE_TEAM_LIST
    
    COMPETITION_ID = str(id_manifestazione)
    FOLDER_NAME = './Output/'+ COMPETITION_ID+ '/'
    PUNTEGGIO_TEAM_LIST = []
    PRIZE_TEAM_LIST = []
    SCORE_TEAM_LIST = [] #per calcolare il punteggio standard

    TEAM_MAP = {}
    
    

    if analizzaSolo != True:
        if os.path.exists(FOLDER_NAME):
            print("La manifestazione con id " + COMPETITION_ID + " è stata già analizzata")
            return
        else:
            print("Analizzo la manifestazione con id ", COMPETITION_ID)
            loadXmlManifestazione();
            downloadEventiFromManifestazione();
    
    if downloadSolo != True:
        analizzaCompetizione()
        PUNTEGGIO_TEAM_LIST.sort(key=getFirstEle, reverse=True)
        print("PUNTEGGIO_TEAM_LIST: \n", PUNTEGGIO_TEAM_LIST)
        storeFinalResult(FOLDER_NAME+'punteggio_' + COMPETITION_ID+'.csv', PUNTEGGIO_TEAM_LIST)

        SCORE_TEAM_LIST.sort(key=getFirstEle, reverse=True)
        print("SCORE_TEAM_LIST: \n", SCORE_TEAM_LIST)
        storeFinalResult(FOLDER_NAME+'score_' + COMPETITION_ID+'.csv', SCORE_TEAM_LIST)

        if len(PRIZE_TEAM_LIST) > 0:
            PRIZE_TEAM_LIST.sort(key=getFirstEle, reverse=True)
            print("PRIZE_TEAM_LIST:\n",PRIZE_TEAM_LIST)
            storeFinalResult(FOLDER_NAME+'premio_' + COMPETITION_ID+'.csv',PRIZE_TEAM_LIST)



def main():

    parser=argparse.ArgumentParser()

    parser.add_argument("-u", help="Username for xml login", required = True)
    parser.add_argument("-p", help="Password for xml login", required = True)
    parser.add_argument("-id",help="Id della competizione", required = False)
    parser.add_argument("-d", help="Solo Download degli xml della competizione", action='store_true', default = False)
    parser.add_argument("-a", help="Solo Analisi degli xml della competizione", action='store_true', default = False)

    args=parser.parse_args()
    
    print("Username ", args.u)
    print("Password ", args.p)
    print("Id Manifestazione ", args.id)
    print("Solo Donwload xml ", args.d)
    print("Solo Analisi xml ", args.a)
        
        
    loginPath = BASE_MAXITHLON_PATH+'login.php?user='+args.u+'&scode='+args.p
    print("Login....",loginPath)
    responseLogin = session.get(loginPath)
    print('Response login: ' + str(responseLogin.status_code))
    print('Response login: ' + str(responseLogin.content))
    
    global ID_EVENTI_MAPPA
    global PUNTEGGIO_MAPPA
    
    ID_EVENTI_MAPPA = doLoadMappaIdEventi()
    PUNTEGGIO_MAPPA = doLoadMappaPunteggio()

    COMPETITION_ID_LIST = []
    if args.id is not None:
        COMPETITION_ID_LIST.append(str(args.id))
    else :
        with open(os.getcwd()+"/Input/Manifestazioni.csv") as csvfile:
            reader = csv.reader(csvfile)
            today = datetime.today()
            for manifestazione in reader:
                dataManifestazione = datetime.strptime(str(manifestazione[1]), DATE_FORMAT)
                if today > dataManifestazione:
                    COMPETITION_ID_LIST.append(str(manifestazione[0]))
    
    
    if len(COMPETITION_ID_LIST)  == 0:
        print("Nessuna manifestazione da analizzare")
        exit(0)

    for id_manifestazione in COMPETITION_ID_LIST:
        doManifestazione(id_manifestazione, args.a, args.d)
    exit(0);
      
if __name__ == "__main__": 
  
    # calling main function 
    main() 