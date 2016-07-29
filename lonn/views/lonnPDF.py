# -*- coding: utf-8 -*-
# project imports
from django_regnskap.lonn.models import *

# django imports
from django.http import HttpResponse


# library imports
from reportlab.pdfgen import canvas
from io import BytesIO

import locale
locale.setlocale(locale.LC_ALL, '')


# in this file the variable c is always the canvas object

def draw_table(c, rows, colXs, startY, deltaY=13, colAligns=[]):
    """Draws rows to canvas at (colXs,startY-n*deltaY), alligned by colAligns(l/r/c for each col) or left"""
    y = startY
    for row in rows:
        for (i, cell) in enumerate(row):
            cAlign = colAligns[i] if (len(colAligns)>i) else 'l'
            if cAlign == 'l':
                c.drawString(colXs[i], y, cell)
            elif cAlign == 'c':
                c.drawCentredString(colXs[i], y, cell)
            elif cAlign == 'r':
                c.drawRightString(colXs[i], y, cell)
            else:
                raise InputError("drawTable", "colAligns contains invalid values, accepted are 'l', 'r' and 'c' ")
        y -= deltaY


def draw_periode_header(c, periode):
    #Selskapinfo
    c.setFont('Helvetica-Bold', 12)
    c.drawString(35, 799, periode.selskap.navn)
    
    c.setFont('Helvetica-Bold', 11)
    c.drawString(400,  800, 'Dato:')
    c.drawString(400,  786, 'Periode:')
    
    c.setFont('Helvetica', 11)
    c.drawString(450, 800, periode.dato.strftime('%d.%m.%Y'))
    c.drawString(450, 786, periode.navn)
    c.drawString(35,  786, periode.selskap.orgnr)


def get_aggregated_kontos(periode):
    kontos = {}
    
    def setOrAdd(konto, value):
        if konto.nummer in kontos:
            kontos[konto.nummer][1] += value
        else:
            kontos[konto.nummer] = [konto,value]

    for pArt in periode.arts:
        setOrAdd(pArt.lonnArt.konto_fra, -pArt.sum)
        setOrAdd(pArt.lonnArt.konto_til,  pArt.sum)
        
        if pArt.lonnArt.konto_aga is not None:
            from decimal import Decimal
            mul_aga = Decimal(0.141) # periode.selskap.aga_sats/100
            setOrAdd(pArt.lonnArt.konto_aga,     -pArt.sum * mul_aga)
            setOrAdd(pArt.lonnArt.konto_aga_til,  pArt.sum * mul_aga)

    return map( lambda a:kontos[a], sorted(kontos))
        

def get_aggregated_arts(periode):
    arts = {}
    for pArt in periode.arts:
        if pArt.lonnArt.nummer in arts:
            arts[pArt.lonnArt.nummer][2] += 1
            arts[pArt.lonnArt.nummer][3] += pArt.sum
        else:
            arts[pArt.lonnArt.nummer] = [pArt.lonnArt.nummer, pArt.lonnArt.tekst, 1, pArt.sum]
                
    return sorted(arts.values())



def draw_journal(c, periode):
    """Tar inn et canvas og et LonnPeriode og skriver Lønnjournal på Canvas"""
    c.setFillColorRGB(0,0,0)
    c.setStrokeColorRGB(0,0,0)
    
    # Header
    draw_periode_header(c, periode)

    # Lønnsarter
    c.setFont('Helvetica-Bold', 14)
    c.drawString(35, 700, 'Lønnsjournal')
    
    c.setFont('Helvetica-Bold', 11)
    c.drawString(35,  680, 'Lønnsart')
    c.drawString(250, 680, 'Ant')
    c.drawString(300, 680, 'Totalsum')
    

    artRows = []
    for artRow in get_aggregated_arts(periode):
        artRows.append([str(artRow[0]), artRow[1], str(artRow[2]), "{0:,.2f}".format(artRow[3])])
    '''            """
    artRows.append([])

    artRows.append(['','Totalt utbetalt',    '',"{0:,.2f}".format(utbetalt)])
    artRows.append(['','Påløpte feriepenger','',"{0:,.2f}".format(feriepenger)])
    artRows.append(['','Skattetrekk'        ,'',"{0:,.2f}".format(skatt)])
    '''
    c.setFont('Helvetica', 11)
    draw_table(c, artRows, [35, 62, 265, 350], 665, 13, ('l','l','r','r'))
    

    # Lønnsarter
    c.setFont('Helvetica-Bold', 14)
    c.drawString(35, 450, 'Konteringsbilag')
    
    c.setFont('Helvetica-Bold', 11)
    c.drawString(35,  430, 'Konto')
    c.drawString(315, 430, 'Debet')
    c.drawString(400, 430, 'Kredit')
    
    c.setFont('Helvetica', 11)

    sums = [0,0]
    ktoRows = []
    for (konto, sum) in get_aggregated_kontos(periode):
        sums[0 if sum<=0 else 1] += sum
        debet  = "{0:,.2f}".format(-sum) if sum <= 0 else ''
        kredit = "{0:,.2f}".format(sum)  if sum >  0 else ''
        ktoRows.append([str(konto.nummer), konto.navn, debet, kredit])
    ktoRows.append([])
    ktoRows.append(['', 'Sum', "{0:,.2f}".format(-sums[0]), "{0:,.2f}".format(sums[1])])
    draw_table(c, ktoRows, [35, 68, 365, 450], 412, 13, ('l','l','r','r'))



def draw_slip(c, data):
    """Tar inn et canvas og et LonnAnsattPeriode og skriver Lønnslipp på Canvas"""
    c.setFillColorRGB(0,0,0)
    c.setStrokeColorRGB(0,0,0)
    
    #Mottakerinfo
    skattekort = data.ansatt.getSkattekort(data.periode.dato);
    mottakerAdresse = data.ansatt.adresse.splitlines()
    mottakerInfo = [
        ('Navn',data.ansatt.navn),
        ('Adresse',(mottakerAdresse[0] if len(mottakerAdresse)>0 else '')),
        ('',(mottakerAdresse[1] if len(mottakerAdresse)>1 else '')),
        ('',(mottakerAdresse[2] if len(mottakerAdresse)>2 else '')),
        ('Stilling',data.ansatt.stilling),
        ('Skattekommune',unicode(skattekort.skattekommune)),
        ('Trekkprosent',unicode(skattekort.prosent)),
        ('Fødselsnummer',data.ansatt.f_nr),
    ]
    
    c.setFont('Helvetica-Bold', 12)
    c.drawString(35, 800, 'Lønnsmottager')
    
    c.setFont('Helvetica', 10)
    draw_table(c, mottakerInfo, [35, 125], 785, 13)
    
    
    #Arbeidsgiverinfo og Periodeinfo
    selskapAdresse = data.periode.selskap.adresse.splitlines()
    selskapInfo = [
        ('Selskap',data.periode.selskap.navn),
        ('Adresse',(selskapAdresse[0] if len(selskapAdresse)>0 else '')),
        ('', (selskapAdresse[1] if len(selskapAdresse)>1 else '')),
        ('', (selskapAdresse[2] if len(selskapAdresse)>2 else '')),
        ('Org.nr',data.periode.selskap.orgnr),
        ('',''),
        ('Periode',data.periode.navn),
        ('Dato',data.periode.dato.strftime('%d.%m.%Y')),
    ]
    
    c.setFont('Helvetica-Bold', 12)
    c.drawString(340, 800, 'Arbeidsgiver')
    
    c.setFont('Helvetica', 10)
    draw_table(c, selskapInfo, [340, 400], 785, 13)
    
    
    
    #Headers
    h = 620
    c.setFont('Helvetica-Bold', 12)
    c.drawString(40,  h, 'Lønnsart')
    c.drawString(270, h, 'Hittil i år')
    c.drawString(400, h, 'Denne Periode')
    c.setFont('Helvetica-Bold', 7)
    c.drawString(206, h-15, 'FP')
    c.drawString(220, h-15, 'Skatt')
    c.setFont('Helvetica-Bold', 10)
    c.drawString(250, h-15, 'Antall')
    c.drawString(310, h-15, 'Beløp')
    c.drawString(380, h-15, 'Antall')
    c.drawString(440, h-15, 'á')
    c.drawString(500, h-15, 'Beløp')
    
    # Grid (A4 is 595x842 points)
    h += 12 #Top of box
    c.setLineWidth(0.01)
    c.line(32,h,563,h)
    c.line(32,h-30,563,h-30)
    c.line(32,32,563,32)
    dh = h-32
    c.line(32, h,    32, h-dh)
    c.line(240,h,    240,h-dh)
    c.line(368,h,    368,h-dh)
    c.line(563,h,    563,h-dh)
    c.setDash(3,2)
    c.line(68, h-30, 68, h-dh)
    c.line(298,h-18, 298,h-dh)
    c.line(428,h-18, 428,h-dh)
    c.line(488,h-18, 488,h-dh)
    
    utbetales = [0,0]
    skatt = [0,0]
    feriepenger = [0,0]
    feriepengegrunnlag = [0,0]
    
    rows = []
    for (i,art) in sorted(data.getYearToPerodeSlipArts().items()):
        if (art['lonnArt'].id == data.periode.selskap.art_feriepenger_id):
            feriepenger[0] += art['yearSum']
            feriepenger[1] += art['periodeSum']  if 'periodeSum' in art else 0
        elif ((art['lonnArt'].id == data.periode.selskap.art_skatt_prosent_id) or
                (art['lonnArt'].id == data.periode.selskap.art_skatt_ordinar_id)):
            skatt[0] -= art['yearSum']
            skatt[1] -= art['periodeSum'] if 'periodeSum' in art else 0
                
        if art['lonnArt'].visPaLonnSlipp:
            row = (
                unicode(art['lonnArt'].nummer),
                art['lonnArt'].tekst,
                u"\u2713" if art['lonnArt'].feriepengegrunnlag else '',
                art['lonnArt'].skattShort,
                '{0:,.2f}'.format(art['yearAntall']),
                '{0:,.2f}'.format(art['yearSum']),
                '{0:.2f}'.format(art['periodeAntall'])   if 'periodeAntall' in art else '',
                '{0:,.2f}'.format(art['periodeStkBelop']) if 'periodeStkBelop' in art else '',
                '{0:,.2f}'.format(art['periodeSum'])    if 'periodeSum' in art else ''
            )
            utbetales[0] += art['yearSum']
            utbetales[1] += art['periodeSum'] if 'periodeSum' in art else 0
            if art['lonnArt'].feriepengegrunnlag:
                feriepengegrunnlag[0] += art['yearSum']
                feriepengegrunnlag[1] += art['periodeSum'] if 'periodeSum' in art else 0
            rows.append(row)

    c.setFont('Helvetica', 11)
    colXs = [40, 75, 212, 229, 290, 360, 420, 480, 555]
    align = ['l','l','c', 'c', 'r', 'r', 'r', 'r', 'r']
    draw_table(c, rows, colXs, h-44, 14, align)

    h = 102
    c.drawString(75, h, 'Til Utbetaling:')
    c.drawRightString(360, h, "{0:,.2f}".format(utbetales[0]))
    c.drawRightString(550, h, "{0:,.2f}".format(utbetales[1]))

    h -= 30
    c.drawString(75, h, 'Feriepengegrunnlag:')
    c.drawRightString(360, h, "{0:,.2f}".format(feriepengegrunnlag[0]))
    c.drawRightString(550, h, "{0:,.2f}".format(feriepengegrunnlag[1]))

    h -= 16
    c.drawString(75, h, 'Opptjente feriepenger:')
    c.drawRightString(360, h, "{0:,.2f}".format(feriepenger[0]))
    c.drawRightString(550, h, "{0:,.2f}".format(feriepenger[1]))

    h -= 16
    c.drawString(75, h, 'Skattetrekk:')
    c.drawRightString(360, h, "{0:,.2f}".format(skatt[0]))
    c.drawRightString(550, h, "{0:,.2f}".format(skatt[1]))



    return

    #Footer - not yet implemented
    h=100


    c.setFont('Helvetica-Bold', 12)
    c.drawString(40,  h, 'Lønnsart')
    c.drawString(270, h, 'Hittil i år')
    c.drawString(400, h, 'Denne Periode')
    c.setFont('Helvetica-Bold', 7)
    c.drawString(206, h-15, 'FP')
    c.drawString(220, h-15, 'Skatt')
    c.setFont('Helvetica-Bold', 10)
    c.drawString(250, h-15, 'Antall')
    c.drawString(310, h-15, 'Beløp')
    c.drawString(380, h-15, 'Antall')
    c.drawString(440, h-15, 'á')
    c.drawString(500, h-15, 'Beløp')

    c.line(32,h,563,h)
    c.line(32,32,563,32)
    dh = 200
    c.line(32, h,    32, 32)
    c.line(68, h-30, 68, 32)
    c.line(240,h,    240,32)
    c.line(298,h-18, 298,32)
    c.line(368,h,    368,32)
    c.line(428,h-18, 428,32)
    c.line(488,h-18, 488,32)
    c.line(563,h,    563,32)


def draw_kladd(c):
    c.saveState()
    c.rotate(45)
    c.setFillColorRGB(1,0,0)
    c.setFont('Courier-Bold',100)
    c.drawString(400,100,'KLADD')
    c.restoreState()




def generate_slip_pdf(ansattPeriode):
    """Lager PDF med lønnslippen til den annsatte for perioden"""
    buffer = BytesIO()
    # Create the PDF object, using the response object as its "file."
    c = canvas.Canvas(buffer, encrypt=ansattPeriode.ansatt.f_nr)
    
    c.setAuthor("Django_regnskap")
    c.setTitle("Lonn %s"%ansattPeriode.periode.navn)
    c.setFont("Helvetica", 12)
    
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    
    if ansattPeriode.periode.finalized == False: #Kladdet
        draw_kladd(c)

    # Tegn lønnslipp for den ansatte
    draw_slip(c, ansattPeriode)

    # Close the PDF object cleanly, and we're done.
    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_periode_pdf(periode):
    """Lager PDF med løalle bilaf for perioden"""
    buffer = BytesIO()
    # Create the PDF object, using the response object as its "file."
    c = canvas.Canvas(buffer)
    
    c.setAuthor("Django_regnskap")
    c.setTitle("Lonn %s"%periode.navn)
    c.setFont("Helvetica", 12)
    
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    
    draw_journal(c, periode)
    if not periode.finalized:
        draw_kladd(c)
    c.showPage()
    
    # Tegn lønnslipp for den ansatte
    for ansattPeriode in periode.ansatte:
        draw_slip(c, ansattPeriode)
        if not periode.finalized:
            draw_kladd(c)
        c.showPage()
    
    # Close the PDF object cleanly, and we're done.
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def generate_slip_response(request, ansattPeriodeID):
    """This is the view function for single slips - maybe remove?"""
    ansattPeriode = LonnAnsattPeriode.objects.get(pk = ansattPeriodeID)
    
    pdf = generate_slip_pdf(ansattPeriode)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=lonn_%s.pdf' % ansattPeriode.periode.navn
    response.write(pdf)
    
    return response





def generate_periode_response(request, periodeID):
    """This is the view function"""
    periode = LonnPeriode.objects.get(pk = periodeID)
    
    pdf = generate_periode_pdf(periode)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=lonn_%s.pdf' % periode.navn
    response.write(pdf)
    
    return response
