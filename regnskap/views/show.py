from django_regnskap.regnskap.models import *

from django.template import RequestContext
from django.shortcuts import render_to_response, render

def konto(request,id):
    konto = Konto.objects.get(pk = id)
    innslags = konto.innslag.order_by('-bilag__dato')
#    omsettning = 
    return render_to_response( 'show/konto.html',{
        'konto' : konto,
        'innslags': innslags,
        },RequestContext(request))
        
def bilag(request,id):
    return render_to_response( 'show/bilag.html',{
        'bilag' : Bilag.objects.get(pk = id),
        },RequestContext(request))

def external_actor(request,id):
    ext = Exteral_Actor.objects.get(pk = id)
    bilags = ext.bilag.order_by('-dato')
    return render_to_response( 'show/external_actor.html',{
        'external_actor' : ext,
        'bilags'       : bilags,
        },RequestContext(request))