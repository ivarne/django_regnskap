# -*- coding: utf-8 -*-

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


def konto_graph_multiyear(request, konto_id):
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    # Collect data
    konto = Konto.objects.get(pk = konto_id)
    innslags = konto.innslag.order_by('bilag__dato')
    years = konto.innslag.order_by()
    # make plot
    fig=Figure()
    fig.suptitle( unicode(konto))
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