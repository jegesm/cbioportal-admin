"""
Definition of urls for cbioportal.
"""

from django.conf.urls import url, include
from django.contrib import admin
#admin.autodiscover()

def req_test(request):
    raise Exception(str(request.META))

urlpatterns = [
## ##    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
#    url(r'^cbioportal-admin/', include(admin.site.urls)),
    url(r'^cbioportal-admin/', admin.site.urls, name="admin"),
#    url(r'^cbioportal-admin/cbioadmin/', admin.site.urls),
        
#    url(r'^admin/', include('cbioportal.admin')),
]
