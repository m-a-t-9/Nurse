import datetime
import collections, copy
class Duty:

    def __init__(self, day, month, year, type):
        self.day = day
        self.month = month
        self.year = year
        self.type = type
        self.nurses = []
        self.partialNurses = []
        self.createDate()
        self.setDayName()
        self.hours = {}

    def clone(self):
        yield copy.deepcopy(self)

    def createDate(self):
        date_time_str = str(self.year) + "-" + str(self.month) + "-" + str(self.day)
        self.date = datetime.datetime.strptime(date_time_str, '%Y-%m-%d')

    def setDayName(self):
        self.dayName = self.date.strftime("%A")

    def getDayName(self):
        return self.dayName
        
    def signOffNurse(self, nurse):
        toRemove = None
        for nur in self.nurses:
            if nur.name == nurse.name:
                toRemove = nur
        if toRemove != None:
            self.nurses.remove(toRemove)
        else:
            for nur in self.partialNurses:
                if nur.name == nurse.name:
                    toRemove = nur
        if toRemove != None:
            self.nurses.remove(toRemove)        
        
    def printDuty(self):
        return str(self.day) + "." + str(self.month) + "." + str(self.year) + " " + self.dayName