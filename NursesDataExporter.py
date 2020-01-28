

class NursesDataExporter:
    
    def __init__(self, list, filepath, logger):
        self.list = list
        self.filepath = filepath
        self.logger = logger
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
        self.f = open(self.filepath, "w")
        self.f.write("#imie_nazwisko,etat,dostepnosc,urlop\n")
        for row in self.rows:
            for i in range(1, len(row)):
                if i == len(row)-1:
                    if len(row[i]) != 0:
                       self.f.write(self.createRow(row[i]))
                else:
                    self.f.write(row[i].strip() + ",")
                
            self.f.write("\n")
        self.f.close()
    
    def createRow(self, row):
        self.logger.info("NursesDataExporter: createRow: " + row)
        sdata = row.split("    ")
        result = ""
        for data in sdata:
            self.logger.debug("NursesDataExporter: createRow: data: " + data)
            data = data.strip()
            if len(data) == 2:
                result += data[0] + "_" + data[1] + ";"
            elif len(data) == 3:
                result += data[0] + data[1] + "_" + data[2] + ";"
        return result
