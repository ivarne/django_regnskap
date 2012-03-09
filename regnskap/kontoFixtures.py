# -*- coding: utf-8 -*-
from models import *

# for å kjøre:
# $ python manage.py shell
# > import regnskap.kontoFixtures


## Desverre brukte ikke den gamle kontoplanen det samme oppsettet som oss
#  så jeg har måttet endre første siffer i kontoplan for å få ting til å stemme
#  med de nye kategoriene








kontos = [
(u"Leie Hybel", 313),
(u"Div. leie", 321),
(u"Div. inntekter", 341),
(u"Strøm", 611),
(u"Brensel", 612),
(u"Eiend. avg", 621),
(u"Forsikring", 622),
(u"Drift", 431),
(u"Vedlikehold", 641),
(u"Utstyr", 651),
(u"Renter inn", 811),
(u"Renter + gebyr", 821),
(u"Avskr. invent.", 711),
(u"Avskr. bygn.", 721),
(u"Vaktm. konto", 191),
(u"Sparebankenpluss", 190),
(u"M. TKS/NKSS", 121),
(u"M. leie", 150),
(u"M. div.", 151),
(u"M. vaktmester", 125),
(u"Inventar/utstyr", 110),
(u"Bygninger", 120),
(u"Lån H. legat", 212),
(u"Lån Kapellråd", 214),
(u"Nøkkelfond", 221),
(u"Egenkapital", 231),
(u"Resultat", 932),
]

# nye kontoer ivar vil ha inn
kontos.extend([
(u"Vaktmester Lønn", 501),
#(u"", ),
])


for k in Konto.objects.all():
    k.delete()

for konto, nr in kontos:
    k = Konto()
    k.nummer = nr
    k.tittel = konto
    k.kontoType = nr//100
    k.save()
