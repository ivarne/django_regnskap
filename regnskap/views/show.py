# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *
from django_regnskap.regnskap.forms import *

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
#        print prosjekt
        kontos = kontos.filter(prosjekt__navn = prosjekt)
    return render_to_response('show/kontoList.html',{
    'kontos' : kontos,
    })

def bilag(request,id):
    bilag = Bilag.objects.get(pk = id)
    if(request.method == 'POST'):
        bilag_file_form = BilagFileForm(request.POST, request.FILES, prefix="files")
        bilag_file_form.save(bilag)
    else:
        bilag_file_form = BilagFileForm(prefix="files")
    return render_to_response( 'show/bilag.html',{
        'bilag' : bilag,
        'bilag_file_form' : bilag_file_form
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
#        print innslag.value
        x.append(innslag.bilag.dato)
        sum += innslag.value
        y.append(sum)
    ax.plot_date(x, y, '-')
    if x: # if there is transactions on the konto in the period
        # fill the period from the end of the year with a red line
        ax.plot_date([x[-1],date(int(year),12,31)],[y[-1],y[-1]],"r")
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
#    print type(ax)
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
        
