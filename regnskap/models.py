# -*- coding: utf-8 -*-
from django.db import models
from django.db.models import Q

from django.contrib.auth.models import User
from django.http import Http404
from django.conf import settings
from django.core import urlresolvers
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe

from decimal import *
import os

class Prosjekt(models.Model):
    navn = models.CharField(max_length=60)
    beskrivelse = models.TextField()
    def __unicode__(self):
        return self.navn

class BaseProsjektManager(models.Manager):
    def prosjekt(self, prosjekt):
        if prosjekt == '' or prosjekt == None:
            return self
        if not isinstance(prosjekt, Prosjekt):
            try:
                prosjekt = Prosjekt.objects.get(navn = prosjekt)
            except:
                raise Http404("Det finnes ikke noe projekt med navn \"%s\"" % prosjekt)
        return self.filter(Q(prosjekt = prosjekt) | Q(prosjekt = None))

class KontoManager(BaseProsjektManager):
    def sum_columns(self, when_arg=(), when = "YEAR(`dato`) = %s", prosjekt = None):
        
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
            select_params = when_arg * 2
            )
        return ret

    def bilagRelated(self, related = None, year = None, kontoTypes=(), bilag_ids=[]):
        """
        somewhat same as sum_colums, but returns a list of kontos with extra properties instead of a query set
        this is also a cleaner approach as it does not use two separate subsql queries
        
        """
        where = []
        args = []
        if related:
            if isinstance(related, Exteral_Actor):
                where.append("`%(b)s`.`external_actor_id` = %%s")
                args.append(related.id)
            elif isinstance(related, Prosjekt):
                where.append("`%(b)s`.`prosjekt_id` = %%s")
                args.append(related.id)
#            elif hasattr(related, ):
#                where.append("`%(b)s`.`external_actor_id` = %%s")
#                args.append(related.id)
            else:
                raise Exception("Ugyldig objekt som relasjon til bilag")
        if year:
            where.append("YEAR(`%(b)s`.`dato`) = %%s")
            args.append(int(year))
        
        if kontoTypes:
            where.append("`%(k)s`.`kontoType` IN %%s")
            args.append(kontoTypes)
        if bilag_ids:
            where.append("`%(b)s`.`id` IN %%s")
            args.append(bilag_ids)
        where = " AND ".join(where)
        sql = ("""SELECT
            SUM(`%(i)s`.`belop` * `%(i)s`.`type` ) AS `sum_kredit`, 
            SUM(`%(i)s`.`belop` * (1 -`%(i)s`.`type`) ) AS `sum_debit`, 
            `%(k)s`.`id`, 
            `%(k)s`.`kontoType`, 
            `%(k)s`.`nummer`, 
            `%(k)s`.`tittel`, 
            `%(k)s`.`beskrivelse`, 
            `%(k)s`.`prosjekt_id`
        FROM `%(k)s` 
        INNER JOIN `%(i)s` ON (`%(k)s`.`id` = `%(i)s`.`konto_id`) 
        INNER JOIN `%(b)s` ON (`%(i)s`.`bilag_id` = `%(b)s`.`id`) 
        WHERE """ + where + """ GROUP BY `%(k)s`.`id` ORDER BY `%(k)s`.`nummer` ASC
        """) % {
            'b': Bilag._meta.db_table,
            'i': Innslag._meta.db_table,
            'k': Konto._meta.db_table,
        }
        return self.raw(sql, args)

    def toOptionGroups(self, prosjekt = "", not_balanse = False):
        avaiable_types = dict(Konto.AVAILABLE_KONTO_TYPE)
        types = [('','')]
        kontos = self.prosjekt(prosjekt).order_by('nummer')
        if not_balanse:
            kontos = kontos.filter(kontoType__gt = 2)
        kontos = list(kontos)
        if not kontos:
            return types
        t = kontos[0].kontoType # first konto type
        subtype = []
        for konto in kontos:
            if(konto.kontoType != t):
                types.append((avaiable_types[t],subtype))
                subtype = []
                t = konto.kontoType
            if prosjekt:
                subtype.append((konto.id, str(konto.nummer) + ' ' + konto.tittel,))
            else:
                subtype.append((konto.id, u"%d %s/%s" % (konto.nummer, konto.prosjekt, konto.tittel)))
        types.append((avaiable_types[t],subtype))
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
      (6,'Av- og nedskrivninger og Annen driftskostnad'),
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
        return u"%s %s/%s" %(self.nummer, self.prosjekt.navn, self.tittel)
    def getTittel(self):
        return self.prosjekt.navn + "/" + self.tittel
    # views can not do calculations
    def getLoadedDebit(self):
        return (self.sum_debit or 0) - (self.sum_kredit or 0)
    def getLoadedKredit(self):
        return (self.sum_kredit or 0) - (self.sum_debit or 0)
    def save(self):
        t = int(str(self.nummer)[0])
        if t == 7:
            t = 6
        self.kontoType = t
        return super(Konto,self).save()
    def get_absolute_url(self):
        return "/regnskap/show/konto/%d" % self.id
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    

class Exteral_Actor(models.Model):
    name = models.CharField(max_length = 256)
    email = models.EmailField(blank = True)
    adress = models.TextField(blank = True)
    org_nr = models.CharField(blank = True, max_length = 100)
    archived = models.DateField(editable = False, blank=True, null=True)
    prosjekt = models.ForeignKey(Prosjekt, null=True)
    objects = BaseProsjektManager()

    def related_kontos(self):
        try:
            return self.related_kontos_cache
        except:
            self.related_kontos_cache = list(Konto.objects.bilagRelated(related = self))
            return self.related_kontos_cache

    def __unicode__(self):
        return self.name + ( " (%d)" % self.id )
    def get_absolute_url(self):
        return "/regnskap/show/external_actor/%d" % self.id
    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))
    

class Bilag(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable = False)
    bilagsnummer = models.IntegerField(editable = False) #Automatic?
    dato = models.DateField()
    beskrivelse = models.CharField(max_length=256)
    external_actor = models.ForeignKey(Exteral_Actor,editable = False, null = True, related_name="bilag")
    registrerd_by = models.ForeignKey(User, editable=False, null=True)
    prosjekt = models.ForeignKey(Prosjekt)
    objects = BaseProsjektManager()
    def getInnslag(self):
        try:
            return self.innslag_cache
        except:
            self.innslag_cache = list(self.innslag.select_related('konto'))
            return self.innslag_cache
    def related_kontos(self):
        try:
            return self.related_kontos_cache
        except:
            self.related_kontos_cache = list(Konto.objects.filter(innslag__bilag = self).distinct())
            return self.related_kontos_cache
    def getNumInnslag(self):
        return len(self.getInnslag())
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
    def getNummer(self):
        return mark_safe(str(self.dato.year) + "&#8209;" + str(self.bilagsnummer))
    def __unicode__(self):
        return mark_safe("%s&#8209;%s %s" % (self.dato.year, self.bilagsnummer, self.beskrivelse))
    def get_absolute_url(self):
        return "/regnskap/show/bilag/%d" % self.id
    def innslag_sum(self):
        """
        Get the sum of the values in the inslags. This should always be zero!!!, and
        this method is used to check concistency.
        This is not runned automatically by django form framework, but is used to
        show warnings that something is wrong in the database (shoud never happen)
        """
        sum = Decimal(0)
        for i in self.getInnslag():
            sum += i.value
        return sum

def _bilag_upload_to(instance, filename):
    return "bilag/%s/%s-%s" % (instance.dato.year, instance.bilag.id, filename)

class BilagFile(models.Model):
    bilag = models.ForeignKey(Bilag, related_name="files")
    file = models.CharField(max_length=100)
    def url(self):
        return settings.MEDIA_URL + self.file
    def saveFile(self, file_content, file_name = u""):
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT,str(self.bilag.dato.year))):
            os.makedirs(os.path.join(settings.MEDIA_ROOT,str(self.bilag.dato.year)))
        self.file = os.path.join(str(self.bilag.dato.year),u"%d-%s" % ( self.bilag.bilagsnummer, file_name))
        with open(os.path.join(settings.MEDIA_ROOT, self.file),"wb+") as f:
            f.write(file_content)

class Innslag(models.Model):
    AVAILABLE_TYPE = (
      (0,'Debit'),
      (1,'Kredit')
    )
    bilag = models.ForeignKey(Bilag, related_name='innslag')
    konto = models.ForeignKey(Konto, related_name='innslag')
    
    belop = models.DecimalField(max_digits=16,decimal_places=2, blank=True, null=False)
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
    def _value(self):
        if self.type == 0:
            return self.belop
        return -self.belop
    debit = property(_debitValue)
    kredit = property(_kreditValue)
    value = property(_value)
    