# -*- coding: utf-8 -*-
from models import *

from django import forms

from django_regnskap.budsjett import widgets
from django_regnskap.regnskap import models as regnskap_models

class BudsjettPostForm(forms.ModelForm):
    class Meta:
        model = BudsjettPost
        widgets = {
            'konto'  : widgets.DynamicSelectMultiple,
            'comment': forms.Textarea( attrs={'columns':40,'rows':4})
            }
        exclude = ()
    def __init__(self, *args, **kwargs):
        super(BudsjettPostForm, self).__init__(*args, **kwargs)
        try:
            prosjekt = self.prosjekt_navn
        except:
            prosjekt = None
        self.fields['konto'].choices = regnskap_models.Konto.objects.toOptionGroups(prosjekt=prosjekt, not_balanse= True)
