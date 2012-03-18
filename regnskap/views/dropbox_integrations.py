"""
django view methods to interact with the dropbox api
"""

from django_regnskap.regnskap.lib.export import ExelYearView

from django.http import HttpResponse

from django_dropbox.decorator import dropbox_user_required


@dropbox_user_required
def saveBackup(request, year, dropbox_client):
    year = int(year)
    # import localy so that openpyxl is only required if needed.
    
    e = open('regnskap/views/bilag.py')
    filename = "bilag.py"
    try:
        metadata = dropbox_client.metadata(filename)['rev'];
    except Exception:
        metadata = None
    ret = dropbox_client.put_file(filename,e ,parent_rev=metadata)
    print ret
    return HttpResponse(str(ret))

@dropbox_user_required
def test(request,dropbox_client):
    ret = dropbox_client.metadata('upload')['contents']
    for f in ret:
        print dropbox_client.media(f['path'])
    print ret
    return HttpResponse(str(ret))