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

from datetime import datetime

def registrerBilagForm(request, prosjekt):
    NumberOfInnslag = 5
    prosjekt = Prosjekt.objects.get(navn = prosjekt)
    InnslagForm = innslag_form_factory(prosjekt)
    InnslagFormSet = formset_factory(InnslagForm, extra = NumberOfInnslag, formset=BaseInnslagFormSet)
    if(request.method == 'POST'):
        bilagform   = BilagForm(request.POST, prefix="bilag")
        innslagform = InnslagFormSet(request.POST, prefix="innslag")
        try:
            inst = Exteral_Actor.objects.get(id = int(request.POST['external-id']))
        except:
            inst = None
        external_actor = External_ActorForm(request.POST, prefix="external", instance = inst)
        bilag_file_form = BilagFileForm(request.POST, request.FILES, prefix="files")
        if bilagform.is_valid() and innslagform.is_valid():
            b = bilagform.instance
            b.prosjekt = prosjekt
            if(external_actor.is_valid()):
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
            bilag_file_form.save(b,get_dropbox(request))
            #except Exception, e:
            #    messages.add_message(request, messages.ERROR, "Det skjedde en feil med lagring av filer (%s)" % e)
            messages.add_message(request, messages.SUCCESS, 'Bilag lagret med bilagsnummer %d-%d.' % (bilagform.instance.dato.year , bilagform.instance.bilagsnummer))
            return HttpResponseRedirect(request.path)
        external_id = request.POST['external-id']
        messages.add_message(request, messages.ERROR, 'Det var feil med valideringen av bilagsregistreringen.')
    else:
        bilagform   = BilagForm(prefix="bilag")
        innslagform = InnslagFormSet(prefix="innslag")
        external_actor = External_ActorForm(prefix="external")
        external_id = '';
        bilag_file_form = BilagFileForm(prefix="files")
    return render_to_response('bilagRegistrering.html', {
        'prosjekt'      : prosjekt,
        'bilagform'     : bilagform,
        'innslagform'   : innslagform,
        'external_a_form':external_actor,
        'url'           : request.path,
        'external_id'   : external_id,
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
    files = dropbox_client.metadata('upload')['contents']
    for f in files:
        f.update(dropbox_client.media(f['path']))
        f['modified'] = datetime.strptime(f["modified"],"%a, %d %b %Y %H:%M:%S +0000")
        f['file'] = f['path'][8:]
    files.sort(key=itemgetter('modified'))
    files.reverse()
    return render_to_response('bilag/dropboxList.html', {
        'files' : files,
    },RequestContext(request))