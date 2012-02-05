# Create your views here.
## standard includes
import os
## my files import
from regnskap import models
from regnskap.forms import *
## django import
from django.shortcuts import render_to_response
from django.forms.formsets import formset_factory


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
            
            return HttpResponseRedirect(request.path)
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
    return render_to_response('bilagRegistrering.html',{
        'bilagform' : bilagform,
        'innslagform': innslagform,
        'url' : request.path,
    })
    