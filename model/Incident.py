
class Incident:
    def __init__(self,operator,title,description,ci,impact,severity):
        self.operator = operator
        self.title = title
        self.description = description
        self.ci = ci
        self.impact = impact
        self.severity = severity

    def toJsonObject(self):
        return "{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}"
