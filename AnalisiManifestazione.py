import requests
import xml.etree.ElementTree as ET
import os
import argparse, sys

ID_EVENTI_MAPPA = {}
ID_EVENTI_MAPPA['1'] = '100 Metres'
ID_EVENTI_MAPPA['4'] = '200 Metres'
ID_EVENTI_MAPPA['6'] = '400 Metres'
ID_EVENTI_MAPPA['8'] = '800 Metres'
ID_EVENTI_MAPPA['11'] = '1500 Metres'
ID_EVENTI_MAPPA['14'] = '5000 Metres'
ID_EVENTI_MAPPA['15'] = '10000 Metres'
ID_EVENTI_MAPPA['19'] = '3000 Steeplechase'
ID_EVENTI_MAPPA['23'] = '110 Hurdles'
ID_EVENTI_MAPPA['25'] = '400 Hurdles'
ID_EVENTI_MAPPA['26'] = 'High Jump'
ID_EVENTI_MAPPA['27'] = 'Pole Vault'
ID_EVENTI_MAPPA['28'] = 'Long Jump'
ID_EVENTI_MAPPA['29'] = 'Triple Jump'
ID_EVENTI_MAPPA['31'] = 'Shot Put'
ID_EVENTI_MAPPA['32'] = 'Discus Throw'
ID_EVENTI_MAPPA['33'] = 'Hammer Throw'
ID_EVENTI_MAPPA['34'] = 'Javelin Throw'
ID_EVENTI_MAPPA['46'] = '10Km Race Walk'
ID_EVENTI_MAPPA['47'] = '20Km Race Walk'
ID_EVENTI_MAPPA['53'] = 'Marathon'
ID_EVENTI_MAPPA['72'] = '50Km Race Walk'
ID_EVENTI_MAPPA['80'] = 'Relay 4x100'
ID_EVENTI_MAPPA['90'] = 'Relay 4x400'
ID_EVENTI_MAPPA['120'] = 'Heptathlon'
ID_EVENTI_MAPPA['130'] = 'Decathlon'

PUNTEGGIO_MAPPA = {}
PUNTEGGIO_MAPPA[1] = 8 # 1 posizione, 8 punti
PUNTEGGIO_MAPPA[2] = 7 # 2 posizione, 7 punti
PUNTEGGIO_MAPPA[3] = 6
PUNTEGGIO_MAPPA[4] = 5
PUNTEGGIO_MAPPA[5] = 4
PUNTEGGIO_MAPPA[6] = 3
PUNTEGGIO_MAPPA[7] = 2
PUNTEGGIO_MAPPA[8] = 1

session = requests.Session()
BASE_MAXITHLON_PATH = "https://www.maxithlon.com/maxi-xml/"
TEAM_FOLDER = './Output/Team/'

def storeXmlToFile(fileName, content):
    with open(fileName, 'wb') as f: 
            f.write(content)
            
def storePunteggio(fileName):
    # open file in write mode
    with open(fileName, 'w', encoding="utf-8") as fp:
        for item in PUNTEGGIO_TEAM_LIST:
            row = str(item[0]) + ";" + str(item[1])
            fp.write(row + "\n")
    
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

def analizzoEvento(rootXml):
    for atleta in rootXml.findall('./heat/athlete'):
        placingAtleta = int(str(atleta.find('placing').text))
        if(placingAtleta <= 8 and placingAtleta >= 1):
            team = atleta.find('teamId').text
            if team in TEAM_MAP.keys():
                TEAM_MAP.get(team).append(placingAtleta)
            else:
                TEAM_MAP[team] = [placingAtleta]

def analizzaCompetizione():
    print("Inizio a scaricare gli eventi associati alla manifestazione")
    with os.scandir(FOLDER_NAME) as entries:
        for entry in entries:
            if(entry.name.startswith('Event-')):
                tree = ET.parse(FOLDER_NAME+entry.name)
                root = tree.getroot()
                typeId = root.find('typeId').text
                if str(typeId) in ID_EVENTI_MAPPA.keys():
                    #print('Analizzo ' + entry.name + ' - ' + str(ID_EVENTI_MAPPA.get(str(typeId))))
                    analizzoEvento(root)
    print("Fine download eventi")

def loadTeam(teamId, teamFilePath):
    responseEvent = session.get(BASE_MAXITHLON_PATH+ 'team.php?teamid='+teamId)
    storeXmlToFile(teamFilePath, responseEvent.content)
        
def calcolaPunteggio():
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
        for position in TEAM_MAP.get(teamId):
            #print('Per la posizione ' + str(position) + ' abbiamo come punteggio ' + str(PUNTEGGIO_MAPPA.get(position)))
            punteggioTeam = punteggioTeam + PUNTEGGIO_MAPPA.get(position)

        #print('Team ' + teamName + ', punteggio ' + str(punteggioTeam))
        PUNTEGGIO_TEAM_LIST.append((teamName, punteggioTeam));
        
def getFirstEle(team):
    return team[1]
    
               
def main():

    parser=argparse.ArgumentParser()

    parser.add_argument("-u", help="Username for xml login", required = True)
    parser.add_argument("-p", help="Password for xml login", required = True)
    parser.add_argument("-id",help="Id della competizione", required = True)
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
    
    global COMPETITION_ID
    global FOLDER_NAME
    global TEAM_MAP
    global PUNTEGGIO_TEAM_LIST

    COMPETITION_ID = str(args.id)
    FOLDER_NAME = './Output/'+ str(COMPETITION_ID) + '/'
    TEAM_MAP = {}
    PUNTEGGIO_TEAM_LIST = []
    
    if args.a != True:
        loadXmlManifestazione();
        downloadEventiFromManifestazione();
    
    if args.d != True:
        analizzaCompetizione()
        #print(TEAM_MAP)
        calcolaPunteggio()

        PUNTEGGIO_TEAM_LIST.sort(key=getFirstEle, reverse=True)
        print(PUNTEGGIO_TEAM_LIST)
        storePunteggio(FOLDER_NAME+'punteggio.csv')
      
if __name__ == "__main__": 
  
    # calling main function 
    main() 