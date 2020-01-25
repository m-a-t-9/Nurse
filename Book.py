import wx
from NurseTab import *
from ScheduleTab import *
class Book:
    
    nurseTab = None
    
    def __init__(self, parent, logger):
        self.parent = parent
        self.logger = logger
        self.schedulePages = []
        self.pageCounter = 1
        self.nb= wx.Notebook(self.parent)
        self.parent.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabChange)
        self.nurseTab = NurseTab(self.nb, self.logger)
        self.nb.AddPage(self.nurseTab, "Zaloga")
        self.nb.ChangeSelection(self.nurseTab.page)
 
    def createNursePage(self):
        self.logger.info("Book: createNursePage")
        self.nurseTab = NurseTab(self.nb, self.logger)
        self.nurseTab.OnOpen()
        self.nb.AddPage(self.nurseTab, "Zaloga")
        self.nb.ChangeSelection(self.nurseTab.page)
    
    def getIface(self):
        if self.nurseTab == None:
            self.logger.warning("Book: getIface: No nurses list loaded")
            #wx.MessageBox(self.parent, "Lista pielęgniarek nie została stworzona." 'Info', wx.OK | wx.ICON_INFORMATION)
        else:
            return self.nurseTab.iface
    
    def createSchedulePage(self, month):
        self.logger.info("Book: createSchedulePage " + str(month))
        self.schedulePages.append(ScheduleTab(self.nb, self.logger, self.getIface(), self.pageCounter, month))
        self.nb.AddPage(self.schedulePages[-1], self.schedulePages[-1].monthName)
        self.nb.ChangeSelection(self.schedulePages[-1].page)
        self.pageCounter += 1
    
    def OnTabChange(self, e):
        self.logger.info("Book: OntabChange: " + str(self.nb.GetSelection()))
        
    def getCurrentSchedule(self):
        return self.schedulePages[self.nb.GetSelection()-1]
        
    def checkSavedFiles(self):
        if os.path.isfile("nurses.nur"):
            return True
        return False