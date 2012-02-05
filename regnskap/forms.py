from models import *

from django import forms

class BilagForm(forms.Form):
    kommentar = forms.CharField(
        max_length=255,
        required = False,
        )
    dato = forms.DateField(
        required = False,
        )

def kontoFilterToChoice(**kwargs):
    kontos = Konto.objects.filter(**kwargs)
    choices = [(0,'')]
    for konto in kontos:
        choices.append((konto.nummer, str(konto.nummer) + ' ' + konto.tittel))
    return choices

class InnslagForm(forms.Form):
    eiendeler = forms.TypedChoiceField(
        coerce = int,
        choices = kontoFilterToChoice(kontoType = 1),#'eiendeler')
        empty_value = 0
    )
    egenkapital_gjeld = forms.TypedChoiceField(
        coerce = int,
        choices = kontoFilterToChoice(kontoType = 2),#'Egenkapital og gjeld')
    )
    inntekter = forms.TypedChoiceField(
        coerce = int,
        choices = kontoFilterToChoice(kontoType = 3),#'Salg og driftsinntekt')
    )
    kostnader = forms.TypedChoiceField(
        coerce = int,
        choices = kontoFilterToChoice(kontoType__gte = 4),#'Varekostnad')
    )
    debit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
    )
    kredit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
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
            #og dersom minst ett av de inneholder verdi ma konto vare satt
            if debit!=None or kredit !=None:
                ##TODO: Sjekke at eksakt en konto er satt
                pass

        return cleaned_data