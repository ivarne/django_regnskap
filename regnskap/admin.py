from django.contrib import admin
from regnskap.models import *

class BilagAdmin(admin.ModelAdmin):
    list_display = ('bilagsnummer', 'dato',) # 'innslag')
#    filter_horizontal = ('innslag',)

admin.site.register(Bilag, BilagAdmin)
admin.site.register(Innslag)
admin.site.register(Konto)
