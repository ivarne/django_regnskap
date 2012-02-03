# Create your views here.
## standard includes
import os
## my files import
from regnskap import models
## django import
from django.shortcuts import render_to_response


def default(request):
    bilag_list = models.Bilag.objects.all()
    return render_to_response('default.html',{'bilag_list': bilag_list})

def registerform(request):
    konto_plan = models.Konto.objects.all()
    files = os.listdir(os.path.join('/','var','www','django_regnskap'))
    return render_to_response('form.html',{'files': files})
    
def registerAction(request):
    pass
