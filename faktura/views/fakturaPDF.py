# -*- coding: utf-8 -*-
# project imports
from django_regnskap.faktura.models import *

# django imports
from django.http import HttpResponse


# library imports
from reportlab.pdfgen import canvas
from io import BytesIO

# Koordinater og fargekoder for giroblankett er basert på arbeid av Marius N. Nicolaysen

# in this file the variable c is always the canvas object

def draw_faktura_header(c, faktura, data):
    c.setFillColorRGB(0,0,0)
    c.setStrokeColorRGB(0,0,0)
    #Tabell info overskrifter
    h = 800
    w = 470
    c.setFont('Helvetica-Bold', 12)
    c.drawRightString(w, h, 'Fakturanr :')
    c.setFont('Helvetica', 12)
    c.drawString(w + 5, h, faktura.getNumber())
    headers = [
        ('Kundenr :',    str(data['kunde']['id'])),
        ('Fakturadato :',faktura.date.strftime('%d.%m.%Y')),
        ('Forfall :',    faktura.frist.strftime('%d.%m.%Y')),
        ('Org nr :',     data['template']['org_nr']),
        ('Tlf :',        data['template']['tlf']),
        ('Epost :',      data['template']['email']),
        ('Bank konto :', data['template']['bank_konto']),
        ('Bank :',       data['template']['bank_navn']),
    ]
    for head in headers:
        h -= 13
        c.setFont('Helvetica-Bold',10)
        c.drawRightString(w,h,head[0])
        c.setFont('Helvetica',10)
        c.drawString(w + 5, h, head[1])
    # avsender adresse
    c.setFont('Helvetica-Bold',11)
    h = 815
    c.drawString(20,h,data['template']['name'])
    c.setFont('Helvetica',10)
    for line in data['template']['adress'].splitlines():
        h -= 12
        c.drawString(20,h,line)
    #Mottaker adresse
    c.setFont('Helvetica-Bold',12)
    h = 750
    w = 50
    c.drawString(w,h,data['kunde']['name'])
    c.setFont('Helvetica',12)
    for line in data['kunde']['adress'].splitlines():
        h -= 15
        c.drawString(w,h,line)
    h -= 15
    c.drawString(w,h,data['kunde']['email'])

def draw_faktura_varer(c, faktura):
    #Overskrifter
    c.setFont('Helvetica-Bold',12)
    h = 630
    c.drawString(40,  h, 'Varenr.')
    c.drawString(100, h, 'Produkt')
    c.drawCentredString(363, h, 'Antall')
    c.drawRightString(450, h, 'Enh.pris')
    #c.drawString(460, h, 'Mva')
    c.drawRightString(560, h, 'Totalpris')
    h -=6
    c.line(20,h,578,h)
    c.setFont('Helvetica',12)
    for vare in faktura.fakturavare.all():
        h -= 15
        c.drawString(50,  h, str(vare.vare.id))
        c.setFont('Helvetica',11)
        c.drawString(100, h, vare.name)
        c.setFont('Helvetica',12)
        c.drawCentredString(363, h, str(vare.ammount))
        c.drawRightString(450, h, str(vare.price))
        #c.drawString(460, h, str(vare.getMva()))
        c.drawRightString(560, h, ("%10.2f" % vare.totalPrice()))
    h -= 6
    c.line(20,h,578,h)
    h -= 15
    c.setFont('Helvetica-Bold',12)
    c.drawString(100, h, 'Totalsum :')
    c.drawRightString(560, h, "%10.2f" % faktura.totalPrice())

def draw_giro_template(c, color=(1, 0.9, 0.2)):
    """Tegn opp en giro mal (slik at du slipper å skrive ut på giropapir)"""
    #Kvitteringsstriper
    c.setFillColorRGB(  *color)
    c.setStrokeColorRGB(*color)
    c.rect(20,286,558,54, fill=1); #Øvre gule felt
    c.rect(20, 90,558,20, fill=1); #Konto-felt
    c.rect(20, 40,558, 5, fill=1); #Konto-felt

    #Hvite tekstfelt
    c.setFillColorRGB(  1, 1, 1)
    c.setStrokeColorRGB(1, 1, 1)
    c.rect(240,293, 80,18, fill=1) #Hvit Beløpsrute
    c.rect(375,293,110,18, fill=1) #Hvit kontonummer
    c.rect(540,93,11,14, fill=1)   #Kryss av for kvitering
    for i in range(11):
        c.rect(125+i*16.8,93,11,14, fill=1) #ruter for kontonummer

    #Diverse småtekst
    c.setFillColorRGB(0,0,0)
    c.setStrokeColorRGB(0,0,0)
    
    c.setFont('Helvetica-Bold',11)
    c.drawString(45,327,"Kvittering")
    
    c.setFont('Helvetica',7)
    c.drawString(45,315,"Innbetalt til konto")
    c.drawString(250,315,u"Beløp")
    c.drawString(380,315,'Betalers kontonummer')
    c.drawString(45,275,'Betalingsinformasjon')
    c.drawString(445,270,'Betalings-')
    c.drawString(445,263,'frist')
    c.drawString(45,185,'Betalt av')
    c.drawString(335,185,'Betalt til')
    c.drawString(100,101,'Belast')
    c.drawString(100, 94,'konto')
    c.drawString(500,101,'Kvittering')
    c.drawString(500, 94,'tilbake')
    c.drawString(45,77,'Kundeidentifikasjon')
    c.drawString(230,77,'Kroner')
    c.drawString(310,77,'Øre')
    c.drawString(370,77,'Til konto')

def draw_giro_content(c, faktura, data):
    c.setFillColorRGB(0,0,0)
    c.setStrokeColorRGB(0,0,0)
    c.setFont('Helvetica',12)
    #Betal til konto
    c.drawString(45,300,data['template']['bank_konto'])
    c.drawString(370,58,data['template']['bank_konto'])
    #Betalingsinnformasjon
    c.drawString(45,250, 'Faktura ' + str(faktura.getNumber()))
    c.drawString(45,236, 'Kundenr ' + str(faktura.kunde.id))
    #Forfall
    c.drawString(485,265,faktura.frist.strftime('%d.%m.%Y'))
    #Betalt av
    c.setFont('Helvetica-Bold',10)
    pos = 170
    c.drawString(45,pos,data['kunde']['name'])
    c.setFont('Helvetica',10)
    for line in data['kunde']['adress'].splitlines():
        pos -= 13
        c.drawString(45,pos,line)
    if pos > 136:
        pos -= 13
        c.drawString(45,pos,data['kunde']['email'])
    #Betalt til
    c.setFont('Helvetica-Bold',10)
    pos = 170
    c.drawString(335,pos,data['template']['name'])
    c.setFont('Helvetica',10)
    for line in data['template']['adress'].splitlines():
        pos -= 13
        c.drawString(335,pos,line)

    c.setFont('Helvetica',12)
    #beløp
    price = u"%10.2f" % faktura.totalPrice()
    c.drawCentredString(276,298,price)
    c.drawString(240,58, price.split('.')[0]) #kroner
    c.drawString(310,58, price.split('.')[1]) #øre
    
def generate_faktura_pdf(faktura):
    """This is one way of connecting the drawing functions"""
    buffer = BytesIO()
    # Create the PDF object, using the response object as its "file."
    c = canvas.Canvas(buffer)
    
    c.setAuthor("Django_regnskap")
    c.setTitle("Faktura %s"%faktura.getNumber())
    c.setFont("Helvetica", 12)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    
    if faktura.status == 0: #Kladdet
        data = faktura.get_data_for_sending()
        c.saveState()
        c.rotate(45)
        c.setFillColorRGB(1,0,0)
        c.setFont('Courier-Bold',100)
        c.drawString(400,100,'KLADD')
        c.restoreState()
    else:
        data = faktura.data
    draw_giro_template(c)
    draw_giro_content(c,faktura,data)
    draw_faktura_header(c,faktura,data)
    draw_faktura_varer(c, faktura)
    # Close the PDF object cleanly, and we're done.
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_response(request, faktura):
    """This is the view function"""
    faktura = Faktura.objects.get(pk = faktura)
    
    pdf = generate_faktura_pdf(faktura)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=faktura%s.pdf' % faktura.getNumber()
    response.write(pdf)
    
    return response