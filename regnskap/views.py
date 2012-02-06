# Create your views here.
## standard includes
import os
## my files import
from regnskap import models
from regnskap.forms import *
## django import
from django.shortcuts import render_to_response
from django.forms.formsets import formset_factory
from django.core.context_processors import csrf


def default(request):
    bilag_list = models.Bilag.objects.all()
    return render_to_response('default.html',{'bilag_list': bilag_list})

def registerform(request):
    konto_plan = models.Konto.objects.all()
    files = os.listdir(os.path.join('/','var','www','django_regnskap'))
    return render_to_response('form.html',{'files': files})
    
def registerAction(request):
    pass

def registrerBilagForm(request):
    InnslagFormSet = formset_factory(InnslagForm, extra=5)
    if(request.method == 'POST'):
        bilagform   = BilagForm(request.POST, prefix="bilag")
        innslagform = InnslagFormSet(request.POST, prefix="innslag")
        if form.is_valid():
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
                
            
            return HttpResponseRedirect(request.path)
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
    c = {
        'bilagform' : bilagform,
        'innslagform': innslagform,
        'url' : request.path,
    }
    c.update(csrf(request)) # add Cross Site Request Forgery Protection
    return render_to_response('bilagRegistrering.html', c)
    