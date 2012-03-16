# -*- coding: utf-8 -*-
from models import *

from django import forms

from decimal import *


class BilagForm(forms.ModelForm):
    class Meta:
        model = Bilag
        exclude = ('prosjekt',)

class External_ActorForm(forms.ModelForm):
    class Meta:
        model = Exteral_Actor
        widgets = {
            'adress': forms.Textarea(attrs={'cols': 20, 'rows': 4}),
        }
        exclude = ('prosjekt',)

class BaseInnslagForm(forms.Form):
    #form fields gets added by the inslag_form_factory
    #Validation:
    def clean(self):
        cleaned_data = super(BaseInnslagForm, self).clean()
        ##Maks en verdi i kredit og debit
        debit = cleaned_data.get("debit")
        kredit = cleaned_data.get("kredit")
        if debit and kredit:
            #Begge feltene er gyldige formateringsmessig - la oss sjekke at maks ett er satt
            if debit!=None and kredit !=None:
                msg = u"Enten debit eller kredit kan inneholde verdi."
                self._errors["debit"] = self.error_class([msg])
                self._errors["kredit"] = self.error_class([msg])
                del cleaned_data["kredit"]
                del cleaned_data["debit"]
        return cleaned_data

def innslag_form_factory(prosjekt):
    kontos = forms.TypedChoiceField(
        coerce = lambda id: Konto.objects.get(id=id),
        choices = Konto.objects.toOptionGroups(prosjekt),
        empty_value = None,
        widget = forms.Select(attrs={'tabindex':'-1'})
    )
    debit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
        widget=forms.TextInput(attrs={'size':'10'}),
        required=False, # one of debit/kredit required(not both)
    )
    kredit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
        widget=forms.TextInput(attrs={'size':'10'}),
        required=False, # one of debit/kredit required(not both)
    )
    return type(str(prosjekt) + "InnslagForm", (BaseInnslagForm,), {
        'kontos' : kontos,
        'debit'  : debit,
        'kredit' : kredit,
    })

class BaseInnslagFormSet(forms.formsets.BaseFormSet):
    
    def clean(self):
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        debit = Decimal(0) # datatype with exact decimal fractions
        kredit = Decimal(0)
        for form in self.forms:
            if form.cleaned_data:
                debit += form.cleaned_data['debit'] or 0
                kredit += form.cleaned_data['kredit'] or 0
        if debit != kredit:
            raise forms.ValidationError(u"Kredit og debit må summere til samme tall")

class BilagFileForm(forms.ModelForm):
    class Meta:
        model = BilagFile
        exclude = ('bilag',)

def bilag_file_form_factory(client):
    return type()
