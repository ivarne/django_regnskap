# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *


from django.template import RequestContext
from django.shortcuts import render_to_response, render

def showYear(request, prosjekt, year):
    bilagYear = Bilag.objects.prosjekt(prosjekt).filter(dato__year = year).order_by('dato')
    
    kostKonto= list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType__in = (4,5,6,7,8,9)))
    intKonto = list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType = 3 ))
    # adjust the lists so that they get equal lenght
    l = max(intKonto, kostKonto, key=len)
    s = min(intKonto, kostKonto, key=len)
    s.extend(None for asdf in range(len(l) - len(s)))
    resultat = zip(kostKonto, intKonto)
    
    eiendelKonto =list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType = 1))
    finansKonto = list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType = 2))
    # adjust the lists so that they get equal lenght
    l = max(eiendelKonto, finansKonto, key=len)
    s = min(eiendelKonto, finansKonto, key=len)
    s.extend(None for _ in range(len(l) - len(s)))
    balanse = zip(eiendelKonto, finansKonto)
    
    return render_to_response('showYear.html', {
        'year'       : year,
        'bilagYear'  : bilagYear,
        'overskrift' : u"Årsoversikt %s" % year,
        
        'resultat'     : resultat,
        'balanse'      : balanse,
    },RequestContext(request))