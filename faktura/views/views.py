# -*- coding: utf-8 -*-

# django imports
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext

# django_regnskap imports
from django_regnskap.faktura.models import *
from django_regnskap.faktura.forms import FakturaBetaling

#general
import datetime

def betal_faktura(request, id):
    if request.method != 'POST':
        raise Exception('Wrong method')
    faktura = Faktura.objects.get(id = id)
    fb = FakturaBetaling(request.POST, prefix ='faktura_betaling' )
    if fb.is_valid() and fb.cleaned_data['faktura_id'] == faktura.id:
        fdata = fb.cleaned_data
        if faktura.getOutstanding() == fdata['belop']:
            bilag_text = u"Faktura %s Betalt" % (faktura.getNumber(),)
            faktura.status = 4 # Betalt
        else:
            bilag_text = u"Faktura %s Delbetaling" % (faktura.getNumber(),)
        bilag = Bilag(
            dato = fdata['date'],
            beskrivelse = bilag_text,
            external_actor = faktura.kunde,
            prosjekt = faktura.prosjekt,
        )
        bilag.save()
        i1 = Innslag(
            bilag = bilag,
            konto = fdata['innbetaling_konto'],
            belop = fdata['belop'],
            type = 0 #debit
        )
        i2 = Innslag(
            bilag = bilag,
            konto = faktura.mellomverende,
            belop = fdata['belop'],
            type = 1 #kredit
        )
        i1.save()
        i2.save()
        faktura.bilag.add(bilag)

        faktura.data['log'].append(u"Betaling registrert (%s kr) %s av %s"%(fdata['belop'],datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), request.user))
        faktura.save()
        
        return HttpResponseRedirect( '/faktura/show/'+str(faktura.id) )

def show_faktura(request, id):
    faktura = Faktura.objects.get(id = id)
    faktura_betaling_form = FakturaBetaling(prefix='faktura_betaling', initial={'faktura_id':faktura.id, 'innbetaling_konto':faktura.template.innbetaling_konto_id})
    if faktura.status == 0:   # Kladdet
        pass
    elif faktura.status == 1: # Sendt
        pass
    elif faktura.status == 2: # Purret
        pass
    elif faktura.status == 3: # Inkasso
        pass
    elif faktura.status == 4: # Betalt
        pass
    elif faktura.status == 5: # Slettet
        pass
    return render_to_response('show.html',{
        'faktura' : faktura,
        'faktura_betaling_form':faktura_betaling_form,
    },RequestContext(request))

def list_faktura(request,prosjekt):
    fakturas = Faktura.objects.filter(prosjekt__navn = prosjekt)
    status = fakturas
    return render_to_response('list.html',{
        'fakturas' : fakturas.order_by('status','date'),
        'prosjekt' : prosjekt,
    },RequestContext(request))

def send_faktura(request):
    if request.method != 'POST':
        raise Exception('Wrong method')
    faktura = Faktura.objects.get(id = request.POST['faktura_id'])
    if faktura.status != 0: #kladdet
        raise Http404('Fakturaen har allerede blitt sendt')
    faktura.status = 1 #sendtm
    faktura.assignNumber()
    faktura.data['log'].append("Sendt: %s av %s"% (datetime.datetime.today().strftime('%Y-%m-%d %H:%M:%S'), request.user))
    faktura.data['template'] = faktura.template.get_template_fields()
    bilag = Bilag(
        dato = faktura.date,
        beskrivelse = u"Faktura %s-%s Sendt" % (faktura.date.year, faktura.number),
        external_actor = faktura.kunde,
        prosjekt = faktura.prosjekt
    )
    bilag.save()
    Innslag(
        bilag = bilag,
        konto = faktura.mellomverende,
        belop = faktura.totalPrice(),
        type = 0, # debit
    ).save()
    konto_cache = {} # summer opp varer som skal på samme konto
    for vare in faktura.fakturavare.all():
        if vare.konto.id in konto_cache:
            konto_cache[vare.konto.id].belop += vare.totalPrice()
            konto_cache[vare.konto.id].save()
        else:
            i = Innslag(
                bilag = bilag,
                konto = vare.konto,
                belop = vare.totalPrice(),
                type = 1, # kredit
            )
            i.save()
            konto_cache[vare.konto.id] = i
    faktura.bilag.add(bilag) 
    faktura.save()
    return HttpResponseRedirect( '/faktura/show/'+str(faktura.id) )