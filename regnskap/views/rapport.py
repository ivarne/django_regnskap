# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *
from django_regnskap.regnskap.lib.table_helper import TableCell, TableRow, Table
from django_regnskap.regnskap.lib.norskStandard import balanse, resultat

from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.conf import settings
from django.db import connection

from decimal import *

def offisielltRegnskap(request, prosjekt, year):
    year = int(year)
    years = range(max(settings.REGNSKAP_FIRST_YEAR, year-2),year+1) # show the last three valid years
    table = Table()
    # set row headers
    table.append_cell(TableCell(u""))
    for overskrift, b in balanse:
        table.append_cell(TableCell(overskrift, head = True))
        for hovedgruppe, h in b:
            table.append_cell(TableCell(hovedgruppe, bold = True))
            for undergruppe, u in h:
                table.append_cell(TableCell(undergruppe, italics = True))
                for kategori, key in u:
                    table.append_cell(TableCell(kategori))
                table.append_cell(TableCell(u"Sum %s" % undergruppe, italics = True))
            table.append_cell(TableCell(u"Sum %s" % hovedgruppe, bold = True))
        table.append_cell(TableCell(u"SUM %s" % overskrift, bold = True))
    
    for year in years:
        kontos = iter(Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (int(year),)).filter(kontoType__in = (1,2)).order_by('nummer'))
        konto = kontos.next()
        table.reset()
        table.append_cell(TableCell(unicode(year), head = True))
        for overskrift, b in balanse:
            osum = Decimal(0)
            table.append_cell(TableCell(u""))
            for hovedgruppe, h in b:
                hsum = Decimal(0)
                table.append_cell(TableCell(u""))
                for undergruppe, u in h:
                    gsum = Decimal(0)
                    table.append_cell(TableCell(u""))
                    for kategori, key in u:
                        ksum = Decimal(0)
                        while str(konto.nummer).startswith(key):
                            if str(konto.nummer).startswith('1'):
                                ksum += konto.getLoadedDebit()
                            else:
                                ksum += konto.getLoadedKredit()
                            try:
                                konto = kontos.next()
                            except StopIteration:
                                konto = Konto(nummer = '0000')
                        table.append_cell(TableCell(unicode(ksum), cssclass='tableNumber'))
                        gsum += ksum
                    table.append_cell(TableCell( unicode(gsum), cssclass='tableNumber', italics = True))
                    hsum += gsum
                table.append_cell(TableCell(unicode(hsum), cssclass='tableNumber', bold = True))
                osum += hsum
            table.append_cell(TableCell(unicode(osum), cssclass='tableNumber', bold = True))
    return render_to_response( 'report/aarsregnskap.html',{
        'safecontent' : table.render(),#the table does not contain user generated content
        'year'    : year,
        'prosjekt': prosjekt,
        },RequestContext(request))



def showYear(request, prosjekt, year):
    bilagYear = list(Bilag.objects.prosjekt(prosjekt).filter(dato__year = int(year)).order_by('dato','bilagsnummer').select_related('external_actor'))
    
    kostKonto= list(Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (int(year),)).filter(kontoType__in = (4,5,6,7,8,9)))
    totalKost = Decimal(0);
    for k in kostKonto:
        totalKost += k.getLoadedDebit()
    intKonto = list(Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (int(year),)).filter(kontoType = 3 ))
    totalInt = Decimal(0);
    for i in intKonto:
        totalInt += i.getLoadedKredit()
    # adjust the lists so that they get equal length
    l = max(intKonto, kostKonto, key=len)
    s = min(intKonto, kostKonto, key=len)
    s.extend(None for asdf in range(len(l) - len(s)))
    resultat = zip(kostKonto, intKonto)
    
    eiendelKonto =list(Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (int(year),)).filter(kontoType = 1))
    totalEie = Decimal(0);
    for e in eiendelKonto:
        totalEie += e.getLoadedDebit()
    finansKonto = list(Konto.objects.sum_columns(prosjekt = prosjekt, when_arg = (int(year),)).filter(kontoType__in = (2,9)))
    totalFinans = Decimal(0);
    for e in finansKonto:
        totalFinans += e.getLoadedKredit()
    # adjust the lists so that they get equal length
    l = max(eiendelKonto, finansKonto, key=len)
    s = min(eiendelKonto, finansKonto, key=len)
    s.extend(None for _ in range(len(l) - len(s)))
    balanse = zip(eiendelKonto, finansKonto)

    # Check if outgoing balance has been queried
    ubalanse_bal = False
    if prosjekt:
        cursor = connection.cursor()
        p_id = Prosjekt.objects.get(navn=prosjekt).id
        cursor.execute( """SELECT 
            SUM(type*belop) - sum((1-type)*belop) = 0 AS bal_inner,
            k.nummer
            FROM regnskap_innslag as i
            INNER JOIN regnskap_bilag AS b ON b.id = i.bilag_id
            INNER JOIN regnskap_konto AS k ON k.id = i.konto_id
            WHERE k.kontoType IN (1, 2) AND YEAR(b.dato) = %s AND b.prosjekt_id = %s
            GROUP BY k.id
        """, [int(year), p_id])
        for row in cursor.fetchall():
            bal_inner, k_nummer = row
            if not bal_inner:
                 ubalanse_bal = True

    ret = render_to_response('report/showYear.html', {
        'year'       : year,
        'bilagYear'  : bilagYear,
        'overskrift' : u"Årsoversikt %s" % year,
        'prosjekt'   : prosjekt,
        
        'resultat'     : resultat,
        'balanse'      : balanse,
        'totalKost'    : totalKost,
        'totalInt'     : totalInt,
        'totalEie'     : totalEie,
        'totalFinans'  : totalFinans,
        'ubalanse_res' : totalInt - totalKost,
        'ubalanse_bal' : ubalanse_bal,
    },RequestContext(request))
    return ret
