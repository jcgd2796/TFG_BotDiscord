# controller.py
import os
import requests
import dotenv
import json
from requests.auth import HTTPBasicAuth
from model.Incident import *

dotenv.load_dotenv()
url = os.getenv("URL")

def validateLogin(login):
    if(login == "!exit") or (login == "!Exit"):
        return True
    response = requests.get(url+'/operators/?name='+login,
            auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    if (response.status_code != 200):
        raise Exception
    elif (response.json()['@count']==0):
        return False
    else:
        return True

def getOperatorName(login):
    return requests.get(url+'/operators/?name='+login,
            auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS"))).json()['content'][0]['Operator']['contact.name']

def validateTitle(title):
    if(title == "!exit") or (title == "!Exit"):
        return True
    return len(title) > 10

def validateCI(ci):
    response = requests.get(url+'/devices/?DisplayName='+ci,auth=HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return (response.status_code < 300) and (response.json()['@count'] > 0)

def getCI(name):
    response = requests.get(url+'/devices/?DisplayName='+name,auth=HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.json()

def validateImpact(impact):
    if(impact == "!exit") or (impact == "!Exit"):
        return True
    return (int(impact) > 1 and int(impact) < 5) 

def createIncident(operator,title,description,ci,impact,severity):
    incident = Incident(operator,title,description,ci,impact,severity,None)
    incidentJson = incident.toJsonObject()
    response = sendToSM(json.dumps(incidentJson))
    return response

def updateIncident(incidentJson):
    response = sendUpdateToSM(incidentJson)
    return response

def sendUpdateToSM(incidentJson):
    response = requests.put(url+"/incidents/"+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    if response.status_code >= 300:
        raise Exception
    return response.json()

def sendToSM(incidentJson):
    response = requests.post(url+"/incidents",data=incidentJson,auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    if response.status_code >= 300:
        raise Exception
    return response.json()

def checkSMAvailability():
    response = requests.get(url+'/operators/?name=bot',auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.status_code < 300

def validateIncident(incidentId):
    response = requests.get(url+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.json()['ReturnCode'] == 0

def getIncident(incidentId):
    response = requests.get(url+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return Incident(response.json()['Incident']['Contact'],response.json()['Incident']['Title'],response.json()['Incident']['Description'][0],response.json()['Incident']['Service'],response.json()['Incident']['Impact'],response.json()['Incident']['Urgency'],response.json()['Incident']['IncidentID'])

def getIncidentData(incidentId):
    return requests.get(url+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS"))).json()


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

def closeIncident(incidentJson):
    return sendUpdateToSM(incidentJson)
