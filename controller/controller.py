# controller.py
#Controller of the bot. Validates the values introduced by the user and communicates with Service Manager Server
import os
import requests #For the http requests to SM REST API
from requests.auth import HTTPBasicAuth #SM REST API requires authentication
import dotenv #For the environment file
import json
#Model imports
from model.Incident import *
from model.Kpi import *

dotenv.load_dotenv()
URL = os.getenv("URL")
BOT_PASSWORD = os.getenv("BOT_OPERATOR_PASS")
URL_OPERATOR = URL+'/operators/?name='
URL_CI = URL+'/devices/?DisplayName='
URL_INCIDENT = URL+"/incidents/"
URL_KPI = URL+'/KPIS/?name='
BOT_AUTH = HTTPBasicAuth('bot',BOT_PASSWORD)

#Validates an operator login given as argument exists in SM server.
#Returns True if there's an operator with that login in SM, of if the user wants to cancell the process. False otherwise.
#If unable to connect to SM, throws an exception
def validateLogin(login):
    if login.lower() == '!exit':
        return True
    response = requests.get(URL_OPERATOR+login,auth = BOT_AUTH)
    if (response.status_code != 200):
        raise Exception('Unable to connect to SM')
    elif (response.json()['@count']==0):
        return False
    else:
        return True

#Get an operator name from its login, given as argument.
#Connects to Service Manager to get the name of the operator. This method must be used only after ensuring that validateLogin returns True and the
#given login is not "!exit", will return an invalid result otherwise.
def getOperatorName(login):
    return requests.get(URL_OPERATOR+login,auth = BOT_AUTH).json()['content'][0]['Operator']['contact.name']

#Validates the Incident title/description introduced by the user. An incident title/description is valid only if it has more than 10 characters.
def validateTitle(title):
    if title.lower() == '!exit':
        return True
    return title != None and len(title) > 10

#Validates the Incident CI introduced by the user. A CI is valid if its name is in SM CIs table
def validateCI(ci):
    if ci.lower() == '!exit':
        return True
    response = requests.get(URL_CI+ci,auth = BOT_AUTH)
    return (response.status_code < 300) and (response.json()['@count'] > 0)

#Get a CI from its name, given as argument.
#Connects to Service Manager to get the CI as a Json String. This method must be used only after ensuring that validateCI returns True and the
#given CI was not "!exit", will return an invalid result otherwise.
def getCI(name):
    return requests.get(URL_CI+name,auth=BOT_AUTH).json()

#Validates the Incident impact or severity values introduces by the user. An impact/Severity value is only valid
#if it's a number between 2 and 4. Throws an exception if the input is not a number.
def validateImpact(impact):
    if impact.lower() == '!exit':
        return True
    try:
        return (int(impact) > 1 and int(impact) < 5) 
    except ValueError:      #NaN
        return False

#Creates an Incident object with the operator's name, and Incident title, description, affected CI, impact and severity values provided as arguments
#After that, gets it as a Json String, and submits it to Service Manager Server.
def createIncident(operator,title,description,ci,impact,severity):
    incident = Incident(operator,title,description,ci,impact,severity,None,'Log')
    incidentJson = incident.toJsonObject()
    response = sendToSM(json.dumps(incidentJson))
    return response

#Submit an Incident given as argument to SM. The Incident must be a Json string.
#Throws an exception if unble to connect to SM, returns SM response otherwise.
def sendToSM(incidentJson):
    response = requests.post(URL+"/incidents",data=incidentJson,auth=BOT_AUTH)
    if response.status_code >= 300:
        raise Exception ('Unable to connect to SM')
    return response.json()

#Transforms an Incident to a Json String and sends it to SM Server to update its values. The Incident is given as an argument.
def updateIncident(incident):
    response = sendUpdateToSM(incident.toJsonObject())
    return response

#Sends an Incident (as a Json string) given as argument to SM Server to save it on its database.
def sendUpdateToSM(incidentJson):
    response = requests.put(URL_INCIDENT+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=BOT_AUTH)
    if response.status_code >= 300:
        raise Exception ('Unable to connect to SM')
    return response.json()

#Transforms an Incident to a Json String and sends it to SM Server to change its phase to closed. The Incident is given as an argument.
def closeIncident(incident):
    return sendClosureToSM(incident.toJsonObject())

#Sends an already existing incident (as a json string given as argument) to SM in order to change its status as closed.
def sendClosureToSM(incidentJson):
    response = requests.put(URL_INCIDENT+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=BOT_AUTH)
    if response.status_code >= 300:
        raise Exception ('Unable to connect to SM')
    return response.json()

#Performs a single request to SM Server to check if its available. Returns True if the server is reachable, False otherwise
def checkSMAvailability():
    try:
        response = requests.get(URL_OPERATOR+'bot',auth = BOT_AUTH)
        return response.status_code < 300
    except Exception:
        return False

#Performs a request to SM Server trying to discover if an Incident exists, given its ID.
def validateIncident(incidentId):
    if incidentId.lower() == '!exit':
        return True
    response = requests.get(URL_INCIDENT+incidentId,auth = BOT_AUTH)
    return response.json()['ReturnCode'] == 0

#Performs a request to SM Server trying to get an Incident, given its ID.
#Returns an Incident with the values of the Incident stored in SM Server
def getIncident(incidentId):
    response = requests.get(URL_INCIDENT+incidentId,auth = BOT_AUTH)
    incident = Incident(response.json()['Incident']['Contact'],response.json()['Incident']['Title'],response.json()['Incident']['Description'][0],response.json()['Incident']['Service'],response.json()['Incident']['Impact'],response.json()['Incident']['Urgency'],response.json()['Incident']['IncidentID'],response.json()['Incident']['Phase'])
    return incident

#Performs a request to SM Server trying to get an Incident as a Json string, given its ID.
#Returns an Incident with the values of the Incident stored in SM Server
def getIncidentData(incidentId):
    return requests.get(URL+'/incidents/'+incidentId,auth = HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS"))).json()

#Validates the list of the Incident fields to be updated. Returns True only if all the values provided are in the allowed values list.
def validateFieldsList(valuesString):
    providedValuesList = getFieldValuesList(valuesString)
    allowedValuesList = ['operator','title','description','impact','severity','!exit']
    for value in providedValuesList:
        if value not in allowedValuesList:
            return False
    return True

#Transform the string with the fields to be updated into a list, removing unnecesary spaces.
def getFieldValuesList(valuesString):
    return list(set(valuesString.replace(" ","").lower().split(",")))

#Validates the closure code provided as argument. A closure code is only valid if its value is between 0 and 12
def validateClosureCode(closureCode):
    if closureCode.lower() == '!exit':
        return True
    else:
        try:
            return int(closureCode) >= 0 and int(closureCode) <13
        except Exception:
            return False

#Return the string associated to a closure code provided as argument.
def getClosureCode(closureCode):
    closureCodesList = ['Diagnosed Succesfully','No Fault Found','No User Response','Not Reproducible','Out of Scope','Request Rejected','Resolved Succesfully','Unable to Solve','Withdrawn by User','Automatically Closed','Solved by Change/Service Request','Solved by User Instruction','Solved by Workaround']
    return str(closureCodesList[int(closureCode)])

#Validates a given list of KPIs to be recovered from SM. The kpi list is given as a string. a KPI list is valid if it contains an asterisk or numbers between 0 and 11
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

#Transforms the kpi string list provided into a real list, get each one from Service Manager Server, and return them as a list.
def getKpis(kpis):
    staticKpiList = ['Average group reassignments','Average number of incidents solved per employee daily','Average days between Incident opening and closure','Number of incidents closed' 
    ,'Number of incidents closed this month','Number of incidents daily closed this month','Number of incidents created this month','Average number of incidents created daily this month','Number of incidents solved','Most common Incident priority','Percentage of critical Incidents','Percentage of Incidents escalated']
    kpiList = list(set(kpis.replace(" ","").lower().split(',')))
    kpis = list()
    if '*' in kpiList:
        for kpiName in staticKpiList:
            kpis.append(getLatestKpi(kpiName))
    else:
        for kpiNumber in kpiList:
            kpis.append(getLatestKpi(staticKpiList[int(kpiNumber)]))
    return list(set(kpis))

#Request SM Server for a kpi given as argument. Always get the last KPI stored in the server
def getLatestKpi(kpiName):
    response = requests.get(URL_KPI+kpiName+'&sort=date:descending',auth = BOT_AUTH)
    latestKpi = response.json()['content'][0]['KPI']  #The latest kpi is always the first one in the JsonArray, as it's sorted
    return Kpi(latestKpi['Name'],latestKpi['Value'],latestKpi['Last_update'])

#Check if the finish message (wether to continue or not updating Incidents/getting KPIs) is valid. Only 'yes' and 'no' values are allowed.
def validateFinishMessage(finishMessage):
    return finishMessage.lower() == 'yes' or finishMessage.lower() == 'no'

        
