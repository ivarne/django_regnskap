# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.conf import settings
from django.utils.safestring import mark_safe

from django_regnskap.regnskap.models import *

from decimal import *
import datetime

class Budsjett(models.Model):
    class Meta:
        verbose_name_plural = "budsjett"
    name = models.CharField(max_length = 100)
    comment = models.TextField()
    fra = models.DateField()
    til = models.DateField()
    prosjekt = models.ForeignKey(Prosjekt)
    def __init__(self, *args, **kwargs):
        super(Budsjett,self).__init__(*args, **kwargs)
        if self.prosjekt_id == None:
            #self.prosjekt_name comes from the sub class
            try:
                self.prosjekt_id = self.prosjekt_store_id
            except:pass
    def get_absolute_url(self):
        return "/budsjett/show/%d" % self.id
    def get_admin_url(self):
        return "/admin/budsjett/%sbudsjett/%d" % (self.prosjekt.navn, self.id)
    def __unicode__(self):
        return self.name


class BudsjettPost(models.Model):
    budsjett = models.ForeignKey(Budsjett, related_name='post')
    konto    = models.ManyToManyField(Konto, related_name='budsjett_post', limit_choices_to={'kontoType__gt': 2})#, through='BudsjettPost_Konto')
    name  = models.CharField(max_length = 200)
    comment = models.TextField(blank=True)
    belop    = models.DecimalField(max_digits=16,decimal_places=2, blank=False, null=False, help_text=u'Husk Minus for kostnader')
    def getResultat(self):
        if hasattr(self,'resultat_cache'):
            return self.resultat_cache
        res = Decimal(0)
        kontos = Konto.objects.sum_columns(when = "`dato`>= %s AND `dato`<= %s",when_arg=(self.budsjett.fra, self.budsjett.til)) \
            .filter(budsjett_post = self)
        for k in kontos:
            if k.sum_kredit:
                res += k.sum_kredit
            if k.sum_debit:
                res -= k.sum_debit
            print k
        self.resultat_cache = res
        return res
    def getAvvik(self):
        #return self.belop - self.getResultat()
        return self.getResultat() - self.belop
    def exResultat(self):
        if self.budsjett.fra > datetime.date.today():
            return "fra is future"
            return Decimal(0)
        if self.budsjett.til < datetime.date.today():
            return self.getResultat()
        return int(self.getResultat() * (self.budsjett.til - self.budsjett.fra).days) / (datetime.date.today() - self.budsjett.fra).days
    def exAvvik(self):
        if(self.belop < 0):
            return abs(self.belop) - abs(self.exResultat())
        return abs(self.exResultat()) - abs(self.belop)
    def getKontoNumbers(self):
        if self.pk:
            return u", ".join([unicode(konto.nummer) for konto in self.konto.all()])
        return u""
    def __unicode__(self):
        return self.name + u': ' + self.getKontoNumbers()
    