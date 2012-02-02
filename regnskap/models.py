from django.db import models

# Create your models here.
class Konto(models.Model):
    AVAILABLE_KONTO_TYPE = (
      (1,'Eiendeler'),
      (2,'Egenkapital og gjeld'),
      (3,'Salg og driftsinntekt'),
      (4,'Varekostnad'),
      (5,'Lonnskonstnad'),
      (6,'Annen driftskostnad'),
      (7,'Av- og nedskrivninger',
      (8,'Finans')
    )
    kontoType = model.IntegerField(choices=AVAILABLE_KONTO_TYPE)
    nummer = model.IntegerField(primary_key=True)
    tittel = model.CharField(max_length=256)

class Bilag(models.Model):
    created = models.DateTimeField(auto_now_add=True)

    bilagsnummer = model.IntegerField() #Automatic?
    dato = model.DateField()
    innslag = model.ManyToManyField(Konto, trough='Innslag')

class Innslag(models.Model):
    bilag = model.ForeignKey(Bilag)
    konto = model.ForeginKey(Konto)
    debit = model.DecimalField(decimal_places=2)
    kredit = model.DecimalField(decimal_places=2)

