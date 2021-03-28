from model.Incident import *
import requests
import os
from requests.auth import HTTPBasicAuth
import dotenv
import json

dotenv.load_dotenv()

incident = Incident ("123","qwe","qwe","dev",'3','4',None)
incident2 = Incident ("123","qwe","qwe","dev",'3','4','IM123')
incident3 = Incident ("123","qwe","qwe","dev",'3','4','IM123')
incident3.setSolution('sol')
incident3.setClosureCode('code')

jsonIncident1 = incident.toJsonObject()
jsonIncident2 = incident2.toJsonObject()
jsonIncident3 = incident3.toJsonObject()
print (jsonIncident1)
print (jsonIncident2)
print (jsonIncident3)

