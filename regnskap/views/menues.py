#local imports
from django_regnskap.regnskap.models import *
from django_regnskap.faktura.models import Template

#django imports
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

#system imports
from datetime import date

def frontpage(request):
    return render_to_response('menues/frontpage.html', {
        'years'    : range(date.today().year, settings.REGNSKAP_FIRST_YEAR -1, -1),
        'prosjekt' : Prosjekt.objects.all(),
        'faktura_templates': Template.objects.order_by('prosjekt').select_related('prosjekt').all(),
    },RequestContext(request))