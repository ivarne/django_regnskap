# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *
from django_regnskap.regnskap.forms import *

from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.http import HttpResponse
from django.conf import settings

#system imports
from datetime import date
from decimal import Decimal


def konto(request,id):
    konto = Konto.objects.get(pk = id)
    bilags = Bilag.objects.filter(innslag__konto = konto).order_by('-dato').prefetch_related('innslag__konto').prefetch_related('innslag__konto__prosjekt').prefetch_related('innslag').prefetch_related('external_actor')
#    omsettning = 
    return render_to_response( 'show/konto.html',{
        'konto' : konto,
        'bilags': bilags,
        'years'  : range(date.today().year, settings.REGNSKAP_FIRST_YEAR -1, -1),
        },RequestContext(request))

def kontoList(request, prosjekt = ""):
    kontos = Konto.objects.order_by('nummer')
    if prosjekt:
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

#stupid proxy for simple lookup of bilag from YYYY-# format
def bilag_nummer(request, year, nummer):
    b = Bilag.objects.get(dato__year = year, bilagsnummer = nummer)
    return bilag(request, b.pk)

def external_actor(request,id):
    ext = Exteral_Actor.objects.get(pk = id)
    bilags = ext.bilag.order_by('-dato').prefetch_related('innslag').prefetch_related('innslag__konto')
    return render_to_response( 'show/external_actor.html',{
        'external_actor' : ext,
        'bilags'       : bilags,
        },RequestContext(request))

def sisste_bilag(request, num):
    if num:
        num = int(num)
    else:
        num = 1
    bilags = list(Bilag.objects.all().order_by('-id')[:num])
    bilag_ids = [b.id for b in bilags]
    if len(bilag_ids) == 1:
        bilag_ids.append(-1) ## no bilag has id=-1 but the in query needs two conditions to work
    related_kontos = list(Konto.objects.bilagRelated(bilag_ids=bilag_ids))
    return render_to_response( 'show/sisste_bilag.html',{
        'bilags': bilags,
        'related_kontos': related_kontos,
        'num_range': range(1, num + 5),
        },RequestContext(request))

def external_actor_list(request):
    extra = {}
    extra['bilag_count'] = "SELECT COUNT(*) FROM `%s` as `b` WHERE `b`.`external_actor_id` = `%s`.`id`" % (Bilag._meta.db_table, Exteral_Actor._meta.db_table)
    #extra['faktura_count_sql'] = "SELECT COUNT(*) FROM `%s` as `f` WHERE `f`.`external_actor_id` = `%s`.`id`" % (Faktura._meta.db_table, Exteral_Actor._meta.db_table)
    ext = Exteral_Actor.objects.all().extra(select= extra).order_by("name")
    return render_to_response( 'show/external_actor_list.html',{
        'external_actors' : ext,
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
        x.append(innslag.bilag.dato)
        sum += innslag.value
        y.append(sum)
    ax.plot_date(x, y, '-')
    if x: # if there is transactions on the konto in the period
        # fill the period from the end of the year with a red line
        ax.plot_date([x[-1],date(int(year),12,31)],[y[-1],y[-1]],"r")
        if x[0].day != 1 or x[0].month != 1:
            ax.plot_date([date(int(year),1,1),x[0]],[0,0],"r")
    else:
        ax.plot_date([date(int(year),1,1),date(int(year),12,31)],[0,0],"r")
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response

def konto_graph_bar(request, year, konto_id):
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
    for innslag in innslags:
        ax.plot_date([innslag.bilag.dato,innslag.bilag.dato],[0,innslag.value],'-b')
    else:
        ax.plot_date([date(int(year),1,1),date(int(year),12,31)],[0,0],"r")
    ax.xaxis.set_major_formatter(DateFormatter('%b'))
    fig.autofmt_xdate()
    canvas = FigureCanvas(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_png(response)
    return response
