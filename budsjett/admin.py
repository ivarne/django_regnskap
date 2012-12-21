# -*- coding: utf-8 -*-
from django.contrib import admin

from django import forms

from django_regnskap.budsjett.models import *
from django_regnskap.budsjett.forms import *


class BudsjettPostInline(admin.TabularInline):
    model = BudsjettPost
    form = BudsjettPostForm

class BudsjettAdmin(admin.ModelAdmin):
    inlines = [
        BudsjettPostInline,
    ]
    list_display = ('name', 'fra', 'til', 'prosjekt')
    date_hierarchy = 'fra'
    save_as = True

# Lag proxy klasser for budsjett for hvert enkelt prosjekt slik at man får
# muliget til å registrere budsjett der man allerede vet hvilke kontoer det skal
# linkes mot
def prosjekt_admin(prosjekt):
    p_name = str(prosjekt.navn)
    class Meta:
        proxy = True
    queryset = lambda self, request: super(BudsjettAdmin, self).queryset(request).filter(prosjekt__navn=p_name)
    pBudsjett = type(
        str(prosjekt)+"budsjett",
        (Budsjett,),
        {
            'Meta':Meta,
            '__module__':__name__,
            'prosjekt_store_id': prosjekt.id,
        })
    pBudsjettPostForm = type(
        p_name+'BPF',
        (BudsjettPostForm,),
        {
            '__module__':__name__,
            'prosjekt_navn':p_name,
        })
    pBudsjettPostFormInline = type(
        p_name+'BPFI',
        (admin.TabularInline,),
        {
            '__module__':__name__,
            'form' : pBudsjettPostForm,
            'model': BudsjettPost,
        })
    pBudsjettAdmin = type(
        p_name+"budsjettAdmin",
        (BudsjettAdmin,),
        {
            '__module__':__name__,
            'queryset':queryset,
            'exclude' : ('prosjekt',),
            'inlines' : [pBudsjettPostFormInline],
        })
    admin.site.register(pBudsjett, pBudsjettAdmin)

for prosjekt in Prosjekt.objects.all():
    prosjekt_admin(prosjekt)
