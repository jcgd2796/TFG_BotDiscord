'''controller.py
Controller of the bot. Validates the values introduced by the user and communicates with Service Manager Server
Author:
    Juan Carlos Gil Dïaz'''
import os
import sys
sys.path.append('/home/jcarlos/TFGDiscordBot') # root folder of the project, to enable imports
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
ALLOWED_FIELDS_LIST = ['operator','title','description','impact','severity','!exit']
CLOSURE_CODES_LIST = ['Diagnosed Succesfully','No Fault Found','No User Response','Not Reproducible','Out of Scope','Request Rejected','Resolved Succesfully','Unable to Solve','Withdrawn by User','Automatically Closed','Solved by Change/Service Request','Solved by User Instruction','Solved by Workaround']
ALLOWED_KPI_LIST = ['Average group reassignments','Average number of incidents solved per employee daily','Average days between Incident opening and closure','Number of incidents closed','Number of incidents closed this month','Number of incidents daily closed this month','Number of incidents created this month','Average number of incidents created daily this month','Number of incidents solved','Most common Incident priority','Percentage of critical Incidents','Percentage of Incidents escalated']

'''Validates an operator login given as argument exists in SM server.
Returns True if there's an operator with that login in SM, of if the user wants to cancel the process. False otherwise.
Args:
    login: the login name to validate. Must be a string and cannot be None
Exceptions thrown:
    ValueError: if the login is None
    Exception: if there's a problem while connecting SM
Return:
    True if an operator with that login exists in Service Manager, or if the string is "!exit". False otherwise'''

def validateLogin(login):
    if login == None:
        raise ValueError('Login is None')
    elif login.lower() == '!exit':
        return True
    else:
        response = requests.get(URL_OPERATOR+login,auth = BOT_AUTH)
        if (response.status_code >= 300):
            raise Exception('Unable to connect to SM')
        elif (response.json()['@count']==0):
            return False
        else:
            return True

'''Get an operator name from its login, given as argument.
Connects to Service Manager to get the name of the operator. This method should be used only after ensuring that validateLogin returns True and the
given login is not "!exit".
Args:
    login: the login name belonging to the operator we want to get. Must be a string, cannot be None, and must return True if given as argument for validateLogin.
Exceptions thrown:
    ValueError: if the login is None, or it's not valid
Return:
    The operator as a Json string, or "!exit" if that was the argument introduced'''
def getOperatorName(login):
    if login == None or not validateLogin(login):
        raise ValueError('Login is None, or it is not valid')
    elif login.lower() == '!exit':
        return login.lower()
    else:
        return requests.get(URL_OPERATOR+login,auth = BOT_AUTH).json()['content'][0]['Operator']['contact.name']

'''Validates the Incident title/description introduced by the user. An incident title/description is valid only if it has more than 10 characters.
Args:
    title: the title of the incident to be created. Must be a string and cannot be None
Exceptions thrown:
    ValueError: if the title is None
Return:
    True if the title has more than 10 characters, false otherwise'''
def validateTitle(title):
    if title == None:
        raise ValueError('title is None')
    elif title.lower() == '!exit':
        return True
    else: 
        return len(title) > 10

'''Validates the Incident CI introduced by the user. A CI is valid if its name is in SM CIs table
Args:
    ci: the Configuration Item name belonging to the CI we want to assign to the Incident. Must be a string and cannot be None
Exceptions thrown:
    ValueError: if the ci is None
Return:
    True if the ci is "!exit" or if there's a CI with that name in SM, false otherwise.'''
def validateCI(ci):
    if ci == None:
        raise ValueError('Affected CI is None')
    if ci.lower() == '!exit':
        return True
    response = requests.get(URL_CI+ci,auth = BOT_AUTH)
    return (response.status_code < 300) and (response.json()['@count'] > 0)

'''Get a CI from its name, given as argument.
Connects to Service Manager to get the CI as a Json String. This method should be used only after ensuring that validateCI returns True and the
given CI was not "!exit".
Args:
    name: the name of the CI to be assigned to the Incident. Must be a string, cannot be None and must return True if passed as argument for the validateCI method
Exceptions thrown:
    ValueError: if the name is None or if it's not valid
Return:
    The value of the CI as a Json string, or "!exit" if that was the introduced value'''
def getCI(name):
    if name == None or not validateCI(name):
        raise ValueError('name is None or it is not valid')
    elif name.lower() == '!exit':
        return name.lower()
    else:
        return requests.get(URL_CI+name,auth=BOT_AUTH).json()

'''Validates the Incident impact or severity values introduces by the user. An impact/Severity value is only valid
if it's a number between 2 and 4.
Args:
    impact: the impact value to be assigned to the Incident. Must be a string representing an integer between 2 and 4.
Exceptions thrown:
    ValueError: if the impact value is None or if it cannot be parsed to an integer
Return:
    True if the impact is "!exit" or a number between 2 and 4, False otherwise.'''
def validateImpact(impact):
    if impact == None:
        raise ValueError('The impact is None')
    elif impact.lower() == '!exit':
        return True
    else:
        try:
            return (int(impact) > 1 and int(impact) < 5) 
        except ValueError:      #NaN
            return False

'''Creates an Incident object with the operator's name, and Incident title, description, affected CI, impact and severity values provided as arguments
#After that, gets it as a Json String, and submits it to Service Manager Server.
Args:
    operator: the name of the operator to be assigned to the Incident. Must be a string and cannot be None.
    title: the title for the Incident. Must be a string and cannot be None.
    description: the description for the Incident. Must be a string and cannot be None
    ci: the name of the affected CI. Must be a string and cannot be None.
    impact: the impact value for the Incident. Must be a string representing an integer between 2 and 4
    severity: the severity value for the Incident. Must be a string representing an integer between 2 and 4
Exceptions thrown:
    ValueError: if any of the args is None or if the impact or severity values are not valid
Return:
    The response of SM Server as a Json string'''
def createIncident(operator,title,description,ci,impact,severity):
    if (operator == None or title == None or description == None or ci == None or impact == None or severity == None or not validateImpact(impact) or not validateImpact(severity)):
        raise ValueError('At least one arg is None, or the severity/impact values are not valid.')
    else:
        incident = Incident(operator,title,description,ci,impact,severity,None,'Log')
        incidentJson = incident.toJsonObject()
        response = sendToSM(json.dumps(incidentJson))
        return response

'''Submit an Incident given as argument to SM.
Args:
    incidentJson: the incident as a Json string. Cannot be None
Exceptions thrown:
    ValueError: if incidentJson is None
    Exception: if unable to connect to SM
Return:
    The response of SM Server as a Json string'''
def sendToSM(incidentJson):
    if incidentJson == None:
        raise ValueError('incidentJson is None')
    else:
        response = requests.post(URL+"/incidents",data=incidentJson,auth=BOT_AUTH)
        if response.status_code >= 300:
            raise Exception ('Unable to connect to SM')
        return response.json()

'''Transforms an Incident to a Json String and sends it to SM Server to update its values. The Incident is given as an argument.
Args:
    incident: the incident as an Incident object. Cannot be None
Exceptions thrown:
    ValueError: if incident is None
Return:
    The response of SM Server as a Json string'''
def updateIncident(incident):
    if incident == None:
        raise ValueError('incident is None')
    else:
        response = sendUpdateToSM(incident.toJsonObject())
        return response

'''Sends an Incident (as a Json string) given as argument to SM Server to save it on its database.
Args:
    incidentJson: the incident to update as a Json string. Cannot be None
Exceptions thrown:
    ValueError: if incidentJson is None
    Exception: if unable to connect to SM
Return:
    The response of SM Server as a Json string'''
def sendUpdateToSM(incidentJson):
    if incidentJson == None:
        raise ValueError('incidentJson is None')
    else:
        response = requests.put(URL_INCIDENT+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=BOT_AUTH)
        if response.status_code >= 300:
            raise Exception ('Unable to connect to SM')
        return response.json()

'''Transforms an Incident to a Json String and sends it to SM Server to change its phase to closed. The Incident is given as an argument.
Args:
    incident: the incident as an Incident object string. Cannot be None
Exceptions thrown:
    ValueError: if incident is None
Return:
    The response of SM Server as a Json string'''
def closeIncident(incident):
    if incident == None:
        raise ValueError('incident is None')
    else:
        return sendClosureToSM(incident.toJsonObject())

'''Sends an already existing incident (as a json string given as argument) to SM in order to change its status as closed.
Args:
    incidentJson: the incident as a Json string. Cannot be None
Exceptions thrown:
    ValueError: if incidentJson is None
    Exception: if unable to connect to SM
Return:
    The response of SM Server as a Json string'''
def sendClosureToSM(incidentJson):
    if incidentJson == None:
        raise ValueError('incident is None')
    else:
        response = requests.put(URL_INCIDENT+incidentJson['Incident']['IncidentID'],data=json.dumps(incidentJson),auth=BOT_AUTH)
        if response.status_code >= 300:
            raise Exception ('Unable to connect to SM')
        return response.json()

'''Performs a single request to SM Server to check if its available. 
Return:
    True if the server is reachable, False otherwise'''
def checkSMAvailability():
    try:
        response = requests.get(URL_OPERATOR+'bot',auth = BOT_AUTH)
        return response.status_code < 300
    except Exception:
        return False

'''Performs a request to SM Server trying to discover if an Incident exists, given its ID.
Args:
    incidentId: the incident ID as a string. Cannot be None
Exceptions thrown:
    ValueError: if incidentId is None
    Exception: if unable to connect to SM
Return:
    True if incidentId is "!exit" or if there's an existing Incident with that ID in SM server, False otherwise'''
def validateIncident(incidentId):
    if incidentId == None:
        raise ValueError('incidentId is None')
    elif incidentId.lower() == '!exit':
        return True
    else:
        response = requests.get(URL_INCIDENT+incidentId,auth = BOT_AUTH)
        if response.status_code >= 300:
                raise Exception ('Unable to connect to SM')
        return response.json()['ReturnCode'] == 0

'''Performs a request to SM Server trying to get an Incident, given its ID.
Returns an Incident with the values of the Incident stored in SM Server
Args:
    incidentId: the incident ID as a string. Cannot be None and must return True when given as an argument for validateIncident method
Exceptions thrown:
    ValueError: if incidentId is None
    Exception: if unable to connect to SM
Return:
    The Incident as an Incident Object if there's an Incident with that ID in SM, "!exit" if the arg was "!exit"'''
def getIncident(incidentId):
    if incidentId == None:
        raise ValueError('IncidentId is None')
    if incidentId.lower() == '!exit':
        return incidentId.lower()
    else:
        response = requests.get(URL_INCIDENT+incidentId,auth = BOT_AUTH)
        if response.status_code >= 300:
                raise Exception ('Unable to connect to SM')
        incident = Incident(response.json()['Incident']['Contact'],response.json()['Incident']['Title'],response.json()['Incident']['Description'][0],response.json()['Incident']['Service'],response.json()['Incident']['Impact'],response.json()['Incident']['Urgency'],response.json()['Incident']['IncidentID'],response.json()['Incident']['Phase'])
        return incident

'''Performs a request to SM Server trying to get an Incident as a Json string, given its ID.
Returns an Incident with the values of the Incident stored in SM Server
Args:
    incidentId: the incident ID as a string. Cannot be None and must return True when given as an argument for validateIncident method
Exceptions thrown:
    ValueError: if incidentId is None
    Exception: if unable to connect to SM
Return:
    The Incident as a Json string if there's an Incident with that ID in SM, "!exit" if the arg was "!exit"'''
def getIncidentData(incidentId):
    if incidentId == None:
        raise ValueError('IncidentId is None')
    if incidentId.lower() == '!exit':
        return incidentId.lower()
    response = requests.get(URL_INCIDENT+incidentId,auth = BOT_AUTH)
    if response.status_code >= 300:
        raise Exception ('Unable to connect to SM')
    else:
        return response.json()

'''Validates the list of the Incident fields to be updated. Returns True only if all the values provided are in the allowed values list.
Args:
    valuesString: the values to check as a string of values separated by comma. Cannot be None.
Exceptions thrown:
    ValueError: if valuesString is None
Return:
    True only if all the values provided are in the allowed values list'''
def validateFieldsList(valuesString):
    if valuesString == None:
        raise ValueError('valuesString is None')
    else:
        providedValuesList = getFieldValuesList(valuesString)
        for value in providedValuesList:
            if value not in ALLOWED_FIELDS_LIST:
                return False
        return True

'''Transform the string with the fields to be updated into a list, removing unnecesary spaces.
Args:
    valuesString: the values to transform to a list. Must be a string of values separated by comma. Cannot be None.
Exceptions thrown:
    ValueError: if valuesString is None
Return:
    A list with the values, using the comma as the separator, without duplicates'''
def getFieldValuesList(valuesString):
    if valuesString == None:
        raise ValueError('valuesString is None')
    else:
        return list(set(valuesString.replace(" ","").lower().split(",")))

'''Validates the closure code provided as argument. A closure code is only valid if its value is between 0 and 12
Args:
    closureCode: the closure code value. Must be a string representing an integer between 0 and 12. Cannot be None.
Exceptions thrown:
    ValueError: if closureCode is None
Return:
    True if closureCode integer value is between 0 and 12, False otherwise'''
def validateClosureCode(closureCode):
    if closureCode == None:
        raise ValueError('ClosureCode is None')
    elif closureCode.lower() == '!exit':
        return True
    else:
        try:
            return int(closureCode) >= 0 and int(closureCode) <13
        except Exception: #NaN
            return False

'''Return the string associated to a closure code provided as argument.
Args:
    closureCode: the closure code value. Must be a string representing an integer between 0 and 12. Cannot be None.
Exceptions thrown:
    ValueError: if closureCode is None or if it cannot be parsed to integer
Return:
    The closure code text associated with the number entered.'''
def getClosureCode(closureCode):
    if closureCode == None:
        raise ValueError('closureCode is None')
    else:
        try:
            return str(CLOSURE_CODES_LIST[int(closureCode)])
        except ValueError:
            raise ValueError('closureCode cannot be parsed to integer')

'''Validates a given list of KPIs to be recovered from SM. The kpi list is given as a string. a KPI list is valid if it contains an asterisk or numbers between 0 and 11
Args:
    kpis: the list of kpi numbers to get. Must be a string of numbers between 0 and 11 separated by comma. Can include asterisk or "!exit" values.
Exceptions thrown:
    ValueError: if kpis is None
Return:
    True if the list contains only numbers from 0 to 11, asterisk or "!exit" string, False otherwise'''
def validateKpiList(kpis):
    if kpis == None:
        raise ValueError('kpis is None')
    else:
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
            except ValueError: #NaN
                return False

'''Transforms the kpi string list provided into a real list, get each one from Service Manager Server, and return them as a list.
Args:
    kpis: the list of kpi numbers to get. Must be a string of numbers between 0 and 11 separated by comma. Can include asterisk or "!exit" values. 
    Must return True when passed as an argument for validateKpiList method
Exceptions thrown:
    ValueError: if kpis is None or if it isn't valid (ValidateKpiList returns False)
Return:
    True if the list contains only numbers from 0 to 11, asterisk or "!exit" string, False otherwise'''
def getKpis(kpis):
    if kpis == None or not validateKpiList(kpis):
        raise valueError('kpis is None, or it is not valid')
    else:
        kpiList = list(set(kpis.replace(" ","").lower().split(',')))
        kpis = list()
        if '*' in kpiList:
            for kpiName in ALLOWED_KPI_LIST:
                kpis.append(getLatestKpi(kpiName))
        else:
            for kpiNumber in kpiList:
                kpis.append(getLatestKpi(ALLOWED_KPI_LIST[int(kpiNumber)]))
        return list(set(kpis))

'''Request SM Server for a kpi given as argument. Always get the last KPI stored in the server
Args:
    kpiName: the name of the KPI to get. Must be a string with a value inside the allowed kpi list
    The allowed KPI list is: 'Average group reassignments','Average number of incidents solved per employee daily','Average days between Incident opening and closure','Number of incidents closed' 
        ,'Number of incidents closed this month','Number of incidents daily closed this month','Number of incidents created this month','Average number of incidents created daily this month',
        'Number of incidents solved','Most common Incident priority','Percentage of critical Incidents','Percentage of Incidents escalated'
Exceptions thrown:
    ValueError: if kpiName is None or if it's not in the allowed list
    Exception: if unable to connect to SM
Return:
    The requested KPI as a KPI object'''
def getLatestKpi(kpiName):
    if kpiName == None or kpiName not in ALLOWED_KPI_LIST:
        raise ValueError('kpiName is None or not valid')
    else:
        response = requests.get(URL_KPI+kpiName+'&sort=date:descending',auth = BOT_AUTH)
        latestKpi = response.json()['content'][0]['KPI']  #The latest kpi is always the first one in the JsonArray, as it's sorted
        if latestKpi.status_code >= 300:
            raise Exception ('Unable to connect to SM')
        else:
            return Kpi(latestKpi)

'''Check if the finish message (wether to continue or not updating Incidents/getting KPIs) is valid. Only 'yes' and 'no' values are allowed.
Args:
    finishMessage: the message to check. Must be a string and cannot be None
Exceptions thrown:
    ValueError: if finishMessage is None
Return:
    True if finishMessage is 'yes' or 'no' (or variants with upper case). False otherwise'''
def validateFinishMessage(finishMessage):
    if finishMessage == None:
        raise ValueError('finishMessage is None')
    return finishMessage.lower() == 'yes' or finishMessage.lower() == 'no'
