# -*- coding: utf-8 -*-

# django imports
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import RequestContext

# django_regnskap imports
from django_regnskap.lonn.models import LonnPeriode
from django_regnskap.regnskap.models import Konto, Bilag, Innslag

from decimal import Decimal, ROUND_HALF_DOWN
from datetime import datetime

# Helper function for å generere billag fra lønnsperioder
def get_bilag(periode, user):
    bilag = Bilag(
        dato = periode.dato,
        beskrivelse = u"Lønsskjøring %s" % (periode),
        prosjekt = periode.selskap.prosjekt,
        registrerd_by = user,
    )
    bilag.related_instance = periode
    konto_innslag = {}# summer opp varer som skal på samme konto
    def add_innslag(konto, belop):
        if konto in konto_innslag:
            i = konto_innslag[konto]
            i.belop += belop
        else:
            i = Innslag(
#                bilag = bilag,
                konto = konto,
                belop = belop,
                type = 1, # kredit (fikses etterpå hvis beløp bli negativ)
            )
            konto_innslag[konto] = i
    for pArt in periode.arts:
        add_innslag(pArt.lonnArt.konto_fra.konto, -pArt.sum)
        add_innslag(pArt.lonnArt.konto_til.konto,  pArt.sum)
        # Beregn arbeidsgiveravgift automatisk
        if pArt.lonnArt.konto_aga is not None:
            mul_aga = Decimal('0.141')
            add_innslag(pArt.lonnArt.konto_aga.konto,    -pArt.sum * mul_aga)
            add_innslag(pArt.lonnArt.konto_aga_til.konto, pArt.sum * mul_aga)
    sum = Decimal(0)
    for i in konto_innslag.values():
        i.belop = Decimal(i.belop).quantize(Decimal('0.01'),ROUND_HALF_DOWN)
        sum += i.belop
        if i.belop < 0:
            i.belop = abs(i.belop)
            i.type = 0 # debit
    if sum != 0:
        raise Exception(u"Beløpene i bilagsføringen for lønnskjøring summerer ikke til null")
    return (bilag,konto_innslag.values())

# TODO: Currently you have to do this manually
def prepare_tax(periode):
    pass
def prepare_vacation_pay(periode):
    pass

def finalize_periode(request, periode_id):
    periode = LonnPeriode.objects.get(id = periode_id)
    #prepare_tax(periode)
    #prepare_vacation_pay(periode)
    bilag, innslags = get_bilag(periode, request.user)
    if(request.method == 'POST'):
        bilag.save()
        for i in innslags:
            i.bilag = bilag
            i.save()
        periode.finalized = True
        periode.save()
        return HttpResponseRedirect(periode.get_absolute_url())
    return render_to_response('lonn/bilag.html',{
        'bilag': bilag,
        'innslags': innslags,
    },RequestContext(request))

#general
def show(request):
    return render_to_response('lonn/show.html',{
        'periodes': LonnPeriode.objects.order_by("-dato"),
    },RequestContext(request))

def periode(request, periode_id):
    periode = LonnPeriode.objects.get(id=periode_id)
    bilag_ids = tuple([int(b.id) for b in periode.bilags.all()])
    related_kontos = list(Konto.objects.bilagRelated(bilag_ids=bilag_ids))
    return render_to_response('lonn/periode.html',{
        'periode' : periode,
        'related_kontos':related_kontos,
        'bilags':periode.bilags.order_by('dato'),
    },RequestContext(request))
