"""
Collection of exportation routines
"""
from regnskap.models import *
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook

class ExelYearView(object):
    """Exporter regnskapet i excel format for year"""
    def __init__(self, year, template = None):
        """
        Initialize an excel export for year an using an excel file as a template
        """
        self._year = year
        """The year that should be exported"""
        self._konto = list(Konto.objects.all().order_by('nummer'))
        self._bilag = Bilag.objects.filter(dato__year = self._year).order_by('bilagsnummer')
        if(template):
            self._wb = openpyxl.load_workbook(template)
            """Internal variable to hold the openpyxl workbook"""
        else:
            self._wb = openpyxl.Workbook()
            self._wb.properties.creator = "Django_regnskap, av Trondheim Kristne Studentlag"
            self._wb.worksheets[0].title = "Transaksjonsoversikt"
            self._wb.create_sheet(1,"Resultat Regnskap")
            self._wb.create_sheet(2,"Balanse")
        # set metadata
        p = self._wb.properties
        p.creator = "Django_regnskap, av Trondheim Kristne Studentlag"
        p.last_modified_by = "Django_regnskap, av Trondheim Kristne Studentlag"
        p.title = "Regnskap for %d" % year
        p.description = "Autogenerert regnskap for %d" % year
        
    def _generateRegnskapArk(self):
        ra = self._wb.worksheets[0]
        #write column headers
        ra.cell("A1").value = "Bilag"
        ra.cell("A2").value = "#"
        ra.cell("B1").value = "Regnskaps"
        ra.cell("B2").value = "Dato"
        ra.cell("C1").value = "Beskrivelse"
        ra.cell("C2").value = ""
        #write konto numbers and labels (first two lines)
        kontoIndex = {} # kontonummer -> column pos
        for i, konto in enumerate(self._konto):
            ra.cell(row=0,column=i+3).value = konto.tittel
            ra.cell(row=1,column=i+3).value = konto.nummer
            kontoIndex[konto.nummer] = i+3;
        for i, bilag in enumerate(self._bilag):
            ra.cell(row=i+3, column=0).value = bilag.bilagsnummer
            ra.cell(row=i+3, column=1).value = bilag.dato
            ra.cell(row=i+3, column=2).value = bilag.beskrivelse
            for innslag in bilag.innslag.all():
                c = kontoIndex[innslag.konto.nummer]
                if(innslag.isDebit):
                    ra.cell(row=i+3, column = c).value = innslag.belop
                else: #negativ for kredit
                    ra.cell(row=i+3, column = c).value = -innslag.belop
    def getExcelFileStream(self):
        return save_virtual_workbook(self._wb)
    def save(self, filename):
        return self._wb.save(filename)

if __name__ == '__main__':
    excel = ExcelYearView(2011)
    excel.save('test.xls')