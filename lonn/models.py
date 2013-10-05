# -*- coding: utf-8 -*-
from django.db import models
from regnskap.models import Konto


# Create your models here.

class Ansatt(models.Model):
    navn = models.CharField(max_length=63)
    f_nr = models.CharField(max_length=20)
    kontonr = models.CharField(max_length=15)
    feriepenge_sats = models.DecimalField(decimal_places=2,max_digits=5)
    def __unicode__(self):
        return self.navn
    def _getSkattekort(self):
        return Skattekort.objects.get(ansatt=self, dato_til=None)
    skattekort = property(_getSkattekort)

class Skattekort(models.Model):
    ansatt = models.ForeignKey(Ansatt)
    skattekommune = models.IntegerField()
    dato_fra = models.DateField()
    dato_til = models.DateField(null=True)
    prosent = models.IntegerField()

class LonnPeriode(models.Model):
    navn = models.CharField(max_length=63)
    dato = models.DateField()
    def __unicode__(self):
        return self.navn+' ('+unicode(self.dato)+')'
    def addAnsatt(self, ansatt):
        return LonnAnsattPeriode(ansatt=ansatt, periode=self).save()
    def _getAnsatte(self):
        return LonnAnsattPeriode.objects.filter(periode=self)
    ansatte = property(_getAnsatte)

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
    feriepengegrunnlag = models.BooleanField(default=True)
    skattetrekk = models.IntegerField(choices=skattetrekk_choices, default=1)
    konto_fra = models.ForeignKey(KontoProxy, related_name='+')
    konto_aga = models.ForeignKey(KontoProxy, related_name='+')
    def __unicode__(self):
        return unicode(self.nummer)+' '+self.tekst

class LonnAnsattPeriode(models.Model):
    ansatt = models.ForeignKey(Ansatt)
    periode = models.ForeignKey(LonnPeriode)
  # kontonr = models.CharField(max_length=15, blank=True, null=True)
  # brutto = models.DecimalField(decimal_places=2,max_digits=15, blank=True, null=True)
  # skatt = models.DecimalField(decimal_places=2,max_digits=15, blank=True, null=True)
    def __unicode__(self):
        return unicode(self.periode.dato)+', '+self.ansatt.navn

class LonnAnsattPeriodeArt(models.Model):
    ansattPeriode = models.ForeignKey(LonnAnsattPeriode)
    lonnArt = models.ForeignKey(LonnArt)
    antall = models.DecimalField(decimal_places=2, max_digits=15)
    stk_belop = models.DecimalField(decimal_places=2, max_digits=15)
    def __unicode__(self):
        return unicode(self.ansattPeriode)+' - '+self.lonnArt.tekst + ' ('+unicode(self.antall)+'x'+unicode(self.stk_belop)+')'
