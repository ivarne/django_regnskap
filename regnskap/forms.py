# -*- coding: utf-8 -*-
from models import *

from django import forms

from decimal import *


class BilagForm(forms.ModelForm):
    class Meta:
        model = Bilag
        exclude = ('external_actor',)

class External_ActorForm(forms.ModelForm):
    class Meta:
        model = Exteral_Actor
        widgets = {
            'adress': forms.Textarea(attrs={'cols': 20, 'rows': 4}),
        }

class kontoFilterToChoice(object):
    def __iter__(self):
        types = [('','')]
        #reverse sort to get them out in correct order using pop()
        kontos  = list(Konto.objects.order_by('-nummer').all())
        konto   = kontos.pop()
        try:
            for i, kategori in Konto.AVAILABLE_KONTO_TYPE:
                subtypes = []
                while konto.kontoType == i:
                    subtypes.append((konto.nummer, str(konto.nummer) + ' ' + konto.tittel,))
                    konto = kontos.pop() #last element
                types.append([kategori, subtypes])
        except IndexError: #kontos.pop() when the list is emptpy
            types.append([kategori, subtypes])
        return iter(types)

class InnslagForm(forms.Form):
    kontos = forms.TypedChoiceField(
        coerce = lambda id: Konto.objects.get(nummer=id),
        choices = kontoFilterToChoice(),
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
    
    #Validation:
    def clean(self):
        cleaned_data = super(InnslagForm, self).clean()
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
