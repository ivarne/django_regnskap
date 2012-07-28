# django imports
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404

# django_regnskap imports
from django_regnskap.faktura.models import *
from django_regnskap.faktura.forms import *
from django_regnskap.regnskap.forms import *

#general imports
import json
import datetime

def create_faktura(request, prosjekt_name, template, num):
    template = Template.objects.get(id = template)
    prosjekt = template.prosjekt
    if prosjekt.navn != prosjekt_name:
        raise Http404
    faktura_initial = {
        'date': datetime.date.today().strftime('%Y-%m-%d'),
        'frist_dager': template.days_untill_forfall,
        'mellomverende': template.mellomverende
    }
    if(request.method == 'POST'):
        faktura_form = FakturaForm(request.POST, initial=faktura_initial, prefix = 'faktura')
        vare_form    = VareItemsFormSet(request.POST, prefix = 'vare')
        to_form      = External_ActorForm(request.POST, prefix = 'to')
        if to_form.is_valid():
            to_form.instance.prosjekt = prosjekt
            kunde = to_form.save() # oppdater info om mottaker
            messages.add_message(request, messages.SUCCESS, 'Mottaker info ble lagret')
            if faktura_form.is_valid() and vare_form.is_valid():
                fd = faktura_form.cleaned_data
                vd = vare_form.cleaned_data
                faktura = Faktura(
                    prosjekt = prosjekt,
                    date = fd['date'],
                    frist = fd['frist'],
                    data = {
                        'kunde': to_form.cleaned_data,
                        'log': ["Kladdet: %s av %s" % (datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), request.user)]
                    },
                    status = Faktura.STATUS_VALUES[0][0],
                    mellomverende = fd['mellomverende'],
                    kunde = kunde,
                    template = template,
                )
                faktura.save()
                vare_form.setFaktura(faktura)
                vare_form.save()
                messages.add_message(request, messages.SUCCESS, 'Faktura lagret')
                return HttpResponseRedirect(faktura.get_absolute_url())
            messages.add_message(request, messages.ERROR, 'Det ble en feil med registrering av faktura')
    faktura_form = FakturaForm(prefix = 'faktura', initial=faktura_initial)
    vare_form    = VareItemsFormSet(prefix = 'vare')
    to_form      = External_ActorForm(prefix = 'to')
    varer = [{'id':v.id, 'name':v.name, 'price':float(v.price)} for v in Vare.objects.filter(active=True)]
    return render_to_response('create.html',{
        'prosjekt'     : prosjekt.navn,
        'faktura_form' : faktura_form,
        'vare_form'    : vare_form,
        'to_form'      : to_form,
        'varer'        : mark_safe(json.dumps(varer)),
        'template'     : template,
    },RequestContext(request))