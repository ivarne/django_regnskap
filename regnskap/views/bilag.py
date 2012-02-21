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

def registrerBilagForm(request):
    NumberOfInnslag = 5
    InnslagFormSet = formset_factory(InnslagForm, extra = NumberOfInnslag)
    if(request.method == 'POST'):
        bilagform   = BilagForm(request.POST, prefix="bilag")
        innslagform = InnslagFormSet(request.POST, prefix="innslag")
        if bilagform.is_valid() and innslagform.is_valid():
            ##process data
            magicNumber = 7 ##GetID
            bilag = models.Bilag(bilagsnummer=magicNumber, dato=bilagform.dato, beskrivelse=bilagform.beskrivelse)
            bilag.save()
            
            for form in innslagform:
            
                ##REFACTOR: Do this directly in the form
                if form.eiendeler != 0:
                    konto = form.eiendeler
                elif form.egenkapital_gjeld != 0:
                    konto = form.egenkapital_gjeld 
                elif form.inntekter != 0:
                    konto = form.inntekter 
                elif form.kostnader != 0:
                    konto = form.kostnader
                else:
                    continue
                
                type = 1
                belop = form.kredit
                if form.debit != 0:
                    type = 0
                    belop = form.debit
                    
                innslag = models.Innslag(bilag=bilag)
                innslag.konto = models.Konto.get(id=konto)
                innslag.belop = belop
                innslag.type = type
                
                innslag.save()
                
            messages.add_message(request, messages.SUCESS, 'Bilag lagret.')
            return HttpResponseRedirect(request.path)
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
    return render_to_response('bilagRegistrering.html', {
        'bilagform' : bilagform,
        'innslagform': innslagform,
        'url'       : request.path,
        'kontos'    : Konto.objects.all().order_by('nummer'),
        'counter'   : iter(xrange(NumberOfInnslag)),
    },RequestContext(request))