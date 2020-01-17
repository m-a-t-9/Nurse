import wx
import wx.grid
import calendar
from datetime import datetime
import xml.etree.ElementTree as ET

from Duty import *
from HTMLExporter import *

monthsDropdown = ["Wybierz miesiac", "Styczen", "Luty", "Marzec", "Kwiecien", "Maj", "Czerwiec", "Lipiec", "Sierpien", "Wrzesien", "Pazdziernik", "Listopad", "Grudzien"]

class ScheduleTab(wx.Panel):
    
    def __init__(self, parent, logger, nurseIface):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.SetSize(parent.GetSize())
        self.SetBackgroundColour("BLACK")
        self.page = 1
        self.logger = logger
        self.nursesCalculated = False
        self.NIF = nurseIface
        self.getBankHolidays()
        self.nurses = []
        self.duties = []
        self.notWorkingDays = []
        self.createMonth()
        self.getNotWorkingDays()
        self.createListCTRL()
        
        
    
    def setMonthAndRefresh(self, month):
        self.createMonth(month)
        self.nurses = self.NIF("GET_NURSES")
        self.getNotWorkingDays()
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
        if len(self.duties) != 0:
            self.duties = []
        for i in range(self.numberOfDays):
            self.duties.append(Duty(i+1, self.month, self.year, "D"))
            self.duties.append(Duty(i+1, self.month, self.year, "N"))
            self.logger.info("Duty date name: " + str(self.duties[-1].getDayName()))
        self.calculateSundaysInMonth()
           
    def calculateSundaysInMonth(self):
        matrix = calendar.monthcalendar(self.year,self.month)
        self.numberOfSundays= sum(1 for x in matrix if x[calendar.SUNDAY] != 0)
        
    
    def getNotWorkingDays(self):
        if len(self.notWorkingDays) != 0:
            self.notWorkingDays = []
        matrix = calendar.monthcalendar(self.year, self.month)
        for i in range(len(matrix)):
            if matrix[i][5] != 0:
                self.notWorkingDays.append(matrix[i][5])
            if matrix[i][6] != 0:
                self.notWorkingDays.append(matrix[i][6])
        print(self.notWorkingDays)
    
    def isNotWorkingDay(self, day):
        if day in self.notWorkingDays:
            return True
        return False
    
    def getOnlyDayDuties(self):
        r = []
        for duty in self.duties:
            if duty.type == "D":
                r.append(duty)
        return r
    
    def createListCTRL(self, month=None, dataFromFile=False):
        if len(self.nurses) == 0:
            self.nurses = self.NIF("GET_NURSES")
        self.dutiesForColumn = self.getOnlyDayDuties()
        self.logger.info("ScheduleTab: createListCTRL: create calendar for days: " + str(self.dutiesForColumn))
        self.calculateHours()
        self.grid = wx.grid.Grid(self)
        
        self.grid.CreateGrid(len(self.nurses), len(self.dutiesForColumn) + 1)
        self.grid.SetSize(self.GetSize())
        #self.grid.Fit()
        self.grid.SetRowLabelSize(width=150)
        
        for i in range(len(self.dutiesForColumn) + 1):
            if i == (len(self.dutiesForColumn)):
                self.grid.SetColLabelValue(i, "SUMA")
                self.grid.SetColSize(i, 60)
            else:
                
                self.grid.SetColLabelValue(i, str(i+1))
                self.grid.SetColSize(i, 40)
                
                
        for i in range(len(self.nurses)):
            self.grid.SetRowLabelValue(i, self.nurses[i].name)
        self.setColours()    
        if dataFromFile:
            self.setDataInGridFromFile()
        else:
            self.setDataInGrid()
        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.onSingleSelect)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnChange)
        
        self.Layout()
        self.Show()        
    
    def OnChange(self, e):
        self.logger.info("OnChange: cell value has been changed")
        row = e.GetRow()
        col = e.GetCol()
        self.logger.debug("Changed in duty: " + str(self.dutiesForColumn[col].day))
        self.logger.debug("Changed for nurse: " + str(self.nurses[row].name))
        newValue =self.grid.GetCellValue(row, col)
        dutyIndex = 0
        if newValue == "N" or newValue == "D":
            duty = Duty(self.dutiesForColumn[col].day, self.month, self.year, newValue)
            result = self.validateNurse(self.nurses[row], duty)
            if not result[0]:
                self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 0, 0))
                wx.MessageBox(result[1], 'Info', wx.OK | wx.ICON_INFORMATION)
            self.nurses[row].addDuty(duty.day, duty.type, duty.dayName)
            self.grid.SetCellValue(row, len(self.dutiesForColumn), str(self.nurses[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
            
        elif newValue.find("U") != -1:
            self.nurses[row].holidays.append(self.nurses[row].monthFix(self.dutiesForColumn[col].day) + "." + self.nurses[row].monthFix(self.month))
        elif newValue == "" or newValue == " ":
            self.nurses[row].removeDuty(self.dutiesForColumn[col].day)
            self.grid.SetCellValue(row, len(self.dutiesForColumn), str(self.nurses[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
            self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 255, 255))
        elif newValue == "DX":
            duty = Duty(self.dutiesForColumn[col].day, self.month, self.year, newValue)
            self.nurses[row].addDuty(duty.day, duty.type, duty.dayName)
            self.grid.SetCellValue(row, len(self.dutiesForColumn), str(self.nurses[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
        
            
        
    
    def onSingleSelect(self, e):
        r = e.GetRow()
        c = e.GetCol()
        if c == len(self.dutiesForColumn):
            text = ""
            if self.nurses[r].getUnplannedHours() < 8 and self.nurses[r].getUnplannedHours() > 0:
                text = 'Pielęgniarka ' + self.nurses[r].name + " ma niezaplanowany krótki dyżór (" + self.nurses[r].getUnplannedHoursString() + ")"
            elif self.nurses[r].getUnplannedHours() < 0:
                text = 'Pielęgniarka ' + self.nurses[r].name + " przekracza etat (" + self.nurses[r].getUnplannedHoursString() + ")"
            else:
                text = 'Pielęgniarka ' + self.nurses[r].name + " ma niezaplanowane godziny (" + self.nurses[r].getUnplannedHoursString() + ")"
            wx.MessageBox(text, 'Info', wx.OK | wx.ICON_INFORMATION)
    
    def setDataInGrid(self):
        for i in range(len(self.nurses)):
        
            for duty in self.nurses[i].dailyDuties:
                self.grid.SetCellValue(i, duty-1, "D")
                self.grid.SetCellAlignment(i, duty-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            for duty in self.nurses[i].nightlyDuties:
                self.grid.SetCellValue(i, duty-1, "N")
                self.grid.SetCellAlignment(i, duty-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            for holiday in self.nurses[i].holidays:
                self.logger.info("ScheduleTab: setDataInGrid: holiday: " + str(holiday) + " month whcih has been set " + str(self.month))
                hday = holiday.split(".")[0]
                hmonth = holiday.split(".")[1]
                if len(str(self.month)) == 1:
                    currMonthString = "0" + str(self.month)
                else:
                    currMonthString = str(self.month)
                if hmonth == currMonthString:
                    self.grid.SetCellValue(i, int(hday)-1, "UW")
                    self.grid.SetCellBackgroundColour(i, int(hday)-1, wx.Colour(0,0,255))
                    self.grid.SetCellTextColour(i, int(hday)-1, wx.Colour(255,255,255))
                    self.grid.SetCellAlignment(i, int(hday)-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellValue(i, len(self.dutiesForColumn), str(self.nurses[i].getPlannedHours()))
            self.setColorOfPlannedHours(i)
            self.grid.SetCellAlignment(i, len(self.dutiesForColumn), wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
    
    def setColorOfPlannedHours(self, index):
        self.logger.info("Set color of planned hours for unplanned: " + str(self.nurses[index].getUnplannedHours()))
        if self.nurses[index].getUnplannedHours() < 8 and  self.nurses[index].getUnplannedHours() > 0:
            self.grid.SetCellBackgroundColour(index, len(self.dutiesForColumn),wx.Colour(255, 255, 0))
        elif self.nurses[index].getUnplannedHours() >= 8 or self.nurses[index].getUnplannedHours() < 0:
            self.grid.SetCellBackgroundColour(index, len(self.dutiesForColumn),wx.Colour(255, 0, 0))
        elif self.nurses[index].getUnplannedHours() == 0:
            self.grid.SetCellBackgroundColour(index, len(self.dutiesForColumn),wx.Colour(0, 255, 0))
    
    def setDataInGridFromFile(self):
        rows = self.root.findall("./body/table/tr")
        for nurse in rows:
            '''to be implemented methods'''
            n = self.findNurseByName(nurse[0].text)
            dailyDuties = self.findDuties(nurse, "D")
            nightlyDuties = self.findDuties(nurse, "N")
            holidays = self.findHolidays(nurse)
            if n != None:
                n.dailyDuties = dailyDuties
                n.nightlyDuties = nightlyDuties
                n.holidays = holidays
        self.calculateHours()
        self.setDataInGrid()
    
    def findNurseByName(self, name):
        for nurse in self.nurses:
            if nurse.name == name:
                return nurse
                
    def findDuties(self, nurseRow, dN):
        i = 0
        duties = []
        for child in nurseRow:
            if child.text == dN:
                duties.append(i)
            i+=1
        return duties
        
    def findHolidays(self, nurseRow):
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
    
    def setColours(self):
        for i in range(self.grid.GetNumberCols()):
            if self.isNotWorkingDay(i) and self.grid.GetColLabelValue(i) != "SUMA":
                for j in range(len(self.nurses)):
                    self.grid.SetCellBackgroundColour(j, i, wx.Colour(211, 211, 211))
    
    
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
        htmlExporter = HTMLExporter(self.grid, self.month)
        htmlExporter.save()
        wx.MessageBox('Zapisano pomyślnie', 'Info',
            wx.OK | wx.ICON_INFORMATION)

          
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
    
    def OnOpen(self):
        with wx.FileDialog(self, "Open schedule file", wildcard="HTML files (*.html)|*.html",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                return self.loadSchedule(pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)
    
    def loadSchedule(self, pathname):
        self.tree = ET.parse(pathname)
        self.root = self.tree.getroot()
       
        monthName = self.root.find('./head/title').text.split(":")[1]
        monthNo = monthsDropdown.index(monthName)
        self.createListCTRL(monthNo, dataFromFile=True)
        return monthName
            
    def validateNurse(self, nurse, duty, withDuties=True):
        if withDuties:
            if not nurse.checkDuties():
                self.logger.info("NURSE " + nurse.name + " has already overloaded")
                return [False, "Pielegniarka ma przypisane wszystkie możliwe dyżury"]
        if nurse.checkHoliday(duty):
            self.logger.info("NURSE " + nurse.name + " has planned holiday")
            return [False, "Pielegniarka ma zaplanowany urlop w tym dniu"]
        if not nurse.checkAvailability(duty.day):
            self.logger.info("NURSE " + nurse.name + " is not available at this day")
            return [False, "Pielegniarka jest nie dostępna w tym dniu"]
        if nurse.checkPreviousDay([duty.type, duty.day]):
            return [False, "Pielęgniarka ma inny dyzur dzień wcześniej. Zaplanowano całodobowy dyżur."]
        if self.isAlreadyAssigned(nurse, duty):
            return [False, "Pielegniarka ma inny dyżur w tym dniu"]
        if nurse.checkWeek(self.getWeekRange(duty.day)):
            return [False, "Pielegniarka przekracza maksymalna liczbę godzin w tygodniu"]
        if self.checkSundays(nurse, duty.dayName):
            self.logger.info("Nurse must have one free Sunday")
            return [False, "Pielegniarka musi mieć przynajmniej jedną niedziele wolna w miesiącu"]
        return [True, ""]
            
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
            self.logPreviousWeek(i)
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
                nurse.hours = round((float(self.workingDays) * float(nurse.timejob) * 7.5833333333 - (len(nurse.holidays)*7.5833333333)), 2)
                self.logger.info("Nurse: " + nurse.name + " should work in this month for " + str(nurse.hours))
        self.nursesCalculated = True
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
                        