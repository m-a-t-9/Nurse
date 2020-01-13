import wx.lib.mixins.listctrl  as  listmix
import wx

class HTMLExporter:

    def __init__(self, list):
        self.list = list
        self.columns = []
        self.raws = []
        self.loadData()
        
    def loadData(self):
        self.numberOfColumns = self.list.GetColumnCount()
        self.numberOfRaws = self.list.GetItemCount()
        self.loadColumn()
        self.loadRaws()
        
    def loadColumn(self):
        for i in range(self.numberOfColumns):
            self.columns.append(self.list.GetColumn(i).GetText())
        
    def loadRaws(self):
        for row in range(self.numberOfRaws):
            self.raws.append([])
            for col in range(self.numberOfColumns):
                item = self.list.GetItem(row, col=col)
                self.raws[-1].append(item.GetText())
    
    def save(self):
        self.createHTMLFile()
    
    def createHTMLFile(self):
        self.f = open("Grafik.html", "w")
        self.createHeaderOfDoc()
        self.createTableHeader()
        self.createTableContent()
        self.createTableFooter()
        self.createFooterOfDoc()
        self.f.close()
        
    def createTableContent(self):
        self.f.write('<tr>')
        for col in self.columns:
            self.f.write("<th>" + col + "</th>")
        self.f.write("</tr>")
        for raw in self.raws:
            self.f.write("<tr>")
            for element in raw:
                self.f.write("<th>" + element + "</th>")
            self.f.write("</tr>")
       # print(self.columns)
        #print(self.raws)
        #for i in range(len(self.columns)):
        #    self.f.write("<tr>")
            
        
    def createHeaderOfDoc(self):
        self.f.write('<!DOCTYPE html><html><head><meta charset="utf-8"><title>Grafik</title></head><style> \
                        table, th, tr {     \
                            border: 1px solid black;}    \
                        th { width: 20px;}  \
                     </style><body>')
        
    def createTableHeader(self):
        self.f.write('<table style="border: 1px solid black">')
        
    def createTableFooter(self):
        self.f.write("</table>")
        
    def createFooterOfDoc(self):
        self.f.write('</body></html>')
                