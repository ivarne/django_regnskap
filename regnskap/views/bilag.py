# Create your views here.
## standard includes
import os
## my files import
from django_regnskap.regnskap.models import *
from django_regnskap.regnskap.forms import *
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
        try:
            inst = Exteral_Actor.objects.get(id = int(request.POST['external-id']))
        except:
            inst = None
        external_actor = External_ActorForm(request.POST, prefix="external", instance = inst)
        if bilagform.is_valid() and innslagform.is_valid():
            if(external_actor.is_valid()):
                external_actor.save()
                b = bilagform.instance
                b.external_actor = external_actor.instance
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
        external_id = request.POST['external-id']
        messages.add_message(request, messages.ERROR, 'Det var feil med valideringen av bilagsregistreringen.')
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
        external_actor = External_ActorForm(prefix="external")
        external_id = '';
    return render_to_response('bilagRegistrering.html', {
        'bilagform'     : bilagform,
        'innslagform'   : innslagform,
        'external_a_form':external_actor,
        'url'           : request.path,
        'buttoncounter' : iter(xrange(NumberOfInnslag)),
        'searchcounter' : iter(xrange(NumberOfInnslag)),
        'external_id'   : external_id
    },RequestContext(request))
    
def ajaxExternalActors(request):
    queryset = Exteral_Actor.objects.all()
    response = HttpResponse()
    json_serializer = serializers.get_serializer("json")()
    json_serializer.serialize(queryset, ensure_ascii=False, stream=response)
    return response
    