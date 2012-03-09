"""
Collection of exportation routines
"""
from django_regnskap.regnskap.models import *
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook
import datetime

class ExelYearView(object):
    """Exporter regnskapet i excel format for year"""
    
    def __init__(self, template = None):
        """
        Initialize an excel export for year an using an excel file as a template
        """
        if(template):
            self._wb = openpyxl.load_workbook(template)
            """Internal variable to hold the openpyxl workbook"""
        else:
            self._wb = openpyxl.Workbook()
            self._wb.properties.creator = "Django_regnskap, av Trondheim Kristne Studentlag"
            self._wb.worksheets[0].title = "Transaksjonsoversikt"
            self._wb.create_sheet(1,"Resultatregnskap")
            self._wb.create_sheet(2,"Balanse")
        # set metadata
        p = self._wb.properties
        p.creator = "Django_regnskap, av Trondheim Kristne Studentlag"
        p.last_modified_by = "Django_regnskap, av Trondheim Kristne Studentlag"
    
    def generateYear(self,year):
        p = self._wb.properties
        p.title = "Regnskap for %d" % year
        p.description = "Autogenerert regnskap for %d\nEksportert :%Y-%m-%d %H:%M:%S".format(year, datetime.datetime.now())
        kontoList = list(Konto.objects.all().order_by('nummer'))
        bilagList = Bilag.objects.filter(dato__year = year).order_by('bilagsnummer')
        self._generateRegnskapArk(kontoList,bilagList)
        self._generateResultArk(year)
        self._generateBalanseArk(year)
    
    def getExcelFileStream(self):
        return save_virtual_workbook(self._wb)
    
    def save(self, filename):
        return self._wb.save(filename)
    
    def _generateRegnskapArk(self, kontoList, bilagList):
        ra = self._wb.worksheets[0]
        #write column headers
        ra.cell("A1").value = "Bilag"
        ra.cell("A2").value = "#"
        ra.cell("B1").value = "Regnskaps"
        ra.cell("B2").value = "Dato"
        ra.cell("C1").value = "Beskrivelse"
        ra.cell("C2").value = ""
        ra.cell("D1").value = "Hvem?"
        ra.cell("D2").value = ""
        #write konto numbers and labels (first two lines)
        kontoIndex = {} # kontonummer -> column pos
        for i, konto in enumerate(kontoList):
            ra.cell(row=0,column=i+4).value = konto.tittel
            ra.cell(row=1,column=i+4).value = konto.nummer
            kontoIndex[konto.nummer] = i+4;
        #write all bilag
        for i, bilag in enumerate(bilagList):
            ra.cell(row=i+2, column=0).value = bilag.bilagsnummer
            ra.cell(row=i+2, column=1).value = bilag.dato
            ra.cell(row=i+2, column=2).value = bilag.beskrivelse
            ra.cell(row=i+2, column=3).value = unicode(bilag.external_actor) or ""
            for innslag in bilag.innslag.all():
                c = kontoIndex[innslag.konto.nummer]
                if(innslag.isDebit):
                    ra.cell(row=i+2, column = c).value = innslag.belop
                else: #negativ for kredit
                    ra.cell(row=i+2, column = c).value = -innslag.belop
    
    def _generateResultArk(self, year):
        ra = self._wb.worksheets[1]
        ra.cell("A1").value = "Resultatregnskap"
        ra.cell("B3").value = "Kostnader"
        ra.cell("C3").value = "Inntekter"
        intKonto =list(getKontoaggregation(year = int(year), kontoType = '3'))
        kostKonto = list(getKontoaggregation(year = int(year), kontoType = '4,5,6,7,8,9'))
        maxLen = max(len(kostKonto),len(intKonto))
        for i, konto in enumerate(kostKonto):
            ra.cell(row=i+3, column=0).value = unicode(konto)
            ra.cell(row=i+3, column=1).value = int(konto.sum_debit or 0) - int(konto.sum_kredit or 0)
        for i, konto in enumerate(intKonto):
            ra.cell(row=i+3, column=2).value = unicode(konto)
            ra.cell(row=i+3, column=3).value = int(konto.sum_kredit or 0) - int(konto.sum_debit or 0)
        ra.cell(row=maxLen+3,column=0).value = "Sum:"
        ra.cell(row=maxLen+3,column=2).value = "Sum:"
        ra.cell(row=maxLen+3,column=1).value = "=SUM(B4:B%d)" % (maxLen+3)
        ra.cell(row=maxLen+3,column=3).value = "=SUM(D4:D%d)" % (maxLen+3)
    
    def _generateBalanseArk(self, year):
        ba = self._wb.worksheets[2]
        ba.cell("A1").value = "Balanseregnskap"
        ba.cell("B3").value = "Eiendeler"
        ba.cell("C3").value = "Egenkapital og Gjeld"
        eiendelKonto =list(getKontoaggregation(year = int(year), kontoType = '1'))
        finansKonto = list(getKontoaggregation(year = int(year), kontoType = '2'))
        maxLen = max(len(eiendelKonto),len(finansKonto))
        for i, konto in enumerate(eiendelKonto):
            ba.cell(row=i+3, column=0).value = unicode(konto)
            ba.cell(row=i+3, column=1).value = int(konto.sum_debit or 0) - int(konto.sum_kredit or 0)
        for i, konto in enumerate(finansKonto):
            ba.cell(row=i+3, column=2).value = unicode(konto)
            ba.cell(row=i+3, column=3).value = int(konto.sum_kredit or 0) - int(konto.sum_debit or 0)
        ba.cell(row=maxLen+3,column=0).value = "Sum:"
        ba.cell(row=maxLen+3,column=2).value = "Sum:"
        ba.cell(row=maxLen+3,column=1).value = "=SUM(B4:B%d)" % (maxLen+3)
        ba.cell(row=maxLen+3,column=3).value = "=SUM(D4:D%d)" % (maxLen+3)

if __name__ == '__main__':
    excel = ExcelYearView(2011)
    excel.save('test.xlsx')