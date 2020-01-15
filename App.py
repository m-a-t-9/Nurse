import wx
import wx.lib.mixins.listctrl  as  listmix
import logging

from NurseTab import *
from ScheduleTab import *

data = [("Styczen",31), ("Luty", 28), ("Marzec",31), ("Kwiecien",30), ("Maj",31), ("Czerwiec",30), ("Lipiec",31), ("Sierpien",31), ("Wrzesien", 30), ("Pazdziernik", 31), ("Listopad",30), ("Grudzien",31)]
monthsDropdown = ["Wybierz miesiac", "Styczen", "Luty", "Marzec", "Kwiecien", "Maj", "Czerwiec", "Lipiec", "Sierpien", "Wrzesien", "Pazdziernik", "Listopad", "Grudzien"]

class Example(wx.Frame):

    monthsMenuItems = []

    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title)
        logging.basicConfig(filename='LOG.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(process)d - %(message)s')
        self.logger = logging.getLogger('LOG')
        self.Maximize(True)
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
            new.Append(self.monthsMenuItems[-1])
            self.Bind(wx.EVT_MENU, self.OnNew, self.monthsMenuItems[-1])
            i+=1
            
        fileMenu.AppendSubMenu(new, 'Nowy grafik')

        imp = wx.MenuItem(fileMenu, wx.ID_ANY, 'Importuj liste pielegniarek')
        fileMenu.Append(imp)
        
        opn = wx.MenuItem(fileMenu, wx.ID_ANY, 'Zaladuj istniejacy grafik z pliku')
        fileMenu.Append(opn)
        
        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Wyjscie\tCtrl+W')
        fileMenu.Append(qmi)

        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        self.Bind(wx.EVT_MENU, self.OnOpen, opn)
        self.Bind(wx.EVT_MENU, self.OnImport, imp)
        

        menubar.Append(fileMenu, '&Plik')
        self.SetMenuBar(menubar)
        self.toolbar = self.CreateToolBar()
        self.combo = wx.ComboBox(self.toolbar, 555, value = monthsDropdown[0], choices = monthsDropdown)
        self.toolbar.Realize()

        
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        
        self.nb = wx.Notebook(self)
        self.nurseTab = NurseTab(self.nb, self.logger)
        self.scheduleTab = ScheduleTab(self.nb, self.logger, self.nurseTab.iface)
        
        self.nb.AddPage(self.nurseTab, "Zaloga")
        self.nb.AddPage(self.scheduleTab, "Grafik")
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnTabChange)
        
        self.hbox.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(self.hbox)
        self.Layout()

    def OnTabChange(self, e):
        print(self.nb.GetSelection())
        if self.nb.GetSelection() == 1:
            self.scheduleTab.setMonthAndRefresh(self.combo.GetSelection())
            self.calculateButton = self.toolbar.AddTool(wx.ID_ANY, 'Calculate', wx.Bitmap('calculator-icon.jpg'))
            #self.toolbar.Realize()
    

    def OnNew(self, e):
        self.scheduleTab.OnNew(e.GetId()+1)
        self.nb.ChangeSelection(self.scheduleTab.page)
       
    def OnOpen(self, e):
        self.scheduleTab.OnOpen()
        self.nb.ChangeSelection(self.scheduleTab.page)
       
    def OnQuit(self, e):
        self.Close()

    def OnImport(self, e):
        self.nurseTab.OnOpen()
        self.nb.ChangeSelection(self.nurseTab.page)

def main():

    app = wx.App()
    ex = Example(None, "Schedule")
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
