# -*- coding: utf-8 -*-
from models import *

from django import forms
from django.conf import settings
from django.template.defaultfilters import slugify as django_slugify

from decimal import *
import os
import string
import random


class BilagForm(forms.ModelForm):
    class Meta:
        model = Bilag
        exclude = ('prosjekt',)

class External_ActorForm(forms.ModelForm):
    class Meta:
        model = Exteral_Actor
        widgets = {
            'adress': forms.Textarea(attrs={'cols': 20, 'rows': 4}),
        }
        exclude = ('prosjekt',)
        
    def __init__(self,data = None, *args,**kwargs):
        # find the instance to be edited
        if not kwargs.get('instance'):
            try:
                if "prefix" in kwargs:
                    key = data[u"%s-%s" % (kwargs['prefix'], u"id")]
                else:
                    key = data["id"]
                kwargs['instance'] = Exteral_Actor.objects.get(pk = key)
            except:
                pass
        # Call parent constructor
        super(External_ActorForm,self).__init__(data,*args, **kwargs)
        
        #shuffle Id to the first place
        self.fields.insert(0,'id',self.fields.pop('id'))
    id = forms.IntegerField(
        min_value = 0,
        widget = forms.TextInput({u'placeholder':u'Søk Her (eller legg til)'}),
        required=False
    )

class BaseInnslagForm(forms.Form):
#    kontos = None #Set kontos with choices in innslag_form_factory
    debit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
        widget=forms.TextInput(attrs={'size':'10'}),
        required=False, # one of debit/kredit required(not both)
    )
    kredit = forms.DecimalField(
        min_value = 0,
        max_value = 10000000, # Ti milioner
        decimal_places = 2,
        widget=forms.TextInput(attrs={'size':'10'}),
        required=False, # one of debit/kredit required(not both)
    )
    #form fields gets added by the inslag_form_factory
    #Validation:
    def clean(self):
        cleaned_data = super(BaseInnslagForm, self).clean()
        ##Maks en verdi i kredit og debit
        debit = cleaned_data.get("debit")
        kredit = cleaned_data.get("kredit")
        if debit and kredit:
            #Begge feltene er gyldige formateringsmessig - la oss sjekke at maks ett er satt
            if debit!=None and kredit !=None:
                msg = u"Enten debit eller kredit kan inneholde verdi."
                self._errors["debit"] = self.error_class([msg])
                self._errors["kredit"] = self.error_class([msg])
                del cleaned_data["kredit"]
                del cleaned_data["debit"]
        return cleaned_data

def innslag_form_factory(prosjekt):
    kontos = forms.TypedChoiceField(
        coerce = lambda id: Konto.objects.get(id=id),
        choices = Konto.objects.toOptionGroups(prosjekt),
        empty_value = None,
        widget = forms.Select(attrs={'tabindex':'-1'})
    )
    return type(str(prosjekt) + "InnslagForm", (BaseInnslagForm,), {
        'kontos' : kontos,
    })

class BaseInnslagFormSet(forms.formsets.BaseFormSet):
    
    def clean(self):
        """Checks that no two articles have the same title."""
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        debit = Decimal(0) # datatype with exact decimal fractions
        kredit = Decimal(0)
        i = 0
        for form in self.forms:
            if form.cleaned_data:
                i+=1
                debit += form.cleaned_data['debit'] or 0
                kredit += form.cleaned_data['kredit'] or 0
        if i == 0:
            raise forms.ValidationError(u"Det må være minst to innslag på et bilag")
        if debit != kredit:
            raise forms.ValidationError(u"Kredit og debit må summere til samme tall")

        
class BilagFileForm(forms.Form):
    currentUpload = forms.FileField(required =False)
    previousUploads = forms.MultipleChoiceField(required =False, widget= forms.CheckboxSelectMultiple())
    def __init__(self, *args, **kwargs):
        super(BilagFileForm,self).__init__(*args, **kwargs)
        files = []
        for file in os.listdir(os.path.join(settings.MEDIA_ROOT, 'upload')):
            files.append((file, file.rsplit('_',1)[1]))
        self.fields['previousUploads'].choices = files
    def save(self,bilag):
        if not self.is_valid():# ignore files if validation fails
            raise Exception("Ugyldig form")
        for f in self._saveFiles(bilag):
            b = BilagFile(bilag = bilag, file = f)
            b.save()
    def _saveFiles(self, bilag):
        def prepareSave(fname):
            newname = os.path.join(str(bilag.dato.year),u"%d-%s" % (bilag.bilagsnummer, fname.encode("ascii","ignore")))
            f = os.path.join(settings.MEDIA_ROOT,newname)
            return (newname, open(f,'wb+'))
        fnames = []
        for file in self.cleaned_data['previousUploads']:
            file = os.path.join(settings.MEDIA_ROOT, "upload", file)
            if os.path.exists(file):
                hash, name = file.split("_",1) #split temorary uplodad filename
                newname = os.path.join(str(bilag.dato.year),"%d-%s" % (bilag.bilagsnummer, name))
                os.rename(file, os.path.join(settings.MEDIA_ROOT, newname))
                fnames.append(newname)
#                newname, newfile = prepareSave(dname)
#                fnames.append(newname)
#                f = client.get_file("upload/" + dname)
#                newfile.write(f.read())
#                f.close()
#                newfile.close()
#                client.file_delete("upload/" + dname)
        # save file from upload field
        if self.cleaned_data['currentUpload']:
            newname, newfile = prepareSave(self.cleaned_data['currentUpload'].name)
            fnames.append(newname)
            for chunk in self.cleaned_data['currentUpload'].chunks():
                newfile.write(chunk)
            newfile.close()
        return fnames
    @staticmethod
    def slugify(fileName):
        fname, ext = fileName.rsplit('.',1)
        return django_slugify(fname) + '.' + ext
    
    @classmethod
    def get_files_from_dropbox(cls, dropbox_client):
        """Utility function to download files from the users dropbox/upload folder and store them on the server"""
        files = dropbox_client.metadata('upload')['contents']
        ret = []
        for f in files:
            random_prefix = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(8))
            name = f['path'].rsplit("/",1)[1]
            fname = random_prefix + "_" + cls.slugify(name)
            tmp_file = open(os.path.join(settings.MEDIA_ROOT, 'upload', fname), "wb+")
            d_file = dropbox_client.get_file(f['path'])
            tmp_file.write(d_file.read())
            ret.append((fname, name))
            dropbox_client.file_delete(f['path'].encode("utf-8"))
        return ret

        
