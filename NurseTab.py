import wx
import os

from Nurse import *

class MyPopupMenu(wx.Menu):

    def __init__(self, parent):
        super(MyPopupMenu, self).__init__()

        self.parent = parent

        add = wx.MenuItem(self, wx.NewId(), 'Dodaj pielegniarke')
        self.Append(add)
        self.Bind(wx.EVT_MENU, self.OnAdd, add)

    def OnAdd(self, e):
        self.logger.info("Adding new nurse into list") 


class NurseTab(wx.Panel):

    def __init__(self, parent, logger):
        wx.Panel.__init__(self, parent)
        self.page = 0
        self.parent = parent
        self.SetSize(parent.GetSize())
        self.logger = logger
        self.logger.info("NurseTab init")
        self.nurses = []
        if self.checkSavedFiles():
            self.loadNurses("nurses.nur")
        self.createGridCTRL()
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        
    def OnRightDown(self, e):
        self.PopupMenu(MyPopupMenu(self), e.GetPosition())
    
    def setNurseAndRefresh(self):
        self.loadNurses()
        self.createGridCTRL()
    
    def createButtons(self):
        self.addNurseBtn = wx.Button(self, label='Dodaj Pielegniarke', size=(120, 30))
        self.removeNurse = wx.Button(self, label='Usun Pielegniarke', size=(120, 30))
        self.hbox.Add(self.addNurseBtn)
        self.hbox.Add(self.removeNurse)
        
    def createGridCTRL(self):
        self.grid = wx.grid.Grid(self)
        
        self.grid.CreateGrid(len(self.nurses), 4)
        
        self.grid.SetRowLabelSize(width=30)
        
        self.grid.SetColLabelValue(0, "Imie i nazwisko")
        self.grid.SetColSize(0, 400)
        self.grid.SetColLabelValue(1, "Etat")
        self.grid.SetColSize(1, 100)
        self.grid.SetColLabelValue(2, "Urlopy")
        self.grid.SetColSize(2, 600)
        self.grid.SetColLabelValue(3, "Dostepnosc")
        self.grid.SetColSize(3, 600)
        
        
        for i in range(len(self.nurses)):
            self.grid.SetCellValue(i, 0, self.nurses[i].name)
            self.grid.SetCellValue(i, 1, self.nurses[i].timejob)
            self.grid.SetCellValue(i, 2, self.nurses[i].getHolidaysString())
            self.grid.SetCellValue(i, 3, self.nurses[i].getAvailabilitiesString())
        self.grid.Fit()
        self.Layout()
        self.Show()
    
    def checkSavedFiles(self):
        if os.path.isfile("nurses.nur"):
            return True
        return False
    
    def OnOpen(self):
         with wx.FileDialog(self, "Open nur file", wildcard="NUR files (*.nur)|*.nur",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                self.loadNurses(pathname)
                self.createGridCTRL()
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)
                
    def loadNurses(self, filename):
        self.logger.info("NurseTab: loadNurses")
        f = open(filename, "r")
        c = f.readlines()
        f.close()
        if len(self.nurses) != 0:
            self.nurses = []
        for i in range(len(c)):
            if i != 0:
                self.nurses.append(Nurse(c[i], self.logger))
        self.logger.info("NurseTab: loadNurses: created: " + str(len(self.nurses)) + " nurses")
        
    def iface(self, operation, add=""):
        
        if operation == "GET_NURSES":
            return self.nurses
        