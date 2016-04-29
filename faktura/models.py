# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation

from django_regnskap.regnskap.models import *


from django_extensions.db.fields.json import JSONField


from decimal import *
from datetime import date


class AbstractVare(models.Model):
    """The vare class is abstract so that we can have a copy registrer"""
    class Meta:
        abstract = True
    MVA_CATEGORIES = (
        (0, '0%'),
        (1, '15%'),
        (2, '25%')
    )
    name  = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=16,decimal_places=2)
    mva   = models.IntegerField(choices= MVA_CATEGORIES)
    konto = models.ForeignKey( # konto varen skal føres til intekt for
        Konto,
        limit_choices_to = {'kontoType':3}
    )
    def __unicode__(self):
        return self.name
    def getMva(self):
        return self.MVA_CATEGORIES[self.mva][1]

class Vare(AbstractVare):
    """Represntasjon av varene som er i vare registeret"""
    active = models.BooleanField(default = True)
    prosjekt = models.ForeignKey(Prosjekt)

class Template(models.Model):
    #interne felt
    prosjekt    = models.ForeignKey(Prosjekt)
    objects     = BaseProsjektManager()
    mellomverende = models.ForeignKey(Konto, related_name="template_mellomverende")
    days_untill_forfall = models.PositiveIntegerField()
    # alle tekst felt som skal på fakturaen
    name        = models.CharField(max_length=20,unique=True)
    adress      = models.TextField()
    org_nr      = models.CharField(max_length=20)
    bank_navn   = models.CharField(max_length=20)
    bank_konto  = models.CharField(max_length=20)
    tlf         = models.CharField(max_length=20)
    email       = models.EmailField()
    innbetaling_konto = models.ForeignKey(Konto, related_name="template_innbetaling")
    def get_template_fields(self):
        return {
            'name'        : self.name, 
            'adress'      : self.adress,
            'org_nr'      : self.org_nr,
            'bank_navn'   : self.bank_navn,
            'bank_konto'  : self.bank_konto,
            'tlf'         : self.tlf,
            'email'       : self.email,
            'innbetaling_konto_id': self.innbetaling_konto.id,
        }
    def get_absolute_url(self):
        return u'/faktura/create/%s/%d' % (self.prosjekt.navn, self.id)
    def __unicode__(self):
        return self.name

class FakturaManager(BaseProsjektManager):
    def getPaymentsDue(self, projekt = None, periods = (None,None)):
        """
        Get the mony ammounts that is due, but not registrerd as payed in the relevant preiods
        param: project (the project you are interrested in the due ammounts for)
        periods: a sequence of datetime objects that encloses the time interval you are interrested in.
                 inclusive from, and exclusive to use None for infinete beginning and end
                 ex.
                 (None, datetime('now - 1 week'), datetime.now(), datetime('now + 1 month'), None)
                 wil return a list of due amounts with
                 [
                     #payments more overdue than 1 week
                     # payments overdue the last week
                     #payments due in the next month
                     #payments due later than the next month
                 ]
        """
        qs = self.prosjekt(project) # get a project filtered QuerySet
        qs = qs.filter(status = 1)  # count only sendt un
        qs.annotate('outstanding',SUM())

class Faktura(models.Model):
    STATUS_VALUES = (
        (0, 'Kladdet'),
        (1, 'Sendt'),
        (2, 'Purret'),
        (3, 'Inkasso'),
        (4, 'Betalt'),
        (5, 'Slettet'),
    )
    number = models.IntegerField(editable = False, default=0)
    status = models.IntegerField(choices=STATUS_VALUES)
    date = models.DateField()
    frist = models.DateField()
    prosjekt = models.ForeignKey(Prosjekt)
    mellomverende = models.ForeignKey(Konto)
    objects = FakturaManager()
    data = JSONField() # data used to generate the PDF file
    #bilag = models.ManyToManyField(Bilag)
    kunde = models.ForeignKey(Exteral_Actor)
    template = models.ForeignKey(Template)
    bilags = GenericRelation(Bilag)
    def getNumber(self):
        if self.number:
            return u"%s-%s" % (self.date.year, self.number)
        return u'#'
    def content_type(self):
        return ContentType.objects.get_for_model(self)
    def totalPrice(self):
        tp = 0.0
        for vare in self.fakturavare.all():
            tp += vare.totalPrice()
        return tp
    def getOutstanding(self):
        """Finn ut hvor mye som er utestående på fakturaen ved å summere opp verdier på mellomværende konto"""
        sum = Decimal(0)
        for innslag in Innslag.objects.filter(bilag__object_id = self.id, bilag__content_type = self.content_type()).filter(konto = self.mellomverende).all():
            sum += innslag.value
        return sum
    def related_kontos(self):
        try:
            return self.related_kontos_cache
        except:
            self.related_kontos_cache = list(Konto.objects.filter(innslag__bilag__object_id = self.pk, innslag__bilag__content_type = self.content_type()).distinct().order_by("nummer"))
            return self.related_kontos_cache
    def assignNumber(self, *args, **kwargs):
        """Assign a fakturanumber to the Faktura (done while sending)"""
        from django.db import connection, transaction
        with transaction.atomic():
            cursor = connection.cursor()
            cursor.execute("SELECT `number` FROM `"+self._meta.db_table+ "` WHERE YEAR(`date`) = %s ORDER BY `number` DESC FOR UPDATE;",[self.date.year])
            self.number = cursor.fetchone()[0] + 1
            self.save()
        return self.number
    def get_data_for_sending(self):
        """this function collects data from relations that needs to be copied into data when the status is changed to sendt"""
        return {
            'template': self.template.get_template_fields(),
            'kunde'   : {'id': self.kunde.id, 'name': self.kunde.name, 'email': self.kunde.email, 'adress': self.kunde.adress,'org_nr': self.kunde.org_nr}
        }
    def getStatus(self):
        return self.STATUS_VALUES[self.status][1]
    def alert(self):
        if self.status == 1 and self.frist < date.today(): # sent og over frist
            return True
        if self.status == 2: # purret
            return True
        if self.status == 3: # inkasso
            return True
        return False
    def get_absolute_url(self):
        return '/faktura/show/%d' % self.id
    def __unicode__(self):
        return u"%s %s (%s)" % (self.getNumber(), self.kunde ,self.getStatus())

class FakturaVare(AbstractVare):
    class Meta:
        db_table = "faktura_faktura_vare"
    faktura = models.ForeignKey(Faktura, related_name="fakturavare")
    vare = models.ForeignKey(Vare, related_name="fakturavare")
    ammount = models.FloatField()
    def totalPrice(self):
        return self.ammount * float(self.price)
    def save(self):
        self.mva = self.vare.mva
        self.konto = self.vare.konto
        super(FakturaVare,self).save()
