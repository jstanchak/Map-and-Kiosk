from django.conf.urls.defaults import *

urlpatterns = patterns('kiosk.views',
	(r'^$', 'index'),
	(r'create/$', 'create'),
#	(r'^add_to_cart/$', 'add_to_cart'),
	(r'(?P<slug>\w+)/edit/$', 'edit'),
	(r'(?P<slug>\w+)/edit_items/$', 'edit_items'),
	(r'(?P<slug>\w+)/add_items/$', 'add_items'),	
	(r'(?P<slug>\w+)/menu/$', 'menu'),
#cart stuff
	(r'(?P<slug>\w+)/cart/$', 'get_cart'),

	(r'foursquare/herenow', 'foursquare'),
	(r'foursquare/places', 'fsq_places'),
	
	(r'(?P<slug>\w+)/$', 'detail'),


	)