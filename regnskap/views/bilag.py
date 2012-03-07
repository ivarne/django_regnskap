# Create your views here.
## standard includes
import os
## my files import
from regnskap.models import *
from regnskap.forms import *
## django import
from django.shortcuts import render_to_response, render
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse

from django.core import serializers


def registrerBilagForm(request):
    NumberOfInnslag = 5
    InnslagFormSet = formset_factory(InnslagForm, extra = NumberOfInnslag, formset=BaseInnslagFormSet)
    if(request.method == 'POST'):
        bilagform   = BilagForm(request.POST, prefix="bilag")
        innslagform = InnslagFormSet(request.POST, prefix="innslag")
        external_actor = External_ActorForm(request.POST, prefix="external")
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
        external_actor = External_ActorForm(prefix="external")
    return render_to_response('bilagRegistrering.html', {
        'bilagform'     : bilagform,
        'innslagform'   : innslagform,
        'external_a_form':external_actor,
        'url'           : request.path,
        'buttoncounter' : iter(xrange(NumberOfInnslag)),
        'searchcounter' : iter(xrange(NumberOfInnslag)),
    },RequestContext(request))
    
def ajaxExternalActors(request):
    queryset = Exteral_Actor.objects.all()
    response = HttpResponse()
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(queryset, ensure_ascii=False, stream=response)
    return response
    