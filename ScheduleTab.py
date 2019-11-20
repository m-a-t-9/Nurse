import wx
import wx.lib.mixins.listctrl  as  listmix
import calendar
from datetime import datetime

from Duty import *

class EditableListCtrl(wx.ListCtrl, listmix.TextEditMixin):

    def __init__(self, parent, ID=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):

        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.TextEditMixin.__init__(self)

    

class ScheduleTab(wx.Panel):
    
    def __init__(self, parent, logger, nurseIface):
        wx.Panel.__init__(self, parent)
        self.page = 1
        self.logger = logger
        self.NIF = nurseIface
        self.nurses = []
        self.duties = []
        self.createMonth()
        self.createListCTRL()
    
    def createMonth(self, month=None):
        self.year = int(datetime.now().strftime('%Y'))
        if month == None:
            self.month = int(datetime.now().strftime('%m')) + 1
            if self.month == 13:
                self.month = 1
                self.year += 1
            self.numberOfDays = calendar.monthrange(self.year, self.month)[1]
        else:
            self.month = month
            self.numberOfDays = calendar.monthrange(self.year, self.month)[1]
        for i in range(self.numberOfDays):
            self.duties.append(Duty((i+1), "D"))
            self.duties.append(Duty((i+1), "N"))
    
    def createListCTRL(self, month=None):
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        
        self.logger.info("ScheduleTab: createListCTRL: create calendar for days: " + str(self.numberOfDays))
        self.list = EditableListCtrl(self, style=wx.LC_REPORT)
        #self.list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick) if will be needed futher
        self.list.InsertColumn(0, "Imie i Nazwisko", width=150)
        for i in range(self.numberOfDays):
            self.list.InsertColumn(i+1, str(i+1), width=30)
        self.list.InsertColumn(self.numberOfDays+1, "Suma", width=60)
        idx = 0
        for nurse in self.nurses:
            index = self.list.InsertItem(idx, nurse.name)
            for duty in nurse.dailyDuties:
                self.list.SetItem(index, duty, "D")
            for duty in nurse.nightlyDuties:
                self.list.SetItem(index, duty, "N") 
            self.list.SetItem(index, self.numberOfDays+1, str(nurse.getPlannedHours()))
            idx += 1
            
        self.applyChangesBtn = wx.Button(self, label='Zastosuj zmiany', size=(80, 20))
        self.calculateBtn = wx.Button(self, label='Uloz grafik', size=(80, 30))
        
        self.Bind(wx.EVT_BUTTON, self.OnApply, self.applyChangesBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCalculate, self.calculateBtn)
        
        self.hbox.Add(self.list, proportion=1, flag=wx.EXPAND)
        if self.list.GetItemCount() != 0:
            self.hbox.Add(self.applyChangesBtn)
        self.hbox.Add(self.calculateBtn)
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
        
    def schedule(self):
        self.calculateHours()
        self.setContractors()
        j = 0
        end = []
        for i in range(len(self.duties)):
            self.logger.info("\nSchedulling day " + str(self.duties[i].day) + " " + self.duties[i].type)
            while len(self.duties[i].nurses) < 3 and len(end) != len(self.nurses):
                if j < len(self.nurses):
                    if self.nurses[j].checkDuties():
                        if not self.nurses[j].checkHoliday(self.duties[i].day) and self.nurses[j].checkAvailability(self.duties[i].day):
                            self.nurses[j].addDuty(self.duties[i].day, self.duties[i].type)
                            self.duties[i].nurses.append(self.nurses[j])
                            self.logger.info(self.nurses[j].name + " assigned to duty in " + str(self.duties[i].day))
                        else:
                            self.logger.info("Nurse " + self.nurses[j].name + " is not available in this day " + str(self.duties[i].day))
                    else:
                        self.logger.info("Nurse " + self.nurses[j].name + " already have all duties in this  month")
                        if self.nurses[j].name not in end:
                            end.append(self.nurses[j].name)
                    j += 1
                else:
                    j = 0
            if len(end) == len(self.nurses):
                self.logger.info("There is not enough nurses in this month to schedule work")
                break
        self.logger.info("Done :D\n\n\n")
        
    def calculateHours(self):
        matrix = calendar.monthcalendar(self.year,self.month)
        num_sun = sum(1 for x in matrix if x[calendar.SUNDAY] != 0)
        num_sat = sum(1 for x in matrix if x[calendar.SATURDAY] != 0)
        self.logger.info("ScheduleTab: calculateHours: calculated SUNDAYS: " + str(num_sun))
        self.logger.info("ScheduleTab: calculateHours: calculated SATURDAYS: " + str(num_sat))
        self.workingDays = self.numberOfDays - num_sat - num_sun
        self.logger.info("ScheduleTab: calculateHours: calculated WORKING DAYS: " + str(self.workingDays))
        for nurse in self.nurses:
            self.logger.info("Nurse timejob is " + str(nurse.timejob))
            if float(nurse.timejob) == 1.0 or float(nurse.timejob) == 0.5:
                nurse.hours = float(self.workingDays) * float(nurse.timejob) * 7.58
                self.logger.info("Nurse: " + nurse.name + " should work in this month for " + str(nurse.hours))
                
    def setContractors(self):
        for nurse in self.nurses:
            if float(nurse.timejob) == 0.0:
                for duty in nurse.availabilities:
                    day = int(duty.split("_")[0])
                    t = duty.split("_")[1]
                    duty = self.getDuty(day, t)
                    if duty != None:
                        self.logger.info("SetContractors: adding duty: " + str(duty.day) + " to nurse " + nurse.name)
                        nurse.addDuty(day, t)
                        duty.nurses.append(nurse)
                        
    def getDuty(self, day, type):
        for duty in self.duties:
            if int(duty.day) == int(day) and str(duty.type) == str(type):
                return duty
                        