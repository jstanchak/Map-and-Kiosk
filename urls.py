from django.conf.urls.defaults import *
from django.contrib.auth.views import login
from django.views.static import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^venmoapp/', include('venmoapp.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'media/(?P<path>.*)$', 'django.views.static.serve', {'document_root':settings.MEDIA_ROOT}),
	(r'^cars/json', 'cars.views.cars'),
	(r'^map/', include('map.urls')),
	(r'^kiosk/', include('kiosk.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/login/$', login),
    (r'^accounts/logout/$', 'kiosk.views.logout'),
    (r'^accounts/profile/$', 'kiosk.views.profile'),
    (r'^accounts/signup/$', 'kiosk.views.signup'),
    (r'^$', 'kiosk.views.base'),
)
