'''Kpi.py
Model class representing KPI (Key Performance Indicator) objects
An KPI has a name, a value, and an obtained date.
Author:
    Juan Carlos Gil Dïaz'''
import json

class Kpi:
    '''Constructor for the KPI.
    Args:
        jsonKpi: the KPI as a Json string. Cannot be None
    Exceptions:
        valueError if jsonKpi is None
        '''
    def __init__(self, jsonKpi):
        if jsonKpi == None:
            raise ValueError('jsonKpi is None')
        self.name = jsonKpi['Name']
        self.value = jsonKpi['Value']
        self.date = jsonKpi['Last_update']

    '''
    Returns the name of the KPI
    Return:
        the name of the KPI as a string'''
    def getName(self):
        return self.name

    '''
    Returns the value of the KPI
    Return:
        the value of the KPI as a string'''
    def getValue(self):
        return self.value

    '''
    Returns the date of the KPI
    Return:
        the date of the KPI as a string'''
    def getDate(self):
        return self.date

    '''
    Returns the KPI values as a Json string.
    Return:
        The KPI as a Json string'''
    def toJsonObject(self):
        return json.loads("{\"KPI\": {\"Name\": \""+getName()+"\",\"Value\": [\""+getValue()+"\"],\"Date\": \""+getDate()+"\"}}")

    '''
    Returns the KPI date as a formatted string easilly legible in format DD/MM/YYYY.
    Return:
        The KPI date as a legible string in format DD/MM/YYYY'''
    def getFormattedDate(self):
        return self.date[8:10]+'/'+self.date[5:7]+'/'+self.date[0:4]+' '+self.date[11:16]

        
