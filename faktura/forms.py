# -*- coding: utf-8 -*-
from models import *

from django import forms
from django.forms.formsets import BaseFormSet

import datetime

class FakturaForm(forms.Form):
    date = forms.DateField(initial=datetime.date.today)
    frist_dager = forms.IntegerField(
        min_value = 1,
#        initial   = 20,
    )
    frist = forms.DateField()
    mellomverende = forms.ModelChoiceField(queryset = Konto.objects.filter(kontoType = 1, nummer__lt = 1900))


#class VareItemForm(forms.Form):
class VareItemForm(forms.ModelForm):
    class Meta:
        model = FakturaVare
        exclude = ('konto','faktura','mva')
    vare = forms.ModelChoiceField(
        queryset = Vare.objects.all(),
        widget   = forms.TextInput(attrs={'size':'5','placeholder':u'Søk','class':'vare-search vare-id search'}),
    )
    name   = forms.CharField(
        widget = forms.TextInput(attrs={'size':'40','class': 'vare-text'}),
    )
    ammount = forms.FloatField(
        widget=forms.TextInput(attrs={'size':'3','class':'vare-antall'}),
        min_value = 1,
        #widget = forms.Select(attrs={'class':'vare-antall'}),
        #choices = zip(range(1,10),range(1,10)),
        #coerce = int
    )
    price   = forms.FloatField(
        widget=forms.TextInput(attrs={'size':'10','class':'vare-pris'}),
        min_value = 0
    )

class VareItemsFormSet(BaseFormSet):
    form = VareItemForm
    extra = 6
    can_order = False
    can_delete = False
    max_num = None
    def setFaktura(self, faktura):
        for f in self.forms:
            f.instance.faktura = faktura
    def save(self):
        for f in self.forms:
            if f.cleaned_data:
                f.save()

class FakturaBetaling(forms.Form):
    faktura_id = forms.IntegerField(
        widget = forms.HiddenInput()
    )
    date  = forms.DateField(
        initial = datetime.date.today,
        widget  = forms.TextInput(attrs={'size':'10','class':'date-input'}),
    )
    belop = forms.FloatField(min_value=0)
    innbetaling_konto = forms.ModelChoiceField(
        queryset = Konto.objects.filter(kontoType=1)
    )