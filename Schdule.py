from Duty import *
from Global import *

class Schedule:

    def __init__(self, logger, month, nurseIface):
        self.logger = logger
        self.month = month
        self.nif = nurseIface
        self.duties = []
        
    def createDutyTemplates(self):
        inx = MONTHS.index(self.month)
        self.logger.info("Schedule: createDutyTemplates: for days: " + str(MONTHS_DETAILED[inx][1]))
        for i in range(MONTHS_DETAILED[inx][1]):
            self.duties.append(Duty(i+1, self.month, self.year, "D"))
            self.duties.append(Duty(i+1, self.month, self.year, "N"))
            self.logger.info("Duty date name: " + str(self.duties[-1].getDayName()))
    
    def tryToCreateDuty(self, day, month, year, value):
        duty = Duty(day, month, year, value)
        result = self.validateNurse(self.nif("GET_NURSES")[row], duty)
        if not result[0]:
            self.nif("GET_NURSES")[row].addDuty(duty.day, duty.type, duty.dayName)
        return result
        
    def validateNurse(self, nurse, duty, withDuties=True):
        if withDuties:
            if not nurse.checkDuties():
                self.logger.info("Schedule: validate nurse: " + nurse.name + " has already overloaded")
                return [False, "Pielegniarka ma przypisane wszystkie możliwe dyżury"]
        if nurse.checkHoliday(duty):
            self.logger.info("Schedule: validate nurse:  " + nurse.name + " has planned holiday")
            return [False, "Pielegniarka ma zaplanowany urlop w tym dniu"]
        if not nurse.checkAvailability(duty.day):
            self.logger.info("Schedule: validate nurse:  " + nurse.name + " is not available at this day")
            return [False, "Pielegniarka jest nie dostępna w tym dniu"]
        if nurse.checkPreviousDay([duty.type, duty.day]):
            return [False, "Pielęgniarka ma inny dyzur dzień wcześniej. Zaplanowano całodobowy dyżur."]
        if self.isAlreadyAssigned(nurse, duty):
            return [False, "Pielegniarka ma inny dyżur w tym dniu"]
        if nurse.checkWeek(self.getWeekRange(duty.day)):
            return [False, "Pielegniarka przekracza maksymalna liczbę godzin w tygodniu"]
        if self.checkSundays(nurse, duty.dayName):
            self.logger.info("Schedule: validate nurse:  must have one free Sunday")
            return [False, "Pielegniarka musi mieć przynajmniej jedną niedziele wolna w miesiącu"]
        return [True, ""]
        
    def addHolidayForNurse(self, nurseId, day):
        self.logger.info("Schedule: addHolidayForNurse: " + str(nurseId) + " in day " + str(day))
        self.nif("GET_NURSES")[nurseId].addHolidays(str(day)+ "." + str(self.month))
        
    def removeDutyForNurse(self, nurseId, day):
        self.logger.info("Schedule: removeDutyForNurse: " + str(nurseId) + " in day " + str(day))
        self.nif("GET_NURSES")[nurseId].removeDuty(day)
        
        
        
    