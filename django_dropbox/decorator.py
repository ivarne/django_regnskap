"""
django view methods to interact with the dropbox api
"""


from dropbox import client, session
from dropbox.rest import ErrorResponse
from oauth.oauth import OAuthToken

from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse

from models import DropboxExtra


DROPBOX_REQUEST_SESSION_KEY = 'dropbox_request_token3' # random temp storage name

def _saveUserToken(user, token):
    try:
        d = user.django_dropbox
    except:
        d = DropboxExtra()
        d.user = user
    d.dropbox_token = token
    d.save()

def _dropboxConnect(request,sess):
    request_token = sess.obtain_request_token()
    request.session[DROPBOX_REQUEST_SESSION_KEY] = request_token
    url = sess.build_authorize_url(request_token,request.build_absolute_uri())
    return HttpResponseRedirect(url)


def dropbox_user_required(funk):
    @login_required
    def _dropbox_wrap(request, *args, **kwargs):
        _keys = settings.DROPBOX_SETTINGS
        sess = session.DropboxSession(_keys['app_key'], _keys['app_secret'],_keys['type'])
        try:
            if request.session.has_key(DROPBOX_REQUEST_SESSION_KEY):
                token = sess.obtain_access_token(request.session.pop(DROPBOX_REQUEST_SESSION_KEY))
                _saveUserToken( request.user, token )
            else:
                token = request.user.django_dropbox.dropbox_token
            sess.token =  OAuthToken.from_string(token)
            c = client.DropboxClient(sess)
        except ObjectDoesNotExist:
            return _dropboxConnect(request, sess)
        try:
            return funk(request, *args, dropbox_client=c, **kwargs)
        except ErrorResponse, e:
            if e.status == 401:
                _dropboxConnect(request, sess)# re authentication needed
            else:
                raise e # let django log the exception that the usier did not handle

    return _dropbox_wrap
    