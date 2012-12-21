# django imports
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import Q

# django_regnskap imports
from django_regnskap.budsjett.models import *

import datetime

def list(request, prosjekt, year):
    year = int(year)
    budsjetts = Budsjett.objects.all() \
        .filter(Q(fra__year = year) | Q(til__year = year)) \
        .filter(prosjekt__navn = prosjekt) \
        .order_by('fra','id')
    return render_to_response('list_budsjett.html', {
        'prosjekt'           : prosjekt,
        'budsjett_list'      : budsjetts,
    },RequestContext(request))
    
def show(request, id):
    return render_to_response('show_budsjett.html', {
        'now'           : datetime.date.today(),
        'budsjett'      : Budsjett.objects.get(pk = int(id)),
    },RequestContext(request))