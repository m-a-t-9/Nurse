import wx


class Example(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(Example, self).__init__(*args, **kwargs)

        self.scheduler = Scheduler()
        self.InitUI()

    def InitUI(self):

        menubar = wx.MenuBar()

        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, '&Nowy grafik')
        fileMenu.Append(wx.ID_OPEN, '&Zaladuj grafik')
        fileMenu.Append(wx.ID_SAVE, '&Zapisz grafik')
        fileMenu.AppendSeparator()

        imp = wx.MenuItem(fileMenu, wx.ID_ANY, 'Importuj liste pielegniarek')
        fileMenu.AppendItem(imp)

        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Wyjscie\tCtrl+W')
        fileMenu.AppendItem(qmi)

        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)
        self.Bind(wx.EVT_MENU, self.OnImport, imp)

        menubar.Append(fileMenu, '&Plik')
        self.SetMenuBar(menubar)

        self.SetSize((350, 250))
        self.SetTitle('Grafiki')
        self.Centre()

    def OnQuit(self, e):
        self.Close()

    def OnImport(self, e):
        # otherwise ask the user what new file to open
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

def main():

    app = wx.App()
    ex = Example(None)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()