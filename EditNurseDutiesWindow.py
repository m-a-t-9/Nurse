import wx

class EditNurseDutiesWindow(wx.Dialog):

    def __init__(self, parent, nurse): 
        super(EditNurseDutiesWindow, self).__init__(parent, size = (250,150)) 
        self.nurse = nurse
        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle(self.nurse.name)


    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label=self.nurse.name)
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        
        sbs.Add(wx.RadioButton(pnl, label='256 Colors',
            style=wx.RB_GROUP))
        sbs.Add(wx.RadioButton(pnl, label='16 Colors'))
        sbs.Add(wx.RadioButton(pnl, label='2 Colors'))

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1.Add(wx.RadioButton(pnl, label='Custom'))
        hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)
        sbs.Add(hbox1)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)


    def OnClose(self, e):

        self.Destroy()
