import json

class Incident:
    def __init__(self, operator, title, description, ci, impact, severity, incidentID, phase):
        self.operator = operator
        self.title = title
        self.description = description
        self.ci = ci
        self.impact = impact
        self.severity = severity
        self.id = incidentID
        self.solution = ""
        self.closureCode = ""
        self.phase = phase

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

    def setSolution(self,newSolution):
        self.solution = newSolution

    def setClosureCode(self,newCode):
        self.closureCode = newCode

    def setPhase(self,newPhase):
        self.phase = newPhase

    def getPhase(self):
        return self.phase

    def toJsonObject(self):
        if self.id == None:
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}")
        elif self.id != None and self.solution == "":
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"IncidentID\": \""+self.id+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}")
        else:
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"IncidentID\": \""+self.id+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Status\":\"Resolved\",\"Phase\": \"Review\",\"Area\": \"failure\",\"Urgency\": \""+self.severity+"\",\"Solution\": [\""+self.solution+"\"],\"ClosureCode\":\""+self.closureCode+"\"}}")
