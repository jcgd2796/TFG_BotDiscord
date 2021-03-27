from model.Incident import *
import requests
import os
from requests.auth import HTTPBasicAuth
import dotenv
import json

dotenv.load_dotenv()

incident = Incident ("123","qwe","qwe","dev",3,4)
