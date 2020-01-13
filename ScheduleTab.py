import wx
import wx.lib.mixins.listctrl  as  listmix
import calendar
from datetime import datetime

from Duty import *
from HTMLExporter import *

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):
    ''' TextEditMixin allows any column to be edited. '''
 
    #----------------------------------------------------------------------
    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """Constructor"""
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

    

class ScheduleTab(wx.Panel):
    
    def __init__(self, parent, logger, nurseIface):
        wx.Panel.__init__(self, parent)
        self.page = 1
        self.logger = logger
        self.NIF = nurseIface
        self.getBankHolidays()
        self.nurses = []
        self.duties = []
        #self.createMonth()
        self.createListCTRL()
    
    def createMonth(self, month=None):
        self.year = int(datetime.datetime.now().strftime('%Y'))
        if month == None:
            self.month = int(datetime.datetime.now().strftime('%m')) + 1
            if self.month == 13:
                self.month = 1
                self.year += 1
            self.numberOfDays = calendar.monthrange(self.year, self.month)[1]
        else:
            self.month = month
            self.numberOfDays = calendar.monthrange(self.year, self.month)[1]
        for i in range(self.numberOfDays):
            self.duties.append(Duty(i+1, self.month, self.year, "D"))
            self.duties.append(Duty(i+1, self.month, self.year, "N"))
            self.logger.info("Duty date name: " + str(self.duties[-1].getDayName()))
        self.calculateSundaysInMonth()
           
    def calculateSundaysInMonth(self):
        matrix = calendar.monthcalendar(self.year,self.month)
        self.numberOfSundays= sum(1 for x in matrix if x[calendar.SUNDAY] != 0)
            
    def getOnlyDayDuties(self):
        r = []
        for duty in self.duties:
            if duty.type == "D":
                r.append(duty)
        return r
    
    def createListCTRL(self, month=None):
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        dutiesForColumn = self.getOnlyDayDuties()
        self.logger.info("ScheduleTab: createListCTRL: create calendar for days: " + str(dutiesForColumn))
        self.list = EditableListCtrl(self, style=wx.LC_REPORT)
        
        self.list.InsertColumn(0, "Imie i Nazwisko", width=150)
        i = 0
        
        for duty in dutiesForColumn:
            self.list.InsertColumn(i+1, str(i+1), width=30)
            i += 1
        if i != 0:
            self.list.InsertColumn(i+1, "Suma", width=60)
        idx = 0
        for nurse in self.nurses:
            index = self.list.InsertItem(idx, nurse.name)
            for duty in nurse.dailyDuties:
                self.list.SetItem(index, duty, "D")
            for duty in nurse.nightlyDuties:
                self.list.SetItem(index, duty, "N") 
            self.list.SetItem(index, len(dutiesForColumn)+1, str(nurse.getPlannedHours()))
            idx += 1
            
        self.applyChangesBtn = wx.Button(self, label='Zastosuj zmiany', size=(80, 20))
        self.calculateBtn = wx.Button(self, label='Uloz grafik', size=(80, 30))
        
        self.exportBtn = wx.Button(self, label="Zapisz do pliku", size=(80, 30))
        
        self.Bind(wx.EVT_BUTTON, self.OnApply, self.applyChangesBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCalculate, self.calculateBtn)
        self.Bind(wx.EVT_BUTTON, self.OnSave, self.exportBtn)
        
        self.hbox.Add(self.list, proportion=1, flag=wx.EXPAND)
        if self.list.GetItemCount() != 0:
            self.hbox.Add(self.applyChangesBtn)
        self.hbox.Add(self.calculateBtn)
        self.hbox.Add(self.exportBtn)
        self.SetSizer(self.hbox)
        self.Layout()    
        
    def OnApply(self, e):
        count = self.list.GetItemCount()
        cols = self.list.GetColumnCount()
        duties = []
        for row in range(count):
            nurseName = self.list.GetItem(row, col=0).GetText()
            #print("NurseName: " + nurseName)
            nurse = self.scheduler.getNurse(nurseName)
            nurse.nightlyDuties = []
            nurse.dailyDuties = []
            for col in range(1,cols):
                val = self.list.GetItem(row, col=col).GetText()
                if val == "D":
                    nurse.dailyDuties.append(col)
                elif val == "N":
                    nurse.nightlyDuties.append(col)
        #self.scheduler.printSchedules()
        #self.scheduler.validateSchedule()
   
    def OnSave(self, e):
        self.logger.info("Saving schedule")
        htmlExporter = HTMLExporter(self.list)
        htmlExporter.save()
        
   
    def OnCalculate(self, e):
        self.logger.info("ScheduleTab: OnCalculate")
        self.nurses = self.NIF("GET_NURSES")
        self.schedule()
        self.createListCTRL()
        
    def OnNew(self, month):
        self.createMonth(month=month)
        self.nurses = self.NIF("GET_NURSES")
        self.schedule()
        self.createListCTRL()
        
    def validateNurse(self, nurse, duty, withDuties=True):
        if withDuties:
            if not nurse.checkDuties():
                self.logger.info("NURSE " + nurse.name + " has already overloaded")
                return False
        if nurse.checkHoliday(duty):
            self.logger.info("NURSE " + nurse.name + " has planned holiday")
            return False
        if not nurse.checkAvailability(duty.day):
            self.logger.info("NURSE " + nurse.name + " is not available at this day")
            return False
        if nurse.checkPreviousDay([duty.type, duty.day]):
            return False
        if self.isAlreadyAssigned(nurse, duty):
            return False
        if nurse.checkWeek(self.getWeekRange(duty.day)):
            return False
        if self.checkSundays(nurse, duty.dayName):
            self.logger.info("Nurse must have one free Sunday")
            return False
        return True
            
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
        end = []
        damageCounter = 10000
        notFinished = []
        for i in range(len(self.duties)):
            self.logPreviousWeek(i)
            self.logger.info("\nSchedulling day " + str(self.duties[i].day) + " " + self.duties[i].type)
            times = 0
            while len(self.duties[i].nurses) < 3 and times < 3:
                if j < len(self.nurses):
                    if self.validateNurse(self.nurses[j], self.duties[i]):
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
            self.planRestNursesHours(notFinished)
            self.setContractors(notFinished)
            
    def planRestNursesHours(self, notPlannedDuties):
        nursesToBePlanned = []
        j=0
        for nurse in self.nurses:
            unplanned = nurse.getUnplannedHours()
            self.logger.debug("Nurse " + nurse.name + " has " + str(nurse.getUnplannedHours()) + " unplanned")
            if unplanned != 0.0:
                nursesToBePlanned.append(nurse)
        for duty in notPlannedDuties:
            if duty.type == "D" and len(duty.nurses) == 2:
                self.logger.info("Day to be splitted " + str(duty.day))
                hoursCounter = 7.00
                times = 0
                while hoursCounter < 19.00:
                    if j  < len(nursesToBePlanned):
                        if self.validateNurse(nursesToBePlanned[j], duty, withDuties=False):
                            end = hoursCounter + nursesToBePlanned[j].getUnplannedHours()
                            if end < 19.00:
                                self.logger.info("Planning duty " + str(duty.day) + " from " + str(hoursCounter) + " to " + str(end) + " for nurse " + nursesToBePlanned[j].name)
                                hoursCounter = end
                                duty.hours[(hoursCounter) + ":" + str(end)] = nursesToBePlanned[j]
                                nursesToBePlanned[j].shortDuties.append(duty)
                                nursesToBePlanned[j].hours += nursesToBePlanned[j].getUnplannedHours()
                        j += 1
                    else:
                        j = 0
                        times += 1
                        if times == 2:
                            self.logger.debug("Times = 2")
                            if len(duty.nurses) != 3:
                                self.logger.warning("For this day it was not possbile to assign nurse")
                                break
                            
                    
            
            

    
    def isAlreadyAssigned(self, nurse, duty):
        for aNurse in duty.nurses:
            if nurse.name == aNurse.name:
                self.logger.info("Nurse already assigned to duty")
                return True
        return False
    
    def checkSundays(self, nurse, day):
        if day != 'niedziela':
            return False
        self.logger.debug("checkSundays" + str(self.numberOfSundays) + " nurse Sundays " + str(nurse.sundays))
        if self.numberOfSundays - nurse.sundays == 1:
            return True
        return False
    
    def logPreviousWeek(self, i):
        if i > 0:
            self.logger.debug("DUTY " + str(self.duties[i - 1].day) + " " + self.duties[i - 1].type + " has been planned already")
            self.logger.debug("NURSES: ")
            for nurse in self.duties[i - 1].nurses:
                self.logger.debug(nurse.name)
    
    def calculateHours(self):
        matrix = calendar.monthcalendar(self.year,self.month)
        num_sun = sum(1 for x in matrix if x[calendar.SUNDAY] != 0)
        num_sat = sum(1 for x in matrix if x[calendar.SATURDAY] != 0)
        self.logger.info("ScheduleTab: calculateHours: calculated SUNDAYS: " + str(num_sun))
        self.logger.info("ScheduleTab: calculateHours: calculated SATURDAYS: " + str(num_sat))
        self.workingDays = self.numberOfDays - num_sat - num_sun - len(self.getBankHolidaysInMonth(str(self.month)))
        self.logger.info("ScheduleTab: calculateHours: calculated WORKING DAYS: " + str(self.workingDays))
        for nurse in self.nurses:
            self.logger.info("Nurse timejob is " + str(nurse.timejob))
            if float(nurse.timejob) == 1.0 or float(nurse.timejob) == 0.5:
                nurse.hours = round((float(self.workingDays) * float(nurse.timejob) * 7.5833333333), 2)
                self.logger.info("Nurse: " + nurse.name + " should work in this month for " + str(nurse.hours))
    
    def getBankHolidays(self):
        f = open("DniWolne.txt", "r")
        self.bankHolidays = f.readlines()
        f.close()
        
    def getBankHolidaysInMonth(self, month):
        holidays= []
        if len(month) == 1:
            month = "0" + month
        for holiday in self.bankHolidays:
            if holiday.split(".")[1].find(month) != -1:
                holidays.append(holiday)
        for holiday in holidays:
            self.logger.debug("Holiday in " + month + ": " + holiday)
        return holidays
    
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
                        