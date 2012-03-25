from django.contrib import admin
from django_regnskap.regnskap.models import *

class BilagAdmin(admin.ModelAdmin):
    list_display = ('bilagsnummer', 'dato',) # 'innslag')
#    filter_horizontal = ('innslag',)

#admin.site.register(Bilag, BilagAdmin)
#admin.site.register(Innslag)
admin.site.register(Konto)
admin.site.register(Exteral_Actor)
admin.site.register(Prosjekt)
