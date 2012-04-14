# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *

from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.http import HttpResponse

#system imports
from datetime import date
from decimal import Decimal


def konto(request,id):
    konto = Konto.objects.get(pk = id)
    innslags = konto.innslag.order_by('-bilag__dato')
#    omsettning = 
    return render_to_response( 'show/konto.html',{
        'konto' : konto,
        'innslags': innslags,
        'years'  : range(2011,date.today().year+1),
        },RequestContext(request))

def kontoList(request, prosjekt = ""):
    kontos = Konto.objects.order_by('nummer')
    if prosjekt:
        print prosjekt
        kontos = kontos.filter(prosjekt__navn = prosjekt)
    return render_to_response('show/kontoList.html',{
    'kontos' : kontos,
    })

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

def konto_graph(request, year, konto_id):
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    # Collect data
    konto = Konto.objects.get(pk = konto_id)
    innslags = konto.innslag.order_by('bilag__dato').filter(bilag__dato__year = year)
    # make plot
    fig=Figure()
    fig.suptitle(u"%s (År:%s)"% (konto, unicode(year)))
    ax=fig.add_subplot(111)
    x=[]
    y=[]
    sum = Decimal(0)
    for innslag in innslags:
        x.append(innslag.bilag.dato)
        y.append(sum)
        print innslag.value
        x.append(innslag.bilag.dato)
        sum += innslag.value
        y.append(sum)
    ax.plot_date(x, y, '-')
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
        