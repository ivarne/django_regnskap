from django.db import models

from django.contrib.auth.models import User


# Kontoplan
class Konto(models.Model):
    AVAILABLE_KONTO_TYPE = (
      (1,'Eiendeler'),
      (2,'Egenkapital og gjeld'),
      (3,'Salg og driftsinntekt'),
      (4,'Varekostnad'),
      (5,'Lonnskonstnad'),
      (6,'Annen driftskostnad'),
      (7,'Av- og nedskrivninger'),
      (8,'Finans')
    )
    kontoType = models.IntegerField(choices=AVAILABLE_KONTO_TYPE)
    nummer = models.IntegerField(primary_key=True)
    tittel = models.CharField(max_length=256)

    def __unicode__(self):
        return unicode(self.nummer) +' '+self.tittel

class Exteral_Actor(models.Model):
    name = models.CharField(max_length = 256)
    email = models.EmailField(blank = True)
    adress = models.TextField(blank = True)
    org_nr = models.CharField(blank = True, max_length = 100)
    archived = models.DateField(editable = False, blank=True, null=True)
    def __unicode__(self):
        return str(self.id) + " " + self.name

class Bilag(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable = False)
    bilagsnummer = models.IntegerField(editable = False) #Automatic?
    dato = models.DateField()
    beskrivelse = models.CharField(max_length=256)
    external_actor = models.ForeignKey(Exteral_Actor,editable = False, null = True)
    def __unicode__(self):
        return str(self.bilagsnummer)
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

class Innslag(models.Model):
    AVAILABLE_TYPE = (
      (0,'Debit'),
      (1,'Kredit')
    )
    prosjekt = models.ForeignKey('Prosjekt')
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

class Prosjekt(models.Model):
    navn = models.CharField(max_length=256)
    beskrivelse = models.TextField()
    
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    dropbox_token = models.CharField(max_length=256)
    