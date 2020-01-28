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
        self.nurseTab.OnOpen()
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
        
    def OnScheduleOpen(self):
        with wx.FileDialog(self.parent, "Open schedule file", wildcard="HTML files (*.html)|*.html",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
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
        self.schedulePages.append(ScheduleTab(self.nb, self.logger, self.getIface(), self.pageCounter, monthName))
        #TO BE IMPLEMENTED
        self.nb.AddPage(self.schedulePages[-1], self.schedulePages[-1].monthName)
        return self.pageCounter
        
    def OnScheduleSave(self):
        with wx.FileDialog(self.parent, "Save schedule file", wildcard="HTML files (*.html)|*.html",style=wx.FD_SAVE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                self.getCurrentSchedule().OnSave(pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)
                
    def OnStaffSave(self):
        with wx.FileDialog(self.parent, "Save staff file", wildcard="NUR files (*.nur)|*.nur",style=wx.FD_SAVE) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                self.nurseTab.OnSave(pathname)
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)
        
        