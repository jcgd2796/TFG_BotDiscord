import json

class Incident:
    def __init__(self, operator, title, description, ci, impact, severity, incidentID):
        self.operator = operator
        self.title = title
        self.description = description
        self.ci = ci
        self.impact = impact
        self.severity = severity
        self.id = incidentID

    def setOperator(self,newOperator):
        self.operator = newOperator

    def setTitle(self,newTitle):
        self.title = newTitle

    def setDescription(self,newDescription):
        self.description = newDescription

    def setImpact(self,newImpact):
        self.impact = newImpact

    def setSeverity(self,newSeverity):
        self.severity = newSeverity

    def toJsonObject(self):
        if self.id == None:
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}")
        else:
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"IncidentID\": \""+self.id+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}")
