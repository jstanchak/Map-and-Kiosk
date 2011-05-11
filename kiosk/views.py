import logging
from django.http import HttpResponse, HttpResponseRedirect
from kiosk.models import Venue, MenuItem
from kiosk import kforms
from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.urlresolvers import reverse
from django.contrib import auth
import htmlentitydefs, re 
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import simplejson
from kiosk.Foursquare import Foursquare
from kiosk.GoogleMaps import gMaps 

from django.core import serializers

from cart import Cart
from cart.models import Item, AddItemToCartForm

import urllib


def slughelper(separator, text1, text2=None):
	slug1 = ""
	for c in text1.lower():
		try:
			slug1 += htmlentitydefs.codepoint2name[ord(c)]
		except:
			slug1 += c
	slug1 = re.sub("([a-zA-z])(uml|acute|grave|circ|tilde|cedil)", r"\1", slug1)
	slug1 = re.sub("\W", " ", slug1)
	slug1 = re.sub(" +", separator, slug1)
	slug1.strip()
	if text2:
		slug2 = ""
		for c in text2.lower():
			try:
				slug2 += htmlentitydefs.codepoint2name[ord(c)]
			except:
				slug2 += c
		slug2 = re.sub("([a-zA-z])(uml|acute|grave|circ|tilde|cedil)", r"\1", slug2)
		slug2 = re.sub("\W", " ", slug2)
		slug2 = re.sub(" +", separator, slug2)
		slug2.strip()
		slug = slug1 + '_' + slug2
		return slug
	return slug1

def slugify(separator, text1, text2=None):
	candidate = slughelper(separator, text1, text2)
	slug_list = Venue.objects.filter(slug__icontains=candidate)
	if slug_list:
		slug = candidate+str(len(slug_list))
	else:
		slug = candidate
	return slug


def base(request):
	return render_to_response('landing.html',context_instance=RequestContext(request))

#user stuff
@csrf_protect	
def signup(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			new_user = form.save()
# 			new_user.groups.add('venues')
# 			new_user.save()
			return HttpResponseRedirect(reverse('kiosk.views.index'))
	else:
		form = UserCreationForm()
	context = dict(form=form)
	return render_to_response('registration/signup.html', context, context_instance=RequestContext(request))
	
def logout(request):
	auth.logout(request)
	return render_to_response('landing.html')			

#kiosk stuff
@login_required
def index(request):
	if request.user.is_superuser:
		venues = Venue.objects.all().order_by('venue_name')[:20]
	else:
		venues = Venue.objects.filter(author = request.user).order_by('venue_name')[:20]
	content = dict(venues = venues)
	return render_to_response('kiosk/index.html', content)

@login_required
@csrf_protect	
def create(request):
	itemforms=[]
	if request.method == 'GET':
		venueform = kforms.VenueForm()
		itemforms = []
		for i in range(6):
			itemforms.append(kforms.MenuItemForm(prefix = 'f%s'%i))
	if request.method == 'POST':
		venueform = kforms.VenueForm(request.POST, request.FILES)
		itemform = kforms.MenuItemForm()
		if venueform.is_valid():
			# Create slug
			venue = venueform.save(commit=False)
			venue.author = request.user
			venue.slug = slugify('_', str(venue.author), venue.venue_name)
			venue.image = request.FILES["image"]
			venue.save()
			# Process items
			itemforms = []
			for i in range(6):
				itemforms.append(kforms.MenuItemForm(venue = venue, prefix = 'f%s'%i, data=request.POST))
			i = 0
			for form in itemforms:
				if form.is_valid():
					img_name = 'f'+str(i)+'-image'
					image = request.FILES[img_name]
					form.save(image)
				i += 1
			return HttpResponseRedirect(venue.get_absolute_url())
		imgdict = request.FILES
		content = dict(venueform=venueform, itemforms=itemforms, imgdict=imgdict)
		return render_to_response('kiosk/create.html', content, context_instance=RequestContext(request))
	content = dict(venueform=venueform, itemforms=itemforms)
	return render_to_response('kiosk/create.html', content, context_instance=RequestContext(request))

@login_required	
@csrf_protect	
def edit(request, slug):
	if request.method == 'GET':
		venue = get_object_or_404(Venue, slug = slug)
		venueform = kforms.VenueForm(instance=venue)
	if request.method == 'POST':
		venue = get_object_or_404(Venue, slug = slug)		
		venueform = kforms.VenueForm(request.POST, instance=venue)
		if venueform.is_valid():
			venue = venueform.save(commit=False)
			venue.slug = slugify('_', str(venue.author), venue.venue_name)
			venue.save()
			return HttpResponseRedirect(venue.get_absolute_url())
	content = dict(venue=venue, venueform=venueform)
	return render_to_response('kiosk/edit.html', content, context_instance=RequestContext(request))

@login_required
@csrf_protect	
def edit_items(request, slug):
	if request.method == 'GET':
		venue = get_object_or_404(Venue, slug = slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		itemforms = []
		i = 1
		for item in itemlist:
			itemforms.append(kforms.NewMenuItemForm(instance=item, prefix = 'f%s'%i))
			i += 1
	if request.method == 'POST':
		venue = get_object_or_404(Venue, slug = slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		itemforms = []
		i = 1
		for item in itemlist:
			itemforms.append(kforms.NewMenuItemForm(instance=item, prefix = 'f%s'%i, data=request.POST))
			i += 1
		for iform in itemforms:
			if iform.is_valid():
				iform.save()
		return HttpResponseRedirect(venue.get_absolute_url())
	content = dict(venue=venue, itemlist=itemlist, itemforms=itemforms)
	return render_to_response('kiosk/edit_items.html', content, context_instance=RequestContext(request))

@login_required
@csrf_protect		
def add_items(request, slug):
	if request.method == 'GET':
		venue = get_object_or_404(Venue, slug = slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		itemforms = []
		for i in range(10):
			itemforms.append(kforms.MenuItemForm(prefix = 'f%s'%i))
	if request.method == 'POST':
		venue = get_object_or_404(Venue, slug = slug)
		itemform = kforms.MenuItemForm()
		itemforms = []
		for i in range(10):
			itemforms.append(kforms.MenuItemForm(venue=venue, prefix = 'f%s'%i, data=request.POST))
		for form in itemforms:
			if form.is_valid():
				form.save()
		return HttpResponseRedirect(venue.get_absolute_url())
	content = dict(venue=venue, itemlist=itemlist, itemforms=itemforms)
	return render_to_response('kiosk/add_items.html', content, context_instance=RequestContext(request))

@login_required	
def detail(request, slug):
	venue = get_object_or_404(Venue, slug=slug)
	items = MenuItem.objects.filter(venue=venue)
	content = dict(venue = venue, items = items)
	return render_to_response('kiosk/venue_details.html', content)

@login_required	
def profile(request):
	return render_to_response('registration/profile.html')
	
# Cart stuff

@csrf_protect		
def menu(request, slug):
	if request.method == 'GET':
		venue = get_object_or_404(Venue, slug = slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		cart = Cart(request)
		cart_total = cart.cart_total()
	if request.method == 'POST':
		venue = get_object_or_404(Venue, slug = slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		cart = Cart(request)
		for item in itemlist:
			add_name = str(item.item_name)+'_add'
			if add_name in request.POST:
				uptd = 0
				for c in cart:
					if c.product.item_name == item.item_name:
						quantity = c.quantity
						cart.update(item, quantity + 1, item.price)
						uptd = 1
				if uptd == 0:
					cart.add(item, item.price, 1)
		for item in cart:
			id = item.object_id
			menu_item = get_object_or_404(MenuItem, id=id)
			name = str(item.product.item_name)
			remove_name = name+'_remove'
			if remove_name in request.POST:
				cart.remove(menu_item)
			else:
				if name in request.POST:
					quantity = request.POST[name]
					if quantity:
						cart.update(menu_item, quantity, item.unit_price)
		return HttpResponseRedirect(reverse('kiosk.views.menu', args=(slug,)))	
	content = dict(venue=venue, itemlist=itemlist, cart=cart, cart_total=cart_total)
	return render_to_response('kiosk/menu.html', content, context_instance=RequestContext(request))

@csrf_protect	
def get_cart(request, slug):
	if request.method == 'GET':
		venue = get_object_or_404(Venue, slug=slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		cart = Cart(request)
		cart_total = cart.cart_total()
	if request.method == 'POST':
		venue = get_object_or_404(Venue, slug=slug)
		itemlist = MenuItem.objects.filter(venue=venue)
		cart = Cart(request)
		for item in cart:
			id = item.object_id
			menu_item = get_object_or_404(MenuItem, id=id)
			name = str(item.product.item_name)
			remove_name = name+'_remove'
			if remove_name in request.POST:
				cart.remove(menu_item)
			else:
				quantity = request.POST[name]
				if quantity:
					cart.update(menu_item, quantity, item.unit_price)
		return HttpResponseRedirect(reverse('kiosk.views.get_cart', args=(slug,)))
	note_list = []
	for item in cart:
		note_list.append(str(item.quantity)+" "+item.product.item_name)
	note = ", ".join(note_list)
	link_note = urllib.quote(note)	
	link = 'https://venmo.com?txn=Pay&recipients='+venue.venmo_account+'&amount='+str(cart_total)+"&note="+link_note	
	content = dict(venue=venue, cart=cart, cart_total=cart_total, link=link, note=note)
	return render_to_response('kiosk/cart.html', content, context_instance=RequestContext(request))
	
@csrf_protect
def foursquare(request):
	logging.error("HELLO")
	foursquare_checkins_at_venue = Foursquare.get_venue_checkins('2292853')
	content = dict(foursquare_checkins_at_venue = foursquare_checkins_at_venue)
	return render_to_response('foursquare_checkins_at_venue.html', content, context_instance=RequestContext(request))
	

@csrf_protect
def fsq_places(request):
    foursquare_venues = []
    ll_string = ''
    if request.method == 'POST':
        address = request.POST["post_address"]	
    	latlong = gMaps.get_latlong(address)
    	lat = latlong['results'][0]['geometry']['location']['lat']
    	lng = latlong['results'][0]['geometry']['location']['lng']
    	ll_string = '%s, %s' % (lat, lng)
    	foursquare_venues = Foursquare.get_venues(ll_string)
    content = dict(foursquare_venues = foursquare_venues, ll_string = ll_string)
    return render_to_response('foursquare_venues.html', content, context_instance=RequestContext(request))