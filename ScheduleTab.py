import wx
import wx.grid
import calendar
from datetime import datetime
import xml.etree.ElementTree as ET

from Duty import *
from HTMLExporter import *

from Global import *
from Schedule import *
from ScheduleHelper import *

class ScheduleTab(wx.Panel):
    
    def __init__(self, parent, logger, nurseIface, page, month):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.logger = logger
        self.NIF = nurseIface
        self.page = page
        self.monthName = month
        self.SetSize(parent.GetSize())
        self.SetBackgroundColour("BLACK")
        self.month = MONTHS.index(self.monthName)
        self.schedule = Schedule(self.logger, self.monthName, nurseIface)
        self.columns = self.schedule
        self.helper = ScheduleHelper(self.logger)
        self.nursesCalculated = False
        self.nurses = []
        self.duties = []
        self.createListCTRL()
    
    def setMonthAndRefresh(self, month):
        self.schedule.createMonth(MONTHS.index(month)+1)
        self.nurses = self.NIF("GET_NURSES")
        self.getNotWorkingDays()
        self.createListCTRL()
    
    def createListCTRL(self, dataFromFile=False):
        self.logger.info("ScheduleTab: createListCTRL: create calendar for days: " + str(MONTHS_DETAILED[self.month][1]))
        if len(self.nurses) == 0:
            self.nurses = self.NIF("GET_NURSES")
        self.schedule.calculateHours()
        
        self.grid = wx.grid.Grid(self)
        self.grid.CreateGrid(len(self.nurses), MONTHS_DETAILED[self.month][1]+1)
        self.grid.SetSize(self.GetSize())
        self.grid.SetRowLabelSize(width=150)
        
        for i in range( MONTHS_DETAILED[self.month][1]+1):
            if i == (MONTHS_DETAILED[self.month][1]):
                self.logger.debug("ScheduleTab: createListCTRL: SUMA column found " + str(i))
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
        #self.grid.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnSingleSelect)
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGING, self.OnChange)
        self.grid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnSelectToEdit)
        
        self.Layout()
        self.Show()        
    
    def OnSelectToEdit(self, e):
        row = e.GetRow()
        col = e.GetCol()
        self.oldValue = self.grid.GetCellValue(row, col)
        self.logger.debug("ScheduleTab: OnSelectToEdit: old value: " + self.oldValue)
    
    def OnChange(self, e):
        
        row = e.GetRow()
        col = e.GetCol()
        self.logger.debug("ScheduleTab: OnChange Changed in duty: " + str(col+1))
        self.logger.debug("Changed for nurse: " + str(self.nurses[row].name))
        newValue = e.GetString()
        self.logger.info("OnChange: cell value has been changed to: " + newValue)
        dutyIndex = 0
        if newValue == "N" or newValue == "D":
            result = self.schedule.tryToCreateDuty(col+1, row, self.month+1,  newValue, self.oldValue)
            if not result[0]:
                #self.grid.SetCellValue(row, col, newValue)
                self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 0, 0))
                wx.MessageBox(result[1], 'Info', wx.OK | wx.ICON_INFORMATION)
            else:
                self.logger.debug("ScheduleTab: new duty created. Changing SUMA value and background color")
                self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 255, 255))
            self.grid.SetCellValue(row, MONTHS_DETAILED[self.month][1], str(self.schedule.nif("GET_NURSES")[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
            
        elif newValue.find("U") != -1:
            self.schedule.addHolidayForNurse(row, col)
        elif newValue == "" or newValue == " ":
            #removeDutyForNurse(row, col)
            self.grid.SetCellValue(row, MONTHS_DETAILED[self.month][1], str(self.schedule.nif("GET_NURSES")[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
            self.grid.SetCellBackgroundColour(row, col,wx.Colour(255, 255, 255))
        elif newValue == "DX":
            result = self.schedule.tryToCreateDuty(col+1, row, self.month,  newValue)
            self.grid.SetCellValue(row, MONTHS_DETAILED[self.month][1], str(self.schedule.nif("GET_NURSES")[row].getPlannedHours()))
            self.setColorOfPlannedHours(row)
        
    def OnSingleSelect(self, e):
        r = e.GetRow()
        c = e.GetCol()
        if c == len(MONTHS):
            text = ""
            if self.schedule.nif("GET_NURSES")[r].getUnplannedHours() < 8 and self.schedule.nif("GET_NURSES")[r].getUnplannedHours() > 0:
                text = 'Pielęgniarka ' + self.schedule.nif("GET_NURSES")[r].name + " ma niezaplanowany krótki dyżór (" + self.schedule.nif("GET_NURSES")[r].getUnplannedHoursString() + ")"
            elif self.schedule.nif("GET_NURSES")[r].getUnplannedHours() < 0:
                text = 'Pielęgniarka ' + self.schedule.nif("GET_NURSES")[r].name + " przekracza etat (" + self.schedule.nif("GET_NURSES")[r].getUnplannedHoursString() + ")"
            else:
                text = 'Pielęgniarka ' + self.schedule.nif("GET_NURSES")[r].name + " ma niezaplanowane godziny (" + self.schedule.nif("GET_NURSES")[r].getUnplannedHoursString() + ")"
            wx.MessageBox(text, 'Info', wx.OK | wx.ICON_INFORMATION)
    
    def setDataInGrid(self):
        for i in range(len(self.schedule.nif("GET_NURSES"))):
        
            for duty in self.schedule.nif("GET_NURSES")[i].dailyDuties:
                self.grid.SetCellValue(i, duty-1, "D")
                self.grid.SetCellAlignment(i, duty-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            for duty in self.schedule.nif("GET_NURSES")[i].nightlyDuties:
                self.grid.SetCellValue(i, duty-1, "N")
                self.grid.SetCellAlignment(i, duty-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            for holiday in self.schedule.nif("GET_NURSES")[i].holidays:
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
            for duty in self.schedule.nif("GET_NURSES")[i].shortDuties:
                self.grid.SetCellValue(i, duty[0]-1, "DX")
                self.grid.SetCellAlignment(i, duty[0]-1, wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
            self.grid.SetCellValue(i, MONTHS_DETAILED[self.month][1], str(self.schedule.nif("GET_NURSES")[i].getPlannedHours()))
            self.setColorOfPlannedHours(i)
            self.grid.SetCellAlignment(i, MONTHS_DETAILED[self.month][1], wx.ALIGN_CENTRE, wx.ALIGN_CENTRE)
    
    def setColorOfPlannedHours(self, index):
        self.logger.info("Set color of planned hours for unplanned: " + str(self.schedule.nif("GET_NURSES")[index].getUnplannedHours()))
        if self.schedule.nif("GET_NURSES")[index].getUnplannedHours() < 8 and  self.schedule.nif("GET_NURSES")[index].getUnplannedHours() > 0:
            self.grid.SetCellBackgroundColour(index, MONTHS_DETAILED[self.month][1],wx.Colour(255, 255, 0))
        elif self.schedule.nif("GET_NURSES")[index].getUnplannedHours() >= 8 or self.schedule.nif("GET_NURSES")[index].getUnplannedHours() < 0:
            self.grid.SetCellBackgroundColour(index, MONTHS_DETAILED[self.month][1],wx.Colour(255, 0, 0))
        elif self.schedule.nif("GET_NURSES")[index].getUnplannedHours() == 0:
            self.grid.SetCellBackgroundColour(index, MONTHS_DETAILED[self.month][1],wx.Colour(0, 255, 0))
    
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

    def setColours(self): #->MUST BE
        for i in range(self.grid.GetNumberCols()):
            if self.schedule.isNotWorkingDay(i+1) and self.grid.GetColLabelValue(i) != "SUMA":
                for j in range(len(self.nurses)):
                    self.grid.SetCellBackgroundColour(j, i, wx.Colour(211, 211, 211))
    
    def OnSave(self, e): #->MUST BE
        self.logger.info("Saving schedule")
        htmlExporter = HTMLExporter(self.grid, self.month)
        htmlExporter.save()
        
    def OnCalculate(self): #->MUST BE
        self.logger.info("ScheduleTab: OnCalculate")
        self.nurses = self.NIF("GET_NURSES")
        self.schedule.schedule()
        self.setDataInGrid()
        
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
    

    
  
                        