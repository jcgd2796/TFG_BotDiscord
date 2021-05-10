'''Incident.py
Model class representing Incident objects
An Incident has an operator, a title, a description, an affected CI, an impact and severity value, and Id and a phase.
Author:
    Juan Carlos Gil Dïaz'''
import json

class Incident:
    '''Constructor for the Incident.
    Args:
        operator: the name of the operator that will be associated to the Incident. Must be a string different from None.
        title: the title of the Incident. Must be a string different from None
        description: the description of the Incident. Must be a string different from None
        ci: the name of the affected CI of the Incident. Must be a string different from None
        impact: the impact value of the Incident. Must be a string different from None, representing an integer between 2 and 4
        severity: the severity value of the Incident. Must be a string different from None, representing an integer between 2 and 4
        incidentId: the Incident ID. Must be a string, can be None
        phase: the name of the phase the Incident is in. Must be a string different from None
    Exceptions:
        valueError if any of the arguments (except incidentID) are None or if the impact/severity values cannot be parsed to integers or are out of range.
        '''
    def __init__(self, operator, title, description, ci, impact, severity, incidentID, phase):
        if operator == None or title == None or description == None or ci == None or impact == None or severity == None or phase == None:
            raise ValueError('at least one argument (not including the incidentID) is None')
        else:
            try:
                if int(impact) <2 or int (impact) >4 or int (severity) <2 or int(severity) > 4:
                    raise ValueError('impact or severity values out of range')
            except ValueError:
                raise ValueError('impact or severity values cannot be parsed to integers')
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

    '''
    Sets a new operator name for the Incident
    Args:
        newOperator: the new operator value. Must be a string different from None
    Exceptions:
        ValueError if newOperator is None'''
    def setOperator(self,newOperator):
        if newOperator == None:
            raise ValueError('newOperator is None')
        else:
            self.operator = newOperator

    '''
    Sets a new title for the Incident
    Args:
        newTitle: the new title value. Must be a string different from None
    Exceptions:
        ValueError if newTitle is None'''
    def setTitle(self,newTitle):
        if newTitle == None:
            raise ValueError('newTitle is None')
        else:
            self.title = newTitle

    '''
    Sets a new description for the Incident
    Args:
        newDescription: the new description value. Must be a string different from None
    Exceptions:
        ValueError if newDescription is None'''
    def setDescription(self,newDescription):
        if newDescription == None:
            raise ValueError('newDescription is None')
        else:
            self.description = newDescription

    '''
    Sets a new impact for the Incident
    Args:
        newImpact: the new impact value. Must be a string different from None, must be possible to parse it to integer, and its range must be between 2 and 4
    Exceptions:
        ValueError if newImpact is None or if it cannot be parsed to an integer, or is out of range'''
    def setImpact(self,newImpact):
        if newImpact == None:
            raise ValueError('newImpact is None')
        else:
            try:
                if int(newImpact) <2 or int (newImpact) >4:
                    raise ValueError('impact value out of range')
            except ValueError:
                raise ValueError('impact value cannot be parsed to integer')    
        self.impact = newImpact

    '''
    Sets a new severity for the Incident
    Args:
        newSeverity: the new severity value. Must be a string different from None, must be possible to parse it to integer, and its range must be between 2 and 4
    Exceptions:
        ValueError if newSeverity is None or if it cannot be parsed to an integer, or is out of range'''
    def setSeverity(self,newSeverity):
        if newSeverity == None:
            raise ValueError('newSeverity is None')
        else:
            try:
                if int(newSeverity) <2 or int (newSeverity) >4:
                    raise ValueError('severity value out of range')
            except ValueError:
                raise ValueError('severity value cannot be parsed to integer')    
        self.severity = newSeverity


    '''
    Sets a new solution for the Incident
    Args:
        newSolution: the new solution. Must be a string different from None
    Exceptions:
        ValueError if newSolution is None'''
    def setSolution(self,newSolution):
        if newSolution == None:
            raise ValueError('newSolution is None')
        else:
            self.solution = newSolution


    '''
    Sets a new closure code for the Incident
    Args:
        newCode: the new closure code value. Must be a string different from None.
    Exceptions:
        ValueError if newClosure is None'''
    def setClosureCode(self,newCode):
        if newCode == None:
            raise ValueError('newCode is None')
        else:
            self.closureCode = newCode

    '''
    Sets a new phase code for the Incident
    Args:
        newPhase: the new phase value. Must be a string different from None.
    Exceptions:
        ValueError if newPhase is None'''
    def setPhase(self,newPhase):
        if newPhase == None:
            raise ValueError('newPhase is None')
        else:
            self.phase = newPhase

    '''
    Returns the phase of the Incident
    Return:
        the phase of the Incident as a string'''
    def getPhase(self):
        return self.phase

    '''
    Returns the incident values as a Json string. The json string returned depends on the value of the Incident fields
    Return:
        The incident as a Json string'''
    def toJsonObject(self):
        if self.id == None:
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}")
        elif self.id != None and self.solution == "":
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"IncidentID\": \""+self.id+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Urgency\": \""+self.severity+"\"}}")
        else:
            return json.loads("{\"Incident\": {\"Category\": \"incident\",\"Contact\": \""+self.operator+"\",\"Description\": [\""+self.description+"\"],\"Impact\": \""+self.impact+"\",\"IncidentID\": \""+self.id+"\",\"Service\": \""+self.ci+"\",\"Title\": \""+self.title+"\",\"Status\":\"Resolved\",\"Phase\": \"Review\",\"Area\": \"failure\",\"Urgency\": \""+self.severity+"\",\"Solution\": [\""+self.solution+"\"],\"ClosureCode\":\""+self.closureCode+"\"}}")
