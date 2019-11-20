import wx
import os

from Nurse import *

class NurseTab(wx.Panel):

    def __init__(self, parent, logger):
        wx.Panel.__init__(self, parent)
        self.page = 0
        self.logger = logger
        self.logger.info("NurseTab init")
        self.nurses = []
        if self.checkSavedFiles():
            self.loadNurses("nurses.nur")
        self.createListCTRL()
        
    def createButtons(self):
        self.addNurseBtn = wx.Button(self, label='Dodaj Pielegniarke', size=(120, 30))
        self.removeNurse = wx.Button(self, label='Usun Pielegniarke', size=(120, 30))
        self.hbox.Add(self.addNurseBtn)
        self.hbox.Add(self.removeNurse)
        
    def createListCTRL(self):
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        self.list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.list.InsertColumn(0, 'Pielegniarka', width=400)
        self.list.InsertColumn(1, 'Etat', width=100)
        self.list.InsertColumn(2, 'Urlopy', width=600)
        self.list.InsertColumn(3, 'Dostepnosc', width=600)
        idx = 0
        for i in self.nurses:
            index = self.list.InsertItem(idx, i.name)
            self.list.SetItem(index, 1, i.timejob)
            self.list.SetItem(index, 2, i.getHolidaysString())
            self.list.SetItem(index, 3, i.getAvailabilitiesString())
            idx += 1
        
        self.hbox.Add(self.list, proportion=1, flag=wx.EXPAND)
        self.createButtons()
        self.SetSizer(self.hbox)
        self.Layout() 
    
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
                self.createListCTRL()
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
        