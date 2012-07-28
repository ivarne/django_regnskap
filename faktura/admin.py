from django.contrib import admin

from django_regnskap.faktura.models import *

admin.site.register(Faktura)
admin.site.register(Template)
admin.site.register(Vare)