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