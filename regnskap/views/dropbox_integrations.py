"""
django view methods to interact with the dropbox api
"""

from django_regnskap.regnskap.lib.export import ExelYearView

from django.http import HttpResponse
from django.conf import settings

from django_regnskap.django_dropbox.decorator import dropbox_user_required

import os

@dropbox_user_required
def saveBackup(request, year, dropbox_client):
    year = int(year)
    # Store bilag files
    db_folder = "/regnskap/%d"%year
    try:
        files = dropbox_client.metadata(db_folder)['contents']
    except Exception as e:
        if e.status == 404:
            dropbox_client.file_create_folder(db_folder)
            files = dropbox_client.metadata(db_folder)['contents']
        else:
            return HttpResponse(str(e),status=e.status)
    files = [f["path"].lower() for f in files]
    server_folder = os.path.join(settings.MEDIA_ROOT,str(year))
#    ret = [files]
    for f in os.listdir(server_folder):
        path = db_folder+"/"+f
        if path.lower() not in files:
            with open(os.path.join(server_folder,f)) as handle:
#                ret.append(path)
                dropbox_client.put_file(db_folder + "/" + f, handle)
    
    # update the full excel export of the accounting year
    e = ExelYearView(year)
    
    filename = "regnskap/%d-regnskap.xlsx"%year
    try:
        metadata = dropbox_client.metadata(filename)['rev'];
    except Exception:
        metadata = None
    ret = dropbox_client.put_file(filename,e.getExcelFileStream(),parent_rev=metadata)
    # update database dump
    filename = "regnskap/database_dump.sql"
    try:
        metadata = dropbox_client.metadata(filename)['rev'];
    except Exception:
        metadata = None
    with open(os.path.join(settings.MEDIA_ROOT,"database_dump.sql")) as file:
        dropbox_client.put_file(filename,file,parent_rev=metadata)

    return HttpResponse(str(ret))

@dropbox_user_required
def test(request,dropbox_client):
    ret = dropbox_client.metadata('upload')['contents']
    return HttpResponse(str(ret))
