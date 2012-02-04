from django.db import models

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

class Bilag(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    bilagsnummer = models.IntegerField() #Automatic?
    dato = models.DateField()
    innslag = models.ManyToManyField(Konto, through='Innslag')
    def __unicode__(self):
        return str(self.bilagsnummer)
    def _getKredit(self):
        self.innslag.filter(isKredit)
    def _getDebit(self):
        self.innslag.filter(isDebit)
    innslagKredit = property(_getKredit)
    innslagDebit = property(_getDebit)

class Innslag(models.Model):
    krosjekt = models.ForeignKey(Prosjekt)
    bilag = models.ForeignKey(Bilag, related_name='bilaget')
    konto = models.ForeignKey(Konto)
    debit = models.DecimalField(max_digits=16,decimal_places=2, null=True)
    kredit = models.DecimalField(max_digits=16,decimal_places=2, null=True)
    def __unicode__(self):
        return unicode(self.konto.nummer) +' '+unicode(self.debit)+'|'+unicode(self.kredit)
    def isDebit(self):
        return self.debit!=Null
    def isKredit(self):
        return self.kredit!=Null
        
class Prosjekt(models.Model):
    navn = models.CharField(max_length=256)
    beskrivelse = models.TextField()