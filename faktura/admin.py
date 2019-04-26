from django.contrib import admin

from django_regnskap.faktura.models import *

class FakturaAdmin(admin.ModelAdmin):
    list_display = ('getNumber', 'kunde', 'date', 'frist', 'status', 'prosjekt')
    list_filter = ('prosjekt', 'status')

admin.site.register(Faktura, FakturaAdmin)
admin.site.register(Template)
admin.site.register(Vare)
