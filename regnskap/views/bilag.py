# Create your views here.
## standard includes
import os
## my files import
from regnskap import models
from regnskap.forms import *
## django import
from django.shortcuts import render_to_response, render
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect

def registrerBilagForm(request):
    NumberOfInnslag = 5
    InnslagFormSet = formset_factory(InnslagForm, extra = NumberOfInnslag,formset=BaseInnslagFormSet)
    if(request.method == 'POST'):
        bilagform   = BilagForm(request.POST, prefix="bilag")
        innslagform = InnslagFormSet(request.POST, prefix="innslag")
        if bilagform.is_valid() and innslagform.is_valid():
            bilagform.save()
            for innslag in innslagform:
                cd = innslag.cleaned_data
                if cd: # do not save the empty innslags
                    inn = Innslag()
                    inn.bilag = bilagform.instance
                    inn.prosjekt = Prosjekt.objects.get(id = 1)
                    inn.konto = cd["kontos"]
                    inn.belop = cd["debit"] or cd["kredit"]
                    inn.type = not cd["debit"] or 0
                    inn.save()
            messages.add_message(request, messages.SUCCESS, 'Bilag lagret.')
            return HttpResponseRedirect(request.path)
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
    return render_to_response('bilagRegistrering.html', {
        'bilagform'     : bilagform,
        'innslagform'   : innslagform,
        'url'           : request.path,
        'buttoncounter' : iter(xrange(NumberOfInnslag)),
        'searchcounter' : iter(xrange(NumberOfInnslag)),
    },RequestContext(request))