from models import *

from django import forms

class BilagForm(forms.ModelForm):
    class Meta:
        model = Bilag
        exclude = ('bilagsnummer',)

def kontoFilterToChoice():
    types = [('','')]
    #reverse sort to get them out in correct order using pop()
    kontos  = list(Konto.objects.order_by('-nummer').all())
    konto   = kontos.pop()
    print 'filter'
    try:
        for i, kategori in Konto.AVAILABLE_KONTO_TYPE:
            subtypes = []
            while konto.kontoType == i:
                subtypes.append((konto.nummer, str(konto.nummer) + ' ' + konto.tittel,))
                konto = kontos.pop() #last element
            types.append([kategori, subtypes])
    except IndexError: #kontos.pop() when the list is emptpy
        types.append([kategori, subtypes])
    print types
    return types

class InnslagForm(forms.Form):
    kontos = forms.TypedChoiceField(
        coerce = int,
        choices = kontoFilterToChoice(),
        empty_value = None,
        widget = forms.Select(attrs={'tabindex':'-1'})
    )
    debit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
        widget=forms.TextInput(attrs={'size':'10'})
    )
    kredit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
        widget=forms.TextInput(attrs={'size':'10'})
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
            #if debit!=None or kredit !=None:
            ##TODO: Sjekke at eksakt en konto er satt
        return cleaned_data