# -*- coding: utf-8 -*-
from django.db import models
from regnskap.models import Konto
from datetime import datetime

# Create your models here.

class Selskap(models.Model):
    navn = models.CharField(max_length=127)
    adresse = models.TextField()
    orgnr = models.CharField(max_length=63)
    aga_sats = models.DecimalField(decimal_places=2, max_digits=5, default=14.1)
    art_feriepenger = models.ForeignKey('LonnArt', related_name='+')
    art_skatt_prosent = models.ForeignKey('LonnArt', related_name='+')
    art_skatt_ordinar = models.ForeignKey('LonnArt', related_name='+')
    def __unicode__(self):
        return self.navn


class Ansatt(models.Model):
    navn = models.CharField(max_length=63)
    adresse = models.TextField()
    stilling = models.CharField(max_length=127)
    f_nr = models.CharField(max_length=20)
    kontonr = models.CharField(max_length=15)
    feriepenge_sats = models.DecimalField(decimal_places=2,max_digits=5)
    def __unicode__(self):
        return self.navn
    def _getSkattekort(self):
        return self.getSkattekort(datetime.now)
    def getSkattekort(self, dato):
        return Skattekort.objects.get(ansatt=self, dato_fra__lte=dato, dato_til__gte=dato)
    skattekort = property(_getSkattekort)

class Skattekort(models.Model):
    ansatt = models.ForeignKey(Ansatt)
    skattekommune = models.IntegerField()
    dato_fra = models.DateField()
    dato_til = models.DateField(null=True)
    prosent = models.IntegerField()
    def __unicode__(self):
        return 'Skattekort ('+unicode(self.dato_fra)+' - '+unicode(self.dato_til)+':  '+self.ansatt.navn+')'

class LonnPeriode(models.Model):
    navn = models.CharField(max_length=63)
    dato = models.DateField()
    selskap = models.ForeignKey(Selskap)
    finalized = models.BooleanField(default=False)
    def __unicode__(self):
        return self.navn+' ('+unicode(self.dato)+')'
#    def addAnsatt(self, ansatt):
#        return LonnAnsattPeriode(ansatt=ansatt, periode=self).save()
    def _getAnsatte(self):
        return LonnAnsattPeriode.objects.filter(periode=self)
    ansatte = property(_getAnsatte)
    def _getArts(self):
        return LonnAnsattPeriodeArt.objects.filter(ansattPeriode__in=self.ansatte)
    arts = property(_getArts)
    def getYearToThis(self):
        return LonnPeriode.objects.filter(dato__lte = self.dato).filter(dato__year = self.dato.year).filter(selskap=self.selskap)

class KontoProxy(models.Model):
    nummer = models.IntegerField(unique=True)
    navn = models.CharField(max_length=63)
    konto = models.ForeignKey(Konto, blank=True, null=True)
    def __unicode__(self):
        return unicode(self.nummer)+' '+self.navn

class LonnArt(models.Model):
    skattetrekk_choices = (
                           (0, 'Ingen'),
                           (1, 'Ordinar'),
                           (2, 'Prosent'),
    )
    
    nummer = models.IntegerField()
    tekst = models.CharField(max_length=63)
    visPaLonnSlipp = models.BooleanField(default=True)
    feriepengegrunnlag = models.BooleanField(default=True)
    skattetrekk = models.IntegerField(choices=skattetrekk_choices, default=1)
    konto_fra = models.ForeignKey(KontoProxy, related_name='+')
    konto_til = models.ForeignKey(KontoProxy, related_name='+')
    konto_aga = models.ForeignKey(KontoProxy, related_name='+', null=True, blank=True, default=None)
    konto_aga_til = models.ForeignKey(KontoProxy, related_name='+', null=True, blank=True, default=None)
    def __unicode__(self):
        return unicode(self.nummer)+' '+self.tekst
    def _skattShort(self):
        return ['-','%','%'][self.skattetrekk]
    skattShort = property(_skattShort)

class LonnAnsattPeriode(models.Model):
    ansatt = models.ForeignKey(Ansatt)
    periode = models.ForeignKey(LonnPeriode)
  # kontonr = models.CharField(max_length=15, blank=True, null=True)
  # brutto = models.DecimalField(decimal_places=2,max_digits=15, blank=True, null=True)
  # skatt = models.DecimalField(decimal_places=2,max_digits=15, blank=True, null=True)
    def __unicode__(self):
        return unicode(self.periode.dato)+', '+self.ansatt.navn
    def _getArts(self):
        return LonnAnsattPeriodeArt.objects.filter(ansattPeriode = self)
    arts = property(_getArts)
    def _getThisYearsArts(self):
        perioder = self.periode.getYearToThis()
        ansattPerioder = LonnAnsattPeriode.objects.filter(periode__in = perioder).filter(ansatt = self.ansatt)
        return LonnAnsattPeriodeArt.objects.filter(ansattPeriode__in = ansattPerioder)
    thisYearsArts = property(_getThisYearsArts)
    def getYearToPerodeSlipArts(self):
        artDict = {}
        for art in self.thisYearsArts:
            dataElem = artDict[art.lonnArt.nummer] if art.lonnArt.nummer in artDict else {"lonnArt":art.lonnArt}
            dataElem['yearAntall'] = dataElem['yearAntall']+art.antall if ('yearAntall' in dataElem)  else art.antall
            dataElem['yearSum']    = dataElem['yearSum']+art.sum       if ('yearSum'    in dataElem)  else art.sum
            if art.ansattPeriode == self:
                dataElem['periodeAntall'] = art.antall
                dataElem['periodeStkBelop'] = art.stk_belop
                dataElem['periodeSum'] = art.sum
            artDict[art.lonnArt.nummer] = dataElem
        return artDict


class LonnAnsattPeriodeArt(models.Model):
    ansattPeriode = models.ForeignKey(LonnAnsattPeriode)
    lonnArt = models.ForeignKey(LonnArt)
    antall = models.DecimalField(decimal_places=2, max_digits=15)
    stk_belop = models.DecimalField(decimal_places=2, max_digits=15)
    def __unicode__(self):
        return unicode(self.ansattPeriode)+' - '+self.lonnArt.tekst + ' ('+unicode(self.antall)+'x'+unicode(self.stk_belop)+')'
    def _getSum(self):
        return self.antall * self.stk_belop
    sum = property(_getSum)
