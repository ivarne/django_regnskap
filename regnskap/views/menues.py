#local imports
from django_regnskap.regnskap.models import *

#django imports
from django.shortcuts import render_to_response
from django.template import RequestContext

#system imports

def frontpage(request):
    return render_to_response('menues/frontpage.html', {
        
    },RequestContext(request))