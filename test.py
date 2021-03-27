from model.Incident import *
import requests
import os
from requests.auth import HTTPBasicAuth
import dotenv
import json

dotenv.load_dotenv()
url = os.getenv("URL")
inc = requests.get(url+'/incidents/IM10268',auth=HTTPBasicAuth('bot',os.getenv("BOT_OPERATOR_PASS"))).json()

print(inc['Incident']['IncidentID'])

#print(ci["content"]["Device"]["ConfigurationItem"])

