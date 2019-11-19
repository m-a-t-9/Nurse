import wx
from Scheduler import *
from EditNurseDutiesWindow import *
data = [("Styczen",31), ("Luty", 28), ("Marzec",31), ("Kwiecien",30), ("Maj",31), ("Czerwiec",30), ("Lipiec",31), ("Sierpien",31), ("Wrzesien", 30), ("Pazdziernik", 31), ("Listopad",30), ("Grudzien",31)]




    


class Example(wx.Frame):

    monthsMenuItems = []

    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title,
            size=(1200, 800))

        self.scheduler = Scheduler()
        self.InitUI()

    def InitUI(self):

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        #fileMenu.Append(wx.ID_OPEN, '&Zaladuj grafik')
        #fileMenu.Append(wx.ID_SAVE, '&Zapisz grafik')
        #fileMenu.AppendSeparator()

        new = wx.Menu()       
        i=0
        for monthName in data:
            self.monthsMenuItems.append(wx.MenuItem(new, i, monthName[0]))
            self.monthsMenuItems[-1].SetItemLabel(monthName[0])
            new.AppendItem(self.monthsMenuItems[-1])
            self.Bind(wx.EVT_MENU, self.OnNew, self.monthsMenuItems[-1])
            i+=1
            
        fileMenu.AppendMenu(wx.ID_ANY, 'Nowy grafik', new)

        imp = wx.MenuItem(fileMenu, wx.ID_ANY, 'Importuj liste pielegniarek')
        fileMenu.AppendItem(imp)
        
        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Wyjscie\tCtrl+W')
        fileMenu.AppendItem(qmi)

        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        self.Bind(wx.EVT_MENU, self.OnImport, imp)
        #self.Bind(wx.EVT_MENU, self.OnNew, new)

        menubar.Append(fileMenu, '&Plik')
        self.SetMenuBar(menubar)
        #self.mainbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        #self.panel = wx.Panel(self)
        
        #self.Maximize(True)
        #self.SetTitle('Grafiki')
        

    def OnNew(self, e):
        self.numberOfDays = data[e.GetId()][1]
        self.scheduler.createMonth(self.numberOfDays)
        if len(self.scheduler.nurses) == 0:
            self.loadNurses()
        self.scheduler.schedule()
        self.showMonth()

    def showMonth(self):
        
        self.list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.list.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.OnRightClick)
        self.list.InsertColumn(0, "Imie i Nazwisko", width=200)
        for i in range(self.numberOfDays):
            self.list.InsertColumn(i+1, str(i+1), width=30)

        idx = 0
        for nurse in self.scheduler.nurses:
            index = self.list.InsertItem(idx, nurse.name)
            for duty in nurse.dailyDuties:
                self.list.SetItem(index, duty, "D")
            for duty in nurse.nightlyDuties:
                self.list.SetItem(index, duty, "N")    
            idx += 1

        #self.editButton = wx.Button(self, label='Edytuj', size=(50, 20))
        #self.Bind(wx.EVT_BUTTON, self.OnEdit, self.editButton)
        
        self.hbox.Add(self.list, proportion=1, flag=wx.EXPAND)
        #self.hbox.Add(self.editButton)
        self.SetSizer(self.hbox)
        self.Layout()    

    def OnRightClick(self, e):
        menu = wx.Menu()
        itemOne = menu.Append(0, "Edytuj")
        self.Bind(wx.EVT_MENU, self.OnEdit, itemOne)
        itemTwo = menu.Append(1, "Usun")
         
        # show the popup menu
        self.PopupMenu(menu)
        menu.Destroy()
        #menu = NursePopupMenu(self)
        
    def OnEdit(self, e):
        i = self.GetSelectedItem()[0]
        nurseName = self.list.GetItem(i).GetText()
        print(nurseName)
        if nurseName != "":
            
            editDialog = EditNurseDutiesWindow(self, self.scheduler.getNurse(nurseName))
            editDialog.ShowModal()
            editDialog.Destroy()
            #PutData in the list and refresh
        
    def OnQuit(self, e):
        self.Close()

    def loadNurses(self):
         with wx.FileDialog(self, "Open nur file", wildcard="NUR files (*.nur)|*.nur",style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            try:
                with open(pathname, 'r') as file:
                    self.scheduler.loadNurses(file)
            except IOError:
                wx.LogError("Cannot open file '%s'." % newfile)

    def OnImport(self, e):
        # otherwise ask the user what new file to open
        self.loadNurses()
        self.list = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
        self.list.InsertColumn(0, 'Pielegniarka', width=400)
        self.list.InsertColumn(1, 'Etat', width=400)
        idx = 0
        for i in self.scheduler.nurses:
            index = self.list.InsertItem(idx, i.name)
            self.list.SetItem(index, 1, i.timejob)
            idx += 1
        self.hbox.Add(self.list, proportion=1, flag=wx.EXPAND)
        self.SetSizer(self.hbox)
        self.Layout() 
        
    def GetSelectedItem(self):
        selection = []
        current = -1
        while True:
            next = self.GetNextSelected(current)
            if next == -1:
                return selection

            selection.append(next)
            current = next

    def GetNextSelected(self, current):
        return self.list.GetNextItem(current, wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)

def main():

    app = wx.App()
    ex = Example(None, "Schedule")
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
