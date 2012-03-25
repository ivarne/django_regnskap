# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.http import Http404
from django.conf import settings

class Prosjekt(models.Model):
    navn = models.CharField(max_length=60)
    beskrivelse = models.TextField()
    def __unicode__(self):
        return self.navn

class BaseProsjektManager(models.Manager):
    def prosjekt(self, prosjekt):
        if not isinstance(prosjekt, Prosjekt):
            try:
                prosjekt = Prosjekt.objects.get(navn = prosjekt)
            except:
                raise Http404("Det finnes ikke noe projekt med navn \"%s\"" % prosjekt)
        return self.filter(Q(prosjekt = prosjekt) | Q(prosjekt = None))

class KontoManager(BaseProsjektManager):
    def sum_columns(self, prosjekt, *arg, **kwarg):
        if kwarg.has_key('when'):
            when = kwarg['when']
            del kwarg['when'] # cleanup
        else:
            when = "YEAR(`dato`) = %s"
        
        if(prosjekt):
            ret = self.prosjekt(prosjekt)
        else:
            ret = self
        
        subsql = '''SELECT SUM(`i`.`belop`)\
            FROM `%(i)s` as `i`\
            LEFT JOIN `%(b)s` as `b`\
            ON `b`.`id` = `i`.`bilag_id`\
            WHERE `i`.`konto_id` = `%(k)s`.`id`\
                AND %(when)s\
                AND `i`.`type` = %(type)s'''
        
        ret = ret.extra(
            select = {
                'sum_debit': subsql % {
                    'b': Bilag._meta.db_table,
                    'i': Innslag._meta.db_table,
                    'k': Konto._meta.db_table,
                    'when': when,
                    'type' : 0
                    },
                'sum_kredit': subsql % {
                    'b': Bilag._meta.db_table,
                    'i': Innslag._meta.db_table,
                    'k': Konto._meta.db_table,
                    'when': when,
                    'type' : 1
                    },
            },
            select_params = arg * 2
            )
        return ret
    
    def toOptionGroups(self, prosjekt):
        types = [('','')]
        kontos = self.prosjekt(prosjekt).order_by('nummer')
        if not kontos:
            return types
        t = kontos[0].kontoType # first konto type
        subtype = []
        for konto in kontos:
            if(konto.kontoType != t):
                types.append((Konto.AVAILABLE_KONTO_TYPE[t-1][1],subtype))
                subtype = []
                t = konto.kontoType
            subtype.append((konto.id, str(konto.nummer) + ' ' + konto.tittel,))
        types.append((Konto.AVAILABLE_KONTO_TYPE[t-1][1],subtype))
        return types

# Kontoplan
class Konto(models.Model):
    class Meta:
        ordering = ["nummer"]
    AVAILABLE_KONTO_TYPE = (
      (1,'Eiendeler'),
      (2,'Egenkapital og gjeld'),
      (3,'Salg og driftsinntekt'),
      (4,'Varekostnad'),
      (5,'Lonnskonstnad'),
      (6,'Annen driftskostnad'),
      (7,'Av- og nedskrivninger'),
      (8,u'Finans, ekstra og oppgjør')
    )
    id = models.AutoField(primary_key=True)
    kontoType = models.IntegerField(choices=AVAILABLE_KONTO_TYPE)
    nummer = models.IntegerField(unique=True)
    tittel = models.CharField(max_length=256)
    beskrivelse = models.TextField(blank = True)
    prosjekt = models.ForeignKey(Prosjekt, blank=True, null=True)
    objects = KontoManager()
    
    def __unicode__(self):
        return unicode(self.nummer) +' '+self.tittel
    # views can not do calculations
    def getLoadedDebit(self):
        return (self.sum_debit or 0) - (self.sum_kredit or 0)
    def getLoadedKredit(self):
        return (self.sum_kredit or 0) - (self.sum_debit or 0)

class Exteral_Actor(models.Model):
    name = models.CharField(max_length = 256)
    email = models.EmailField(blank = True)
    adress = models.TextField(blank = True)
    org_nr = models.CharField(blank = True, max_length = 100)
    archived = models.DateField(editable = False, blank=True, null=True)
    prosjekt = models.ForeignKey(Prosjekt)
    objects = BaseProsjektManager()

    def __unicode__(self):
        return self.name + ( " (%d)" % self.id )

class Bilag(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable = False)
    bilagsnummer = models.IntegerField(editable = False) #Automatic?
    dato = models.DateField()
    beskrivelse = models.CharField(max_length=256)
    external_actor = models.ForeignKey(Exteral_Actor,editable = False, null = True)
    prosjekt = models.ForeignKey(Prosjekt)
    objects = BaseProsjektManager()
    def _getKredit(self):
        self.innslag.filter(type=0)
    def _getDebit(self):
        self.innslag.filter(type=1)
    innslagKredit = property(_getKredit)
    innslagDebit = property(_getDebit)
    def save(self, *args, **kwargs):
        """Not thread safe, concider using transactions"""
        year = self.dato.year
        previous = Bilag.objects.filter(dato__year = year).aggregate(models.Max("bilagsnummer"))['bilagsnummer__max'] or 0
        self.bilagsnummer = previous + 1
        super(Bilag,self).save(*args, **kwargs)
        return self.bilagsnummer
    def __unicode__(self):
        return "%s-%s %s" % (self.dato.year, self.bilagsnummer, self.beskrivelse)

def _bilag_upload_to(instance, filename):
    return "bilag/%s/%s-%s" % (instance.dato.year, instance.bilag.id, filename)

class BilagFile(models.Model):
    bilag = models.ForeignKey(Bilag, related_name="files")
    file = models.CharField(max_length=100)
    def url(self):
        return settings.MEDIA_URL + self.file

class Innslag(models.Model):
    AVAILABLE_TYPE = (
      (0,'Debit'),
      (1,'Kredit')
    )
    bilag = models.ForeignKey(Bilag, related_name='innslag')
    konto = models.ForeignKey(Konto)
    
    belop = models.DecimalField(max_digits=16,decimal_places=2, blank=True, null=True)
    type = models.IntegerField(choices=AVAILABLE_TYPE)
    @property
    def isDebit(self):
        return self.type ==0
    @property
    def isKredit(self):
        return self.type == 1
    def __unicode__(self):
        return unicode(self.konto.nummer) +' '+unicode(self.debit)+'|'+unicode(self.kredit)
        
    def _debitValue(self):
        if self.type == 0:
            return self.belop
        else:
            return None
    def _kreditValue(self):
        if self.type == 1:
            return self.belop
        else:
            return None
    debit = property(_debitValue)
    kredit = property(_kreditValue)