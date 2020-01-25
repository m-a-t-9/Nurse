import wx
import os

from Nurse import *

class MyPopupMenu(wx.Menu):

    def __init__(self, parent, grid, context, row=0):
        super(MyPopupMenu, self).__init__()
        self.row = row
        self.parent = parent
        self.grid = grid
        add = wx.MenuItem(self, wx.NewId(), 'Dodaj pielegniarke')
        self.Append(add)
        self.Bind(wx.EVT_MENU, self.OnAdd, add)
        if context == "grid":
            rem = wx.MenuItem(self, wx.NewId(), 'Usuń pielegniarke')
            self.Append(rem)
            self.Bind(wx.EVT_MENU, self.OnRemove, rem)

    def OnAdd(self, e):
        self.grid.InsertRows(pos=-1)
        self.grid.Fit()
        
    def OnRemove(self, e):
        self.parent.remove(self.row)

class NurseTab(wx.Panel):

    def __init__(self, parent, logger):
        wx.Panel.__init__(self, parent)
        self.page = 0
        self.parent = parent
        self.SetSize(parent.GetSize())
        self.logger = logger
        self.logger.info("NurseTab init")
        self.nurses = []
        self.lastAdded = None
        if self.checkSavedFiles():
            self.loadNurses("nurses.nur")
        self.createGridCTRL()
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        
    def OnRightDown(self, e):
        self.PopupMenu(MyPopupMenu(self, self.grid, "panel"), e.GetPosition())
    
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
        self.grid.SetColMinimalWidth(0, 400)
        self.grid.SetColLabelValue(1, "Etat")
        self.grid.SetColMinimalWidth(1, 100)
        self.grid.SetColLabelValue(2, "Urlopy")
        self.grid.SetColMinimalWidth(2, 600)
        self.grid.SetColLabelValue(3, "Dostepnosc")
        self.grid.SetColMinimalWidth(3, 600)
        self.putDataInGrid()
        
    def putDataInGrid(self):  
        self.grid.InsertRows(numRows=len(self.nurses))
        for i in range(len(self.nurses)):
            self.logger.debug(str(i))
            self.grid.SetCellValue(i, 0, self.nurses[i].name)
            self.grid.SetCellValue(i, 1, self.nurses[i].timejob)
            self.grid.SetCellValue(i, 2, self.nurses[i].getHolidaysString())
            self.grid.SetCellValue(i, 3, self.nurses[i].getAvailabilitiesString())
        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnChange)
        self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK , self.OnRowRightClick, self.grid)    

        self.grid.Fit()
        self.Layout()
        self.Show()
    
    def OnRowRightClick(self, e):
       row = e.GetRow()
       column = e.GetCol()
       self.logger.info("NurseTab: right click on row " + str(row)) 
       self.grid.SelectRow(row)
       self.PopupMenu(MyPopupMenu(self, self.grid, "grid", row=row), e.GetPosition())
       
    
    def OnChange(self, e):
        self.logger.info("NurseTab: OnChange: cell value has been changed")
        row = e.GetRow()
        col = e.GetCol()
        oldValue = e.GetString()
        newValue =self.grid.GetCellValue(row, col)
        if col == 0:
            if oldValue == "":
                self.nurses.append(Nurse(newValue +",,,", self.logger))
            else:
                for nurse in self.nurses:
                    if nurse.name == oldValue:
                        self.logger.info("NurseTab: OnChange: name of nurse " + oldValue + " has been changed to " + newValue)
                        self.logger.debug("NurseTab: OnChange: number of nurses: " + str(len(self.nurses)))
                        nurse.name = newValue
                        break
        elif col == 1:
            self.nurses[row].setTimejob(newValue)
            
        elif col == 2:
            data = newValue.split(",")
            self.nurses[row].addHolidays(data)
            #self.grid.Fit()
            
    
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
                self.putDataInGrid()
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
            
    def remove(self, id):
        self.logger.info("NurseTab: nurse " + self.nurses[id].name + " has been remove" )
        toRemove = self.nurses[id]
        self.nurses.remove(toRemove)
        self.grid.DeleteRows(pos=id)
        self.grid.Fit()
        