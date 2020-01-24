
class ScheduleHelper:

    def __init__(self, logger):
        self.logger=logger
    
    def findNurseByName(self, name): #->move to helper
        for nurse in self.nurses:
            if nurse.name == name:
                return nurse
                
    def findDuties(self, nurseRow, dN): #->move to helper
        i = 0
        duties = []
        for child in nurseRow:
            if child.text == dN:
                duties.append(i)
            i+=1
        return duties
        
    def findHolidays(self, nurseRow):#->move to helper
        m = ""
        if len(str(self.month)) == 1:
            m = "0" + str(self.month)
        else:
            m = str(self.month)
        i = 0
        duties = []
        self.logger.info("Found elements: " + str(len(nurseRow)))
        for child in nurseRow:
            if child.text != None:
                if child.text.find("U") != -1:
                    d = ""
                    if len(str(i)) == 1:
                        d = "0" + str(i)
                    else:
                        d = str(i)
                    duties.append(d + "." + m)
                i+=1
        return duties
    
    def isAlreadyAssigned(self, nurse, duty): 
        for aNurse in duty.nurses:
            if nurse.name == aNurse.name:
                self.logger.info("Nurse already assigned to duty")
                return True
        return False
        
    def logPreviousWeek(self, duty): #is it really needed? maybe helper or logger wrapper
        self.logger.debug("DUTY " + str(duty.day) + " " +duty.type + " has been planned already")
        self.logger.debug("NURSES: ")
        for nurse in duty.nurses:
            self.logger.debug(nurse.name)
            
    def findFirstDailyDutyWithThreeNursesAssigned(self, nurse, duties):
        for duty in duties:
            self.logger.debug("ScheduleHelper: findFirstDailyDutyWithThreeNursesAssigned " + duty.printDuty())
            if duty.type == "D" and len(duty.nurses) == 3 and len(duty.partialNurses) == 0 and not self.isAlreadyAssigned(nurse, duty) and duty.dayName != 'sobota':
                return duty
    