from Duty import *
from Global import *
import calendar
from datetime import datetime
from ScheduleHelper import *
class Schedule:

    def __init__(self, logger, month, nurseIface):
        self.logger = logger
        self.month = month
        self.monthId = MONTHS.index(self.month)+1
        self.monthIndex = self.monthId-1
        self.nif = nurseIface
        self.nurses = self.nif("GET_NURSES")
        self.helper = ScheduleHelper(self.logger)
        self.duties = []
        self.saturdays = []
        self.sundays = []
        self.createMonth()
    
    def createMonth(self):
        self.createDutyTemplates()
        self.getBankHolidays()
        self.getNotWorkingDays()
    
    def createDutyTemplates(self):
        self.year = int(datetime.now().strftime('%Y'))
        self.logger.info("Schedule: createDutyTemplates: for days: " + str(MONTHS_DETAILED[self.monthIndex][1]))
        for i in range(MONTHS_DETAILED[self.monthIndex][1]):
            self.logger.debug("Schedule: createDutyTemplates: " + str(i))
            self.duties.append(Duty(i+1, self.monthId, self.year, "D"))
            self.duties.append(Duty(i+1, self.monthId, self.year, "N"))
            self.logger.info("Duty date name: " + str(self.duties[-1].getDayName()))
    
    def tryToCreateDuty(self, day, nurseId, month, value, oldValue):
        duty = Duty(day, month, self.year, value)
        nurse = self.nif("GET_NURSES")[nurseId]
        if oldValue == "N" or oldValue == "D":
            nurse.removeDuty(duty.day)
        result = self.validateNurse(nurse, duty)
        nurse.addDuty(duty.day, duty.type, duty.dayName)
        
        
        if result[0]:
            self.logger.info("Schedule: tryToCreateDuty: validation done successfully")
            
                
        #modyfiedDuty = self.helper.getDutyByDay(day, self.duties)
        #cloned = modyfiedDuty.clone()
        #cloned.signOffNurse(nurse)
        #result = self.validateDuty(cloned)
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
    
   
    
    def isAlreadyAssigned(self, nurse, duty):
        for nur in duty.nurses:
            if nur.name == nurse.name:
                return True
        return False
    
    def addHolidayForNurse(self, nurseId, day):
        self.logger.info("Schedule: addHolidayForNurse: " + str(nurseId) + " in day " + str(day))
        self.nif("GET_NURSES")[nurseId].addHolidays(str(day)+ "." + str(self.month))
        
    def removeDutyForNurse(self, nurseId, day):
        self.logger.info("Schedule: removeDutyForNurse: " + str(nurseId) + " in day " + str(day))
        self.nif("GET_NURSES")[nurseId].removeDuty(day)
        
    def checkSundays(self, nurse, day):
        if day != 'niedziela':
            return False
        self.logger.debug("checkSundays" + str(len(self.sundays)) + " nurse Sundays " + str(nurse.sundays))
        if len(self.sundays) - nurse.sundays == 1:
            return True
        return False
        
    def calculateHours(self): #refactor and move to schdule
        self.logger.info("ScheduleTab: calculateHours: calculated SUNDAYS: " + str(len(self.sundays)))
        self.logger.info("ScheduleTab: calculateHours: calculated SATURDAYS: " + str(len(self.saturdays)))
        self.workingDays = MONTHS_DETAILED[self.monthIndex][1] - len(self.saturdays)- len(self.sundays) - len(self.getBankHolidaysInMonth())
        
        self.logger.info("ScheduleTab: calculateHours: calculated WORKING DAYS: " + str(self.workingDays))
        for nurse in self.nurses:
            self.logger.info("Nurse timejob is " + str(nurse.timejob))
            if float(nurse.timejob) == 1.0 or float(nurse.timejob) == 0.5:
                nurse.hours = round((float(self.workingDays) * float(nurse.timejob) * 7.5833333333 - (len(nurse.holidays)*7.5833333333)), 2)
                self.logger.info("Nurse: " + nurse.name + " should work in this month for " + str(nurse.hours))
        self.nursesCalculated = True
        
          
    def getBankHolidays(self): 
        f = open("DniWolne.txt", "r")
        self.bankHolidays = f.readlines()
        f.close()
    
    def getNotWorkingDays(self):
        matrix = calendar.monthcalendar(self.year, self.monthId)
        for i in range(len(matrix)):
            if matrix[i][5] != 0:
                self.saturdays.append(matrix[i][5])
            if matrix[i][6] != 0:
                self.sundays.append(matrix[i][6])
        
    
    def getBankHolidaysInMonth(self):
        holidays= []
        monthIdStr = ""
        if self.monthId < 10:
           monthIdStr = "0" + str(self.monthId)
        for holiday in self.bankHolidays:
            if holiday.split(".")[1].find(monthIdStr) != -1:
                holidays.append(holiday)
        for holiday in holidays:
            self.logger.debug("Holiday in " + monthIdStr + ": " + holiday)
        return holidays
    
    def isNotWorkingDay(self, day):
        if day in self.saturdays or day in self.sundays:
            return True
        return False
    
    def setContractors(self, dutiesToBePlanned):
        j = 0
        for duty in dutiesToBePlanned:
            self.logger.info("\nSchedulling day " + str(duty.day) + " " + duty.type)
            times = 0
            while len(duty.nurses) < 3:
                if j < len(self.nurses):
                    if float(self.nurses[j].timejob) == 0.0 and self.nurses[j].checkAvailability:
                        self.nurses[j].addDuty(duty.day, duty.type, duty.dayName)
                        duty.nurses.append(self.nurses[j])
                        self.logger.info(self.nurses[j].name + " assigned to duty in " + str(duty.day) + " " + duty.type)
                    j += 1    
                else:
                    self.logger.info("Nurse list is already finished")
                    j = 0
                    times += 1
                    if times == 2:
                        self.logger.debug("Times = 2")
                        if len(duty.nurses) != 3:
                            self.logger.error("For this day it was not possbile to assign nurse")
                        
    def getDuty(self, day, type): 
        for duty in self.duties:
            if int(duty.day) == int(day) and str(duty.type) == str(type):
                return duty
                
    def getWeekRange(self, day):
        self.logger.debug("Get week range for day " + str(day))
        if day > 1 and day < 8:
            return (1, 7)
        elif day > 7 and day < 15:
            return (8, 14)
        elif day > 14 and day < 22:
            return (15, 21)
        elif day > 21 and day < 29:
            return (22, 28)
        else:
            return (29, self.duties[-1].day)
        
    def schedule(self):
        self.calculateHours()
        #self.setContractors()
        j = 0
        notFinished = []
        for i in range(len(self.duties)):
            self.helper.logPreviousWeek(self.duties[i-1])
            self.logger.info("\nSchedulling day " + str(self.duties[i].day) + " " + self.duties[i].type)
            times = 0
            while len(self.duties[i].nurses) < 3 and times < 3:
                if j < len(self.nurses):
                    if self.validateNurse(self.nurses[j], self.duties[i])[0]:                              #HERE MUST BE [0]
                        self.nurses[j].addDuty(self.duties[i].day, self.duties[i].type, self.duties[i].dayName)
                        self.duties[i].nurses.append(self.nurses[j])
                        self.logger.info(self.nurses[j].name + " assigned to duty in " + str(self.duties[i].day) + " " + self.duties[i].type)
                    j += 1    
                else:
                    self.logger.info("Nurse list is already finished")
                    j = 0
                    times += 1
                    if times == 2:
                        self.logger.debug("Times = 2")
                        if len(self.duties[i].nurses) != 3:
                            self.logger.warning("For this day it was not possbile to assign nurse")
                            notFinished.append(self.duties[i])
            
        self.logger.info("Planning Done")
        if len(notFinished) != 0:
            self.logger.error("There are not secured duties")
            for duty in notFinished:
                self.logger.error("Duty: " + str(duty.day) + " " + duty.type)
           # self.planRestNursesHours(notFinished)
        self.planRestNursesHours()
        self.setContractors(notFinished)
            
    def planRestNursesHours(self): 
        for nurse in self.nurses:
            if nurse.getUnplannedHours() != 0:
                duty = self.helper.findFirstDailyDutyWithThreeNursesAssigned(nurse, self.duties)
                self.logger.info("Schedule: planRestNursesHours: duty which was found: " + str(duty.day))
                nurse.addDuty(duty.day, "DX", duty.dayName)
                duty.partialNurses.append(nurse)
                
    
    
       
        
    