# -*- coding: utf-8 -*-
"""
Collection of exportation routines
"""

from django_regnskap.regnskap.models import *
import openpyxl
from openpyxl.writer.excel import save_virtual_workbook
import datetime

class ExelYearView(object):
    """Exporter regnskapet i excel format for year"""
    
    def __init__(self, year, wb = None):
        """
        Initialize an excel export for year an using an excel file as a template
        """
        self._year = year
        self._wb = wb or openpyxl.Workbook()
        self._setWbProperties()
        self._generateMainSheet( year, self._wb.worksheets[0] )
        for prosjekt in Prosjekt.objects.all():
            sheet = self._wb.create_sheet( 1, str(prosjekt) )
            self._generateProjectSheet( prosjekt, year, sheet )
    
    def _setWbProperties(self):
        # set metadata
        p = self._wb.properties
        p.creator = "Django_regnskap, av Trondheim Kristne Studentlag"
        p.last_modified_by = "Django_regnskap, av Trondheim Kristne Studentlag"
        p.title = "Regnskap for %d" % self._year
        p.description = "Autogenerert regnskap for %d\nEksportert :%Y-%m-%d %H:%M:%S".format(self._year, datetime.datetime.now())
    
    def _generateMainSheet(self,year, sheet):
        sheet.title = "Oversikt"
        
    
    def _generateProjectSheet(self, prosjekt, year, sheet):
        kontoList = list(Konto.objects.prosjekt(prosjekt))
        bilagList = Bilag.objects.prosjekt(prosjekt).filter(dato__year = year).order_by('bilagsnummer')
        sheet.cell("A1").value = "Bilag"
        sheet.cell("A2").value = "#"
        sheet.cell("B1").value = "Regnskaps"
        sheet.cell("B2").value = "Dato"
        sheet.cell("C1").value = "Beskrivelse"
        sheet.cell("C2").value = ""
        sheet.cell("D1").value = "Hvem?"
        sheet.cell("D2").value = ""
        #write konto numbers and labels (first two lines)
        kontoIndex = {} # kontonummer -> column pos
        for i, konto in enumerate(kontoList):
            sheet.cell(row=0,column=i+4).value = konto.tittel
            sheet.cell(row=1,column=i+4).value = konto.nummer
            kontoIndex[konto.nummer] = i+4;
        #write all bilag
        for i, bilag in enumerate(bilagList):
            sheet.cell(row=i+2, column=0).value = bilag.bilagsnummer
            sheet.cell(row=i+2, column=1).value = bilag.dato
            sheet.cell(row=i+2, column=2).value = bilag.beskrivelse
            sheet.cell(row=i+2, column=3).value = unicode(bilag.external_actor) or ""
            try:
                for innslag in bilag.innslag.all():
                    c = kontoIndex[innslag.konto.nummer]
                    if(innslag.isDebit):
                        sheet.cell(row=i+2, column = c).value = innslag.belop
                    else: #negativ for kredit
                        sheet.cell(row=i+2, column = c).value = -innslag.belop
            except KeyError:
                sheet.cell(row=i+2, column = 4).value = "ERROR: innslag registrert pa konto som ikke er del av dette prosjketet"
    
    def getExcelFileStream(self):
        return save_virtual_workbook(self._wb)
    
    def save(self, filename):
        return self._wb.save(filename)
    

    
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
            ra.cell(row=i+3, column=1).value = float(konto.sum_debit or 0) - float(konto.sum_kredit or 0)
        for i, konto in enumerate(intKonto):
            ra.cell(row=i+3, column=2).value = unicode(konto)
            ra.cell(row=i+3, column=3).value = float(konto.sum_kredit or 0) - float(konto.sum_debit or 0)
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
            ba.cell(row=i+3, column=1).value = float(konto.sum_debit or 0) - float(konto.sum_kredit or 0)
        for i, konto in enumerate(finansKonto):
            ba.cell(row=i+3, column=2).value = unicode(konto)
            ba.cell(row=i+3, column=3).value = float(konto.sum_kredit or 0) - float(konto.sum_debit or 0)
        ba.cell(row=maxLen+3,column=0).value = "Sum:"
        ba.cell(row=maxLen+3,column=2).value = "Sum:"
        ba.cell(row=maxLen+3,column=1).value = "=SUM(B4:B%d)" % (maxLen+3)
        ba.cell(row=maxLen+3,column=3).value = "=SUM(D4:D%d)" % (maxLen+3)