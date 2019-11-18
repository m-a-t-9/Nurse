import wx

class SelectMonthPopup(wx.Dialog):
    
    def __init__(self):
        super(SelectMonthPopup, self).__init__()
        
        self.InitUI()
        self.SetSize((250, 200))
        self.SetTitle("Select month")