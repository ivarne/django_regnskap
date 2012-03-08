from django_regnskap.regnskap.lib.export import ExelYearView
from django.http import HttpResponse

def export(request, year):
    year = int(year)
    # import localy so that openpyxl is only required if needed.
    e = ExelYearView()
    e.generateYear(year)
    response = HttpResponse(mimetype='application/vnd.ms-excel')
    response['Content-Disposition'] = "attachment; filename=regnskap%d.xlsx" % year
    response.write(e.getExcelFileStream())
    return response
    
