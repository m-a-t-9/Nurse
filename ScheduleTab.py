import wx
import wx.grid
import calendar
from datetime import datetime
import xml.etree.ElementTree as ET

from Duty import *
from HTMLExporter import *

from Global import *
from Schedule import *

class ScheduleTab(wx.Panel):
    
    def __init__(self, parent, logger, nurseIface, page, month):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.SetSize(parent.GetSize())
        self.SetBackgroundColour("BLACK")
        self.page = page
        self.monthName = month
        self.month = MONTHS.index(self.monthName) + 1
        self.logger = logger
        self.schedule = Schedule(self.logger, self.monthName, nurceIface)
        self.nursesCalculated = False
        self.nurses = []
        self.duties = []
        self.saturdays = []
        self.sundays = []
        self.createMonth()
        
        self.createListCTRL()
    
    def setMonthAndRefresh(self, month):
        self.createMonth(month)
        self.nurses = self.NIF("GET_NURSES")
        self.getNotWorkingDays()
        self.createListCTRL()
    
    def createMonth(self):
        self.year = int(datetime.datetime.now().strftime('%Y'))
        self.schedule.createDutyTemplates()
        self.getBankHolidays()
        self.getNotWorkingDays()
           
    
    
    def getNotWorkingDays(self):
        
        matrix = calendar.monthcalendar(self.year, self.month)
        for i in range(len(matrix)):
            if matrix[i][5] != 0:
                self.saturdays.append(matrix[i][5])
            if matrix[i][6] != 0:
                self.sundays.append(matrix[i][6])
        
    def isNotWorkingDay(self, day):
        if day in self.saturdays or day in self.sundays:
            return True
        return False
    
    def createListCTRL(self, dataFromFile=False):
        self.logger.info("ScheduleTab: createListCTRL: create calendar for days: " + str(MONTHS_DETAILED[self.month][1]))
        if len(self.nurses) == 0:
            self.nurses = self.NIF("GET_NURSES")
        self.calculateHours()
        
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(len(self.nurses), MONTHS_DETAILED[self.month][1]+1)
        self.grid.SetSize(self.GetSize())
        self.grid.SetRowLabelSize(width=150)
        
        for i in range(len(MONTHS)):
            if i == (len(MONTHS)):
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
        self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnSingleSelect)
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
            result = self.schedule.tryToCreateDuty(col, self.month, self.year, newValue)
            if not result[0]:
                self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 0, 0))
                wx.MessageBox(result[1], 'Info', wx.OK | wx.ICON_INFORMATION)
            else:
                self.grid.SetCellValue(row, len(self.dutiesForColumn), str(self.schdule.nif("GET_NURSES")[row].getPlannedHours()))
                self.setColorOfPlannedHours(row)
            
        elif newValue.find("U") != -1:
            self.schedule.addHolidayForNurse(row, col)
        elif newValue == "" or newValue == " ":
            removeDutyForNurse(row, col)
            self.grid.SetCellValue(row, len(self.dutiesForColumn), str(self.schdule.nif("GET_NURSES")[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
            self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 255, 255))
        elif newValue == "DX":
            result = self.schedule.tryToCreateDuty(col, self.month, self.year, newValue)
            self.grid.SetCellValue(row, len(self.dutiesForColumn), str(self.schdule.nif("GET_NURSES")[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
        
    def OnSingleSelect(self, e):
        r = e.GetRow()
        c = e.GetCol()
        if c == len(MONTHS):
            text = ""
            if self.schdule.nif("GET_NURSES")[r].getUnplannedHours() < 8 and self.schdule.nif("GET_NURSES")[r].getUnplannedHours() > 0:
                text = 'Pielęgniarka ' + self.schdule.nif("GET_NURSES")[r].name + " ma niezaplanowany krótki dyżór (" + self.schdule.nif("GET_NURSES")[r].getUnplannedHoursString() + ")"
            elif self.schdule.nif("GET_NURSES")[r].getUnplannedHours() < 0:
                text = 'Pielęgniarka ' + self.schdule.nif("GET_NURSES")[r].name + " przekracza etat (" + self.schdule.nif("GET_NURSES")[r].getUnplannedHoursString() + ")"
            else:
                text = 'Pielęgniarka ' + self.schdule.nif("GET_NURSES")[r].name + " ma niezaplanowane godziny (" + self.schdule.nif("GET_NURSES")[r].getUnplannedHoursString() + ")"
            wx.MessageBox(text, 'Info', wx.OK | wx.ICON_INFORMATION)
    
    def setDataInGrid(self):
        for i in range(len(self.schdule.nif("GET_NURSES"))):
        
            for duty in self.schdule.nif("GET_NURSES")[i].dailyDuties:
                self.grid.SetCellValue(i, duty-1, "D")
                self.grid.SetCellAlignment(i, duty-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            for duty in self.schdule.nif("GET_NURSES")[i].nightlyDuties:
                self.grid.SetCellValue(i, duty-1, "N")
                self.grid.SetCellAlignment(i, duty-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            for holiday in self.schdule.nif("GET_NURSES")[i].holidays:
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
            self.grid.SetCellValue(i, len(self.dutiesForColumn), str(self.schdule.nif("GET_NURSES")[i].getPlannedHours()))
            self.setColorOfPlannedHours(i)
            self.grid.SetCellAlignment(i, len(self.dutiesForColumn), wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
    
    def setColorOfPlannedHours(self, index):
        self.logger.info("Set color of planned hours for unplanned: " + str(self.schdule.nif("GET_NURSES")[index].getUnplannedHours()))
        if self.schdule.nif("GET_NURSES")[index].getUnplannedHours() < 8 and  self.schdule.nif("GET_NURSES")[index].getUnplannedHours() > 0:
            self.grid.SetCellBackgroundColour(index, len(MONTHS),wx.Colour(255, 255, 0))
        elif self.schdule.nif("GET_NURSES")[index].getUnplannedHours() >= 8 or self.schdule.nif("GET_NURSES")[index].getUnplannedHours() < 0:
            self.grid.SetCellBackgroundColour(index, len(MONTHS),wx.Colour(255, 0, 0))
        elif self.schdule.nif("GET_NURSES")[index].getUnplannedHours() == 0:
            self.grid.SetCellBackgroundColour(index, len(MONTHS),wx.Colour(0, 255, 0))
    
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
        #HERE STOP
        self.calculateHours()# -> move to schedule 
        self.setDataInGrid()
    
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
    
    def setColours(self): #->MUST BE
        for i in range(self.grid.GetNumberCols()):
            if self.isNotWorkingDay(i) and self.grid.GetColLabelValue(i) != "SUMA":
                for j in range(len(self.nurses)):
                    self.grid.SetCellBackgroundColour(j, i, wx.Colour(211, 211, 211))
    
    def OnSave(self, e): #->MUST BE
        self.logger.info("Saving schedule")
        htmlExporter = HTMLExporter(self.grid, self.month)
        htmlExporter.save()
        
    def OnCalculate(self, e): #->MUST BE
        self.logger.info("ScheduleTab: OnCalculate")
        self.nurses = self.NIF("GET_NURSES")
        self.schedule()
        self.createListCTRL()
        
    def OnNew(self, month): #-> is it possible
        self.createMonth(month=month)
        self.nurses = self.NIF("GET_NURSES")
        self.schedule()
        self.createListCTRL()
    
    def OnOpen(self): #->MUST BE
        with wx.FileDialog(self, "Open schedule file", wildcard="HTML files (*.html)|*.html",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                return self.loadSchedule(pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)
    
    def loadSchedule(self, pathname): #->MUST BE
        self.tree = ET.parse(pathname)
        self.root = self.tree.getroot()
       
        monthName = self.root.find('./head/title').text.split(":")[1]
        monthNo = MONTHS.index(monthName)
        self.createListCTRL(monthNo, dataFromFile=True)
        return monthName
            
    
            
    def getWeekRange(self, day): #-> move to schedule
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
        
    def schedule(self): #-> move to schedule and refactor
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
            
    def planRestNursesHours(self, notPlannedDuties): #-> move to schedule 
        pass
                                
    def isAlreadyAssigned(self, nurse, duty): #->move to helper
        for aNurse in duty.nurses:
            if nurse.name == aNurse.name:
                self.logger.info("Nurse already assigned to duty")
                return True
        return False
    
    def checkSundays(self, nurse, day): #-> move to schedule
        if day != 'niedziela':
            return False
        self.logger.debug("checkSundays" + str(self.numberOfSundays) + " nurse Sundays " + str(nurse.sundays))
        if self.numberOfSundays - nurse.sundays == 1:
            return True
        return False
    
    def logPreviousWeek(self, i): #is it really needed? maybe helper or logger wrapper
        if i > 0:
            self.logger.debug("DUTY " + str(self.duties[i - 1].day) + " " + self.duties[i - 1].type + " has been planned already")
            self.logger.debug("NURSES: ")
            for nurse in self.duties[i - 1].nurses:
                self.logger.debug(nurse.name)
    
    def calculateHours(self): #refactor and move to schdule
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
        
    def getBankHolidays(self): #->move to schedule
        f = open("DniWolne.txt", "r")
        self.bankHolidays = f.readlines()
        f.close()
        
    def getBankHolidaysInMonth(self, month): #->move to schedule
        holidays= []
        if len(month) == 1:
            month = "0" + month
        for holiday in self.bankHolidays:
            if holiday.split(".")[1].find(month) != -1:
                holidays.append(holiday)
        for holiday in holidays:
            self.logger.debug("Holiday in " + month + ": " + holiday)
        return holidays
    
    def setContractors(self, dutiesToBePlanned): #->move to schedule
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
                        
    def getDuty(self, day, type): #->move to schedule
        for duty in self.duties:
            if int(duty.day) == int(day) and str(duty.type) == str(type):
                return duty
                        