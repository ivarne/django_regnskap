from models import *

from django import forms

class BilagForm(From):
    kommentar = forms.CharField(max_lenght=255)
    dato = forms.DateField()
    