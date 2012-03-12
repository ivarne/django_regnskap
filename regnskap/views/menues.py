#local imports
from django_regnskap.regnskap.models import *

#django imports
from django.shortcuts import render_to_response
from django.template import RequestContext

#system imports
from datetime import date

def frontpage(request):
    return render_to_response('menues/frontpage.html', {
        'years'    : range(date.today().year, 2011 -1, -1),
        'prosjekt' : Prosjekt.objects.all(),
    },RequestContext(request))