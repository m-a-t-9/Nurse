import wx
from NurseTab import *
from ScheduleTab import *
class Book:
    
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        self.schedulePages = []
        self.pageCounter = 1
        self.nb= wx.Notebook(self.parent)
        self.parent.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabChange)
        
    def createNursePage(self):
        self.logger.info("Book: createNursePage")
        self.nurseTab = NurseTab(self.nb, self.logger)
        self.nurseTab.OnOpen()
        self.nb.AddPage(self.nurseTab, "Zaloga")
        self.nb.ChangeSelection(self.nurseTab.page)
        
        
    def createSchedulePage(self, month):
        self.logger.info("Book: createSchedulePage " + str(month))
        self.schedulePages.append(ScheduleTab(self.nb, self.logger, self.nurseTab.iface, self.pageCounter, month))
        self.nb.AddPage(self.schedulePages[-1], self.schedulePages[-1].monthName)
        self.nb.ChangeSelection(self.schedulePages[-1].page)
        self.pageCounter += 1
    
    def OnTabChange(self, e):
        print(self.nb.GetSelection())
        if self.nb.GetSelection() == 1:
            self.scheduleTab.setMonthAndRefresh(self.combo.GetSelection())
            self.calculateButton = self.toolbar.AddTool(wx.ID_ANY, 'Calculate', wx.Bitmap('calculator-icon.jpg'))
            #self.toolbar.Realize()
        elif self.nb.GetSelection() == 0:
            self.nurseTab.setNurseAndRefresh()