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
from datetime import date

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
    bilagYear = list(Bilag.objects.prosjekt(prosjekt).filter(dato__year = int(year)).order_by('dato','bilagsnummer').prefetch_related('external_actor').prefetch_related('innslag').prefetch_related('prosjekt').prefetch_related('innslag__konto'))
    
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


def get_innslag_dato(innslag):
    #return 31.desember for inngående balanse
    if innslag.bilag.bilagType == 1 and innslag.bilag.dato.day == 1 and innslag.bilag.dato.month == 1:
        return date(innslag.bilag.dato.year-1, 12, 31)
    return innslag.bilag.dato

def calculate_intrest(request, year, kontos, rate):
    year = int(year)
    rate = float(rate) / 100
    innslags = list(Innslag.objects.filter(konto__in = kontos.split(',')).filter(bilag__dato__year = int(year)).order_by('bilag__dato', '-bilag__bilagType').select_related('bilag'))
    
    prev = innslags[0]
    saldo = prev.value
    rentesaldo = [float(0)] # mutable type can be changed inside intrest_period
    # calculation of leap years from 1901 to 2199
    days_in_year = 365 + (year % 4 == 0) - (year == 2100)
    
    def intrest_period(start, end):
        days = (end - start).days
        intrest = rate * float(saldo) * float(days) / float(days_in_year)
        rentesaldo[0] += intrest
        return {
            "start": start,
            "end" : end,
            "days": days,
            "days_in_year" : days_in_year,
            "intrest" : intrest,
            "saldo" : saldo,
            "rentesaldo": rentesaldo[0],
        }
    
    rows = [prev]
    for innslag in innslags[1:]:
        p_dato = get_innslag_dato(prev)
        i_dato = get_innslag_dato(innslag)
        if p_dato != i_dato:
            rows.append(intrest_period(p_dato, i_dato))
        saldo += innslag.value
        rows.append(innslag)
        prev = innslag
        
    return render_to_response( 'report/calculate_intrest.html',{
        'kontos': Konto.objects.filter(id__in = kontos.split(',')).select_related('prosjekt'),
        'rows': rows,
        "rate" : rate*100,
    },RequestContext(request))

def konto_external_actor_imbalance(request, konto):
    konto = Konto.objects.get(pk = int(konto))
    external_actors = Exteral_Actor.objects.raw("""SELECT * FROM (SELECT SUM(`i`.`belop` * i.`type` ) - SUM(`i`.`belop` * (1 -`i`.`type`) ) AS `imbalance`, e.* FROM regnskap_bilag AS b INNER JOIN regnskap_innslag AS i ON i.bilag_id = b.id INNER JOIN regnskap_exteral_actor AS e ON e.id = b.`external_actor_id` WHERE i.konto_id = %d GROUP BY e.id ) AS subtalbe WHERE imbalance <> 0""" % int(konto.pk))
    return render_to_response( 'report/external_actor_imbalance.html',{
        'konto': konto,
        'external_actors': external_actors,
    },RequestContext(request))