import wx.lib.mixins.listctrl  as  listmix
import wx

monthsDropdown = ["Wybierz miesiac", "Styczen", "Luty", "Marzec", "Kwiecien", "Maj", "Czerwiec", "Lipiec", "Sierpien", "Wrzesien", "Pazdziernik", "Listopad", "Grudzien"]

class HTMLExporter:

    def __init__(self, list, month, filepath):
        self.list = list
        self.month = month
        self.filepath = filepath
        self.columns = []
        self.rows = []
        self.loadData()
        
    def loadData(self):
        self.numberOfColumns = self.list.GetNumberCols()
        self.numberOfRows = self.list.GetNumberRows()
        self.loadColumn()
        self.loadRaws()
        
    def loadColumn(self):
        for i in range(self.numberOfColumns):
            self.columns.append(self.list.GetColLabelValue(i))
        
    def loadRaws(self):
        for row in range(self.numberOfRows):
            self.rows.append([])
            self.rows[-1].append(self.list.GetRowLabelValue(row))
            for col in range(self.numberOfColumns):
                item = self.list.GetCellValue(row, col=col)
                self.rows[-1].append(item)
    
    def save(self):
        self.createHTMLFile()
    
    def createHTMLFile(self):
        self.f = open(self.filepath, "w")
        self.createHeaderOfDoc()
        self.createTableHeader()
        self.createTableContent()
        self.createTableFooter()
        self.createFooterOfDoc()
        self.f.close()
        
    def createTableContent(self):
        self.f.write('<tr><th></th>')
        for col in self.columns:
            self.f.write("<th>" + col + "</th>")
        self.f.write("</tr>")
        for row in self.rows:
            self.f.write("<tr>")
            for element in row:
                self.f.write("<th>" + element + "</th>")
            self.f.write("</tr>")
       # print(self.columns)
        #print(self.raws)
        #for i in range(len(self.columns)):
        #    self.f.write("<tr>")
            
        
    def createHeaderOfDoc(self):
        self.f.write('<html><head><meta charset="utf-8" /><title>Grafik:' + monthsDropdown[self.month] + '</title></head><style>table, th, tr {border: 1px solid black;}</style><body>')
        
    def createTableHeader(self):
        self.f.write('<table>')
        
    def createTableFooter(self):
        self.f.write("</table>")
        
    def createFooterOfDoc(self):
        self.f.write('</body></html>')
                