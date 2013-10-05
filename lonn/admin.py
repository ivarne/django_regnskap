from django.contrib import admin
from django_regnskap.lonn.models import *

admin.site.register(Ansatt)
admin.site.register(Skattekort)
admin.site.register(LonnPeriode)
admin.site.register(KontoProxy)
admin.site.register(LonnArt)
admin.site.register(LonnAnsattPeriode)
admin.site.register(LonnAnsattPeriodeArt)