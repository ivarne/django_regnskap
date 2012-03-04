from regnskap.models import *


from django.template import RequestContext
from django.shortcuts import render_to_response, render

def showYear(request,year):
    bilagYear = Bilag.objects.filter(dato__year = year).order_by('bilagsnummer')
    return render_to_response('showYear.html', {
        'year'     : year,
        'bilagYear'    : bilagYear,
    },RequestContext(request))