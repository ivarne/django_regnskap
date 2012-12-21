# -*- coding: utf-8 -*-
# Create your views here.
## standard includes
import os
## my files import
from django_regnskap.regnskap.models import *
from django_regnskap.regnskap.forms import *
from django_regnskap.django_dropbox.decorator import get_dropbox,dropbox_user_required
## django import
from django.shortcuts import render_to_response, render
from django.forms.formsets import formset_factory
from django.contrib import messages
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse



import json

from operator import itemgetter

from datetime import datetime, date

def registrerBilagForm(request, prosjekt, extra):
    NumberOfInnslag = int(extra or 5)
    prosjekt = Prosjekt.objects.get(navn = prosjekt)
    InnslagForm = innslag_form_factory(prosjekt)
    InnslagFormSet = formset_factory(InnslagForm, extra = NumberOfInnslag, formset=BaseInnslagFormSet)
    if(request.method == 'POST'):
        bilagform   = BilagForm(request.POST, prefix="bilag")
        innslagform = InnslagFormSet(request.POST, prefix="innslag")
        external_actor = External_ActorForm(request.POST, prefix="external")
        bilag_file_form = BilagFileForm(request.POST, request.FILES, prefix="files")
        if bilagform.is_valid() and innslagform.is_valid():
            b = bilagform.instance
            b.prosjekt = prosjekt
            if(external_actor.is_valid()):
                if external_actor.instance.pk == None:
                    external_actor.instance.prosjekt = prosjekt
                external_actor.save()
                b.external_actor = external_actor.instance
            bilagform.save()
            for innslag in innslagform:
                cd = innslag.cleaned_data
                if cd: # do not save the empty innslags
                    inn = Innslag()
                    inn.bilag = bilagform.instance
                    inn.konto = cd["kontos"]
                    inn.belop = cd["debit"] or cd["kredit"]
                    inn.type = not cd["debit"] or 0
                    inn.save()
            #try:
            bilag_file_form.save(b)
            #except Exception, e:
            #    messages.add_message(request, messages.ERROR, "Det skjedde en feil med lagring av filer (%s)" % e)
            messages.add_message(request, messages.SUCCESS, 'Bilag lagret med bilagsnummer <a href="%s">%s></a>.' % (bilagform.instance.get_absolute_url(), bilagform.instance.getNummer()))
            return HttpResponseRedirect(request.path)
        messages.add_message(request, messages.ERROR, 'Det var feil med valideringen av bilagsregistreringen.')
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
        external_actor = External_ActorForm(prefix="external")
        bilag_file_form = BilagFileForm(prefix="files")
    return render_to_response('bilagRegistrering.html', {
        'prosjekt'      : prosjekt,
        'bilagform'     : bilagform,
        'innslagform'   : innslagform,
        'external_a_form':external_actor,
        'url'           : request.path,
        'bilag_file_form':bilag_file_form,
    },RequestContext(request))

def inngaaendeBalanseForm(request, prosjekt, year):
    year = int(year)
    prosjekt = Prosjekt.objects.get(navn = prosjekt)
    InnslagForm = innslag_form_factory(prosjekt)
    InnslagFormSet = formset_factory(InnslagForm, extra = 0, formset=BaseInnslagFormSet)
    #collect usefull infromation
    
    bilagform   = BilagForm(prefix="bilag", initial={
                'dato' : date(year,1,1),
                'beskrivelse': u"Inngående balanse %d" % year,
                })
    initial_inslag = []
    for konto in Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (year-1,)).filter(kontoType = 1):
        v = (konto.sum_debit or 0) - (konto.sum_kredit or 0)
        initial_inslag.append({
            'debit': v if v >= 0 else None,
            'kredit': -v if v < 0 else None,
            'kontos': konto.id,
        })
    for konto in Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (year-1,)).filter(kontoType = 2):
        v = (konto.sum_debit or 0) - (konto.sum_kredit or 0)
        initial_inslag.append({
            'debit': v if v > 0 else None,
            'kredit': -v if v <= 0 else None,
            'kontos': konto.id,
        })
    innslagform = InnslagFormSet(prefix="innslag", initial=initial_inslag)
    external_actor = External_ActorForm(prefix="external")
    bilag_file_form = BilagFileForm(prefix="files")
    return render_to_response('bilagRegistrering.html', {
        'prosjekt'      : prosjekt,
        'bilagform'     : bilagform,
        'innslagform'   : innslagform,
        'external_a_form':external_actor,
        'bilag_file_form':bilag_file_form,
    },RequestContext(request))

def ajaxExternalActors(request, prosjekt):
    actors = Exteral_Actor.objects.prosjekt(prosjekt)
    ret = []
    for a in actors:
        ret.append( {'id': a.id, 'name': a.name, 'email': a.email, 'adress': a.adress,'org_nr': a.org_nr})
    return HttpResponse(json.dumps(ret,sort_keys=True))

@dropbox_user_required
def ajaxDropboxUploads(request,dropbox_client):
    newFiles = BilagFileForm.get_files_from_dropbox(dropbox_client)
    newFiles = ["""<li><label><input type="checkbox" id="asdf" value="%s" name="files-previousUploads"><a href="/media/upload/%s">%s</a></label></li>""" % (file,file,label) for file,label in newFiles]
    return HttpResponse("\n".join(newFiles))