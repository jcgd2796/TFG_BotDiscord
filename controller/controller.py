# controller.py
import os
import requests
import dotenv
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
    incident = Incident(operator,title,description,ci,impact,severity)
    incidentJson = incident.toJsonObject()
    print(incidentJson)
    response = sendToSM(incidentJson)
    return response

def sendToSM(incidentJson):
    response = requests.post(url+"/incidents",data=incidentJson,auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    return response.json()

def checkSMAvailability():
    response = requests.get(url+'/operators/?name=bot',auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.status_code < 300



