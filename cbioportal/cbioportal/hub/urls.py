import logging

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import login as login_view
from django.conf.urls import url, include
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponseRedirect
from datetime import datetime
from django.contrib import messages

from cbioportal.hub.forms import authenticationForm
from cbioportal.hub.views import passwordresetForm, passwordtokenForm, passwordchangeForm, guestAccountRequestForm, tokenchangeForm
from cbioportal.hub.models import User

logger = logging.getLogger(__name__)

def indexpage(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    if request.user.is_active:
        return redirect('/hub/projects')

    return render(
        request,
        'app/index.html',
        context = 
        {
            'title': 'Home Page',
            'year': datetime.now().year,
        }
    )

def loginHandler(request, *v, **kw):
    if request.method == 'GET':
        if request.user.is_active:
            logger.debug('%s is active' % request.user)
            try:
                User.objects.get(username = request.user.username)
                logger.warning('user %s is already logged in and is a hubuser' % request.user)
                messages.info(request, 'You are already logged in as %s' % request.user)
                return redirect('projects')
            except User.DoesNotExist:
                logger.warning('user %s is not a hub user, we log it out' % request.user)
                if "%s"%request.user == 'hubadmin':
                    return redirect('projects')
                else:
                    logout(request)
                 
        logger.debug('render login')
        return login_view(request, template_name = 'auth/login.html', authentication_form = authenticationForm)
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)
        if user is not None:
            try:
                User.objects.get(username = user.username)
                logger.info('user %s logs in' % request.user)
                login(request, user)
                return redirect('projects')
            except User.DoesNotExist:
                logger.warning('user %s is not a hub user, we do not log it in' % request.user)
                messages.error(request, 'You tried to log in as %s, but as you are not a hub user we deny access' % user)
        return redirect('login')
    return redirect('indexpage')


def logoutHandler(request):
    logout(request)
    return redirect('indexpage')



urlpatterns = [
#    url(r'^/?$', indexpage, name = 'indexpage'),
#
#    url(r'^/login/?$', loginHandler, name = 'login'),
#    url(r'^/logout$', logoutHandler, name = 'logout'),
#    url(r'^/passwordreset$', passwordresetForm, name = 'passwordreset'),
#    url(r'^/passwordtoken$', passwordtokenForm, name = 'passwordresettoken'),
#    url(r'^/passwordchange$', passwordchangeForm, name = 'passwordchange'),
#    url(r'^/guestaccount$', guestAccountRequestForm, name = 'guestaccount'),
#
#    url(r'^/tokenchange$', tokenchangeForm, name = 'tokenchange'),
#
#
#    url(r'^/ws', include('cbioportal.hub.ws')),
#    url(r'^/s', gt),
]
