# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *


from django.template import RequestContext
from django.shortcuts import render_to_response, render

from decimal import *


def showYear(request, prosjekt, year):
    bilagYear = Bilag.objects.prosjekt(prosjekt).filter(dato__year = int(year)).order_by('dato')
    
    kostKonto= list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType__in = (4,5,6,7,8,9)))
    totalKost = Decimal(0);
    for k in kostKonto:
        totalKost += k.getLoadedDebit()
    intKonto = list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType = 3 ))
    totalInt = Decimal(0);
    for i in intKonto:
        totalInt += i.getLoadedKredit()
    # adjust the lists so that they get equal lenght
    l = max(intKonto, kostKonto, key=len)
    s = min(intKonto, kostKonto, key=len)
    s.extend(None for asdf in range(len(l) - len(s)))
    resultat = zip(kostKonto, intKonto)
    
    eiendelKonto =list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType = 1))
    totalEie = Decimal(0);
    for e in eiendelKonto:
        totalEie += e.getLoadedDebit()
    finansKonto = list(Konto.objects.sum_columns(prosjekt, int(year)).filter(kontoType__in = (2,9)))
    totalFinans = Decimal(0);
    for e in finansKonto:
        totalFinans += e.getLoadedKredit()
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
        'totalKost'    : totalKost,
        'totalInt'     : totalInt,
        'totalEie'     : totalEie,
        'totalFinans'  : totalFinans,
    },RequestContext(request))