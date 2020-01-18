import wx
import wx.lib.mixins.listctrl  as  listmix
import logging


from Book import *
from Global import *

class Example(wx.Frame):

    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title)
        logging.basicConfig(filename='LOG.log', level=logging.DEBUG, filemode='w', format='%(asctime)s - %(levelname)s - %(process)d - %(message)s')
        self.logger = logging.getLogger('LOG')
        self.monthsMenuItems = []
        self.Maximize(True)
        self.InitUI()
        
    def InitUI(self):
        self.logger.info("App: InitUI")
        self.createMenu()
                
        self.hbox = wx.BoxSizer(wx.VERTICAL)
        self.book = Book(self, self.logger)
        self.hbox.Add(self.book.nb, 1, wx.EXPAND)
        self.SetSizer(self.hbox)
        self.Layout()

    def createMenu(self):
        self.logger.info("App: createMenu")
        self.menubar = wx.MenuBar()
        self.fileMenu = wx.Menu()
        self.calculateMenu = wx.Menu()
        self.createNewMenuItem()
        self.createOpenMenuItems()
        self.createSaveMenuItems()
        self.createExitMenuItem()       

        self.menubar.Append(self.fileMenu, '&Plik')
        self.menubar.Append(self.calculateMenu, '&Oblicz grafik')
        self.SetMenuBar(self.menubar)

    def createNewMenuItem(self):
        self.new = wx.Menu()       
        i=0
        for monthName in MONTHS_DETAILED:
            self.monthsMenuItems.append(wx.MenuItem(self.new, i, monthName[0]))
            self.monthsMenuItems[-1].SetItemLabel(monthName[0])
            self.new.Append(self.monthsMenuItems[-1])
            self.Bind(wx.EVT_MENU, self.OnNew, self.monthsMenuItems[-1])
            if i == 11:
                self.new.AppendSeparator()
            i+=1
        self.monthsMenuItems[-1].Enable(False)
        self.fileMenu.AppendSubMenu(self.new, 'Nowy pusty grafik')
        self.fileMenu.AppendSeparator()

    def createOpenMenuItems(self):
        self.opn = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Otwórz grafik\tCtrl+O')
        self.fileMenu.Append(self.opn)
        self.Bind(wx.EVT_MENU, self.OnOpen, self.opn)
        self.imp = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Otwórz listę pielegniarek\tCtrl+Alt+O')
        self.fileMenu.Append(self.imp)
        self.fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnImport, self.imp)
        
    def createSaveMenuItems(self):
        self.saveSchedule = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Zapisz grafik do pliku\tCtrl+S')
        self.fileMenu.Append(self.saveSchedule)
        self.Bind(wx.EVT_MENU, self.OnSave, self.saveSchedule)
        self.saveNurse = wx.MenuItem(self.fileMenu, wx.ID_ANY, '&Zapisz załogę do pliku\tCtrl+Alt+S')
        self.fileMenu.Append(self.saveNurse)
        self.fileMenu.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnNurseSave, self.saveNurse)
        
    def createExitMenuItem(self):
        self.qmi = wx.MenuItem(self.fileMenu, wx.ID_EXIT, '&Wyjście\tCtrl+W')
        self.fileMenu.Append(self.qmi)
        self.Bind(wx.EVT_MENU, self.OnQuit, self.qmi)

    def OnNew(self, e):
        self.logger.info("App: OnNew " + str(e.GetId()))
        self.book.createSchedulePage(MONTHS[e.GetId()])
       
    def OnOpen(self, e):
        month = self.scheduleTab.OnOpen()
        self.combo.SetValue(month)
        self.nb.ChangeSelection(self.scheduleTab.page)
       
    def OnQuit(self, e):
        self.Close()

    def OnImport(self, e):
        self.book.createNursePage()
        
    def OnSave(self, e):
        self.scheduleTab.OnSave(e)
        wx.MessageBox('Zapisano pomyślnie', 'Info',
            wx.OK | wx.ICON_INFORMATION)
        
    def OnNurseSave(self, e):
        self.logger.info("App: OnNurseSave")

def main():

    app = wx.App()
    ex = Example(None, "Schedule")
    ex.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
