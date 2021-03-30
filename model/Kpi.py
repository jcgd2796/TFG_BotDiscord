import json

class Kpi:
    def __init__(self, name, value, date):
        self.name = name
        self.value = value
        self.date = date

    def getName(self):
        return self.name

    def getValue(self):
        return self.value

    def getDate(self):
        return self.date

    def toJsonObject(self):
        return json.loads("{\"KPI\": {\"Name\": \""+getName()+"\",\"Value\": [\""+getValue()+"\"],\"Date\": \""+getDate()+"\"}}")

        