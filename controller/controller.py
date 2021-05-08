# controller.py
import os
import requests
import dotenv
import json
from requests.auth import HTTPBasicAuth
from model.Incident import *
from model.Kpi import *

dotenv.load_dotenv()
URL = os.getenv("URL")
BOT_PASSWORD = os.getenv("BOT_OPERATOR_PASS")

def validateLogin(login):
    if login.lower() == '!exit':
        return True
    response = requests.get(URL+'/operators/?name='+login,
            auth = HTTPBasicAuth('bot',BOT_PASSWORD))
    if (response.status_code != 200):
        raise Exception
    elif (response.json()['@count']==0):
        return False
    else:
        return True

def getOperatorName(login):
    return requests.get(URL+'/operators/?name='+login,
            auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS"))).json()['content'][0]['Operator']['contact.name']

def validateTitle(title):
    if title.lower() == '!exit':
        return True
    return len(title) > 10

def validateCI(ci):
    if ci.lower() == '!exit':
        return True
    response = requests.get(URL+'/devices/?DisplayName='+ci,auth=HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return (response.status_code < 300) and (response.json()['@count'] > 0)

def getCI(name):
    response = requests.get(URL+'/devices/?DisplayName='+name,auth=HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.json()

def validateImpact(impact):
    if impact.lower() == '!exit':
        return True
    try:
        return (int(impact) > 1 and int(impact) < 5) 
    except ValueError:      #NaN
        return False

def createIncident(operator,title,description,ci,impact,severity):
    incident = Incident(operator,title,description,ci,impact,severity,None,'Log')
    incidentJson = incident.toJsonObject()
    response = sendToSM(json.dumps(incidentJson))
    return response

def updateIncident(incident):
    response = sendUpdateToSM(incident.toJsonObject())
    return response

def sendClosureToSM(incidentJson):
    response = requests.put(URL+"/incidents/"+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    if response.status_code >= 300:
        raise Exception
    return response.json()

def sendUpdateToSM(incidentJson):
    response = requests.put(URL+"/incidents/"+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    if response.status_code >= 300:
        raise Exception
    return response.json()

def sendToSM(incidentJson):
    response = requests.post(URL+"/incidents",data=incidentJson,auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    if response.status_code >= 300:
        raise Exception
    return response.json()

def checkSMAvailability():
    response = requests.get(URL+'/operators/?name=bot',auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.status_code < 300

def validateIncident(incidentId):
    if incidentId.lower() == '!exit':
        return True
    response = requests.get(URL+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.json()['ReturnCode'] == 0

def getIncident(incidentId):
    response = requests.get(URL+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    incident = Incident(response.json()['Incident']['Contact'],response.json()['Incident']['Title'],response.json()['Incident']['Description'][0],response.json()['Incident']['Service'],response.json()['Incident']['Impact'],response.json()['Incident']['Urgency'],response.json()['Incident']['IncidentID'],response.json()['Incident']['Phase'])
    return incident

def getIncidentData(incidentId):
    return requests.get(URL+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS"))).json()

def validateList(valuesString):
    valuesList = valuesString.replace(" ","").lower().split(",")
    staticValuesList = ['operator','title','description','impact','severity','!exit']
    for value in valuesList:
        if value not in staticValuesList:
            return False
    return True

def getValuesList(valuesString):
    return valuesString.replace(" ","").lower().split(",")

def validateClosureCode(closureCode):
    if closureCode.lower() == '!exit':
        return True
    else:
        return int(closureCode) >= 0 and int(closureCode) <13

def getClosureCode(closureCode):
    closureCodesList = ['Diagnosed Succesfully','No Fault Found','No User Response','Not Reproducible','Out of Scope','Request Rejected','Resolved Succesfully','Unable to Solve','Withdrawn by User','Automatically Closed','Solved by Change/Service Request','Solved by User Instruction','Solved by Workaround']
    return str(closureCodesList[int(closureCode)])

def closeIncident(incident):
    return sendClosureToSM(incident.toJsonObject)

def validateKpiList(kpis):
    kpiList = kpis.replace(" ","").lower().split(',')
    if ('!exit' in kpiList):
        return True
    elif '*' in kpiList:
        return True
    else:
        try:
            for kpi in kpiList:
                if int(kpi) > 11 or int(kpi) < 0:
                    return False
            return True
        except ValueError:
            return False

def getKpis(kpis):
    staticKpiList = ['Average group reassignments','Average number of incidents solved per employee daily','Average days between Incident opening and closure','Number of incidents closed' 
    ,'Number of incidents closed this month','Number of incidents daily closed this month','Number of incidents created this month','Average number of incidents created daily this month','Number of incidents solved','Most common Incident priority','Percentage of critical Incidents','Percentage of Incidents escalated']
    kpiList = kpis.replace(" ","").lower().split(',')
    kpis = list()
    if '*' in kpiList:
        for kpiName in staticKpiList:
            kpis.append(getLatestKpi(kpiName))
    else:
        for kpiNumber in kpiList:
            kpis.append(getLatestKpi(staticKpiList[int(kpiNumber)]))
    return kpis

def getLatestKpi(kpiName):
    response = requests.get(URL+'/KPIS/?name='+kpiName+'&sort=date:descending',auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    latestKpi = response.json()['content'][0]['KPI']  #The latest kpi is always the first one in the JsonArray, as it's sorted
    return Kpi(latestKpi['Name'],latestKpi['Value'],latestKpi['Last_update'])

def validateFinishMessage(finishMessage):
    return finishMessage.lower() == 'yes' or finishMessage.lower() == 'no'

        
