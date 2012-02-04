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
    debit = 
    