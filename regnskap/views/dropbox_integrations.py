"""
django view methods to interact with the dropbox api
"""

from django_regnskap.regnskap.lib.export import ExelYearView

from dropbox import client, session
from oauth.oauth import OAuthToken

from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from django_regnskap.regnskap.models import UserProfile

from pprint import pprint

#helper functions
def getSession():
    keys = settings.DROPBOX_SETTINGS
    return session.DropboxSession(keys['app_key'], keys['app_secret'],'app_folder')

def getUserProfile(user):
    # ensure a valid profile
    try:
        profile = user.get_profile()
    except ObjectDoesNotExist:
        profile = UserProfile(user = user)
        #profile.save() save later
    return profile

@login_required
def connect(request):
    sess = getSession()
    userProfile = getUserProfile(request.user)
    dropbox_request_session_key = 'dropbox_request_token3'
    if not request.session.has_key(dropbox_request_session_key):
        request_token = sess.obtain_request_token()
        request.session[dropbox_request_session_key] = request_token
        url = sess.build_authorize_url(request_token,request.build_absolute_uri())
        return redirect(url)
    access_token = sess.obtain_access_token(request.session.pop(dropbox_request_session_key))
    userProfile.dropbox_token = access_token
    userProfile.save()
    return redirect('/regnskap/')

@login_required
def saveBackup(request, year):
    year = int(year)
    # import localy so that openpyxl is only required if needed.
    e = ExelYearView()
    e.generateYear(year)
    
    #connect with dropbox
    sess = getSession()
    up = getUserProfile(request.user)
    sess.token =  OAuthToken.from_string(up.dropbox_token)
    c = client.DropboxClient(sess)
    filename = "regnskap/%d-regnskap.xlsx"%year
    try:
        metadata = c.metadata(filename)['rev'];
    except Exception:
        metadata = None
    ret = c.put_file(filename,e.getExcelFileStream(),parent_rev=metadata)
    print ret
    return HttpResponse(str(ret))
    