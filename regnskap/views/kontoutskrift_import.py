# -*- coding: utf-8 -*-
from django_regnskap.regnskap.models import *
from django_regnskap.regnskap.forms import *

from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.conf import settings

from decimal import *
from datetime import date
import json

# Helper function for 
def kontoutskrift_import(request, project):
    project = Prosjekt.objects.get(navn = project)
    if request.method == 'POST':
        metadata_form = BilagKontoutskriftForm(request.POST, prefix="metadata")
        row_formset = BilagKontoutskriftRowFormset(request.POST, prefix="rows")
        if metadata_form.is_valid() and row_formset.is_valid():
            konto = metadata_form.cleaned_data["konto"]
            for row in row_formset.cleaned_data:
                if not row["DELETE"]:
                    bilag_draft = BilagDraft(
                        dato = row["date"],
                        beskrivelse = row["text"],
                        prosjekt = project,
                        belop = row['ammount'],
                        konto = konto,
                    )
                    bilag_draft.save()
                    
            return HttpResponseRedirect("/")
    else:
        metadata_form = BilagKontoutskriftForm(prefix="metadata")
        row_formset = BilagKontoutskriftRowFormset(prefix="rows")
    return render_to_response('bilag/kontoutskrift_import.html', {
        'metadata_form': metadata_form,
        'row_formset': row_formset,
        'prosjekt': project,
    },RequestContext(request))

def show_drafts(request, project):
    project = Prosjekt.objects.get(navn = project)
    drafts = BilagDraft.objects.filter(prosjekt = project).order_by("konto","-dato")
    return render_to_response('bilag/show_drafts.html', {
        'project': project,
        'drafts': drafts,
    },RequestContext(request))
