# controller.py
import os
import requests
import dotenv
from requests.auth import HTTPBasicAuth
from model.Incident import *

dotenv.load_dotenv()
url = os.getenv("URL")

def validateLogin(login):
    response = requests.get(url+'/operators/?name='+login,
            auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return(response.json()['@count']>0)

def validateTitle(title):
    return len(title) > 10

def getCIs():
    response = requests.get(url+'/devices',auth=HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS")))
    return response.json()

def validateImpact(impact):
    return (int(impact) > 0 and int(impact) < 5) 

def createIncident(operator,title,description,ci,impact,severity):
    incident = Incident(operator,title,description,ci,impact,severity)
    incidentJson = incident.toJsonObject()
    response = sendToSM(incidentJson)
    return response

def sendToSM(incidentJson):
    response = requests.post(url+"/incidents",data=incidentJson,auth=HTTPBasicAuth('bot',os.getenv('BOT_OPERATOR_PASS')))
    return response.json()


