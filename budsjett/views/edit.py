# django imports
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse, Http404

# django_regnskap imports
from django_regnskap.budsjett.models import *


def edit(request):
    pass