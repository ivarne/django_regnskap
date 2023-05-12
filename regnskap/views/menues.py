#local imports
from django_regnskap.regnskap.models import *
from django_regnskap.faktura.models import Template

#django imports
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings
from django.db import connection

#system imports
from datetime import date

def frontpage(request):
    prosjekt = list(Prosjekt.objects.all().order_by('navn'))
    prosjekt_id = [p.id for p in prosjekt]
    years = {}

    cursor = connection.cursor()
    # legg inn resultat kontoer kontoType = 3,4,5,6,7,8
    cursor.execute( """SELECT
        YEAR(b.dato) as y,
        b.prosjekt_id AS p,
        SUM(type*belop)- sum((1-type)*belop) = 0 AS res_ok
    FROM regnskap_bilag AS b
        INNER JOIN regnskap_innslag AS i ON i.bilag_id = b.id
        INNER JOIN regnskap_konto AS k ON k.id = i.konto_id
    WHERE k.kontoType > 2
    GROUP BY y, p
    ORDER BY y, p
    """)
    for row in cursor.fetchall():
        if row[0] not in years:
            # If there is no bilag on a project for a year assume it is correct
            years[row[0]] = [[p.navn, True, True] for p in prosjekt]
        years[row[0]][prosjekt_id.index(row[1])][1] = bool(row[2])

    # legg inn balanse kontoer
    cursor.execute( """SELECT
        y_inner AS y,
        p_inner AS p,
        MIN(bal_inner) as bal_ok
    FROM
    (SELECT
        SUM(type*belop) - sum((1-type)*belop) = 0 AS bal_inner,
        YEAR(b.dato) as y_inner,
        b.prosjekt_id AS p_inner
        FROM regnskap_innslag as i
        INNER JOIN regnskap_bilag AS b ON b.id = i.bilag_id
        INNER JOIN regnskap_konto AS k ON k.id = i.konto_id
        WHERE k.kontoType IN (1, 2)
        GROUP BY k.id , y_inner, p_inner
    ) as asdfasdf
    GROUP BY y, p
    ORDER BY y, p
    """)
    for row in cursor.fetchall():
        y, p, bal_ok = row
        if y not in years:
            # If there is no bilag on a project for a year assume it is correct
            years[y] = [[pr.navn, True, True] for pr in prosjekt]
        years[y][prosjekt_id.index(p)][2] = bool(bal_ok)

    return render_to_response('menues/frontpage.html', {
        'years'    : reversed(sorted(years.items())),
        'prosjekt' : prosjekt,
        'faktura_templates': Template.objects.order_by('prosjekt').select_related('prosjekt').all(),
    },RequestContext(request))