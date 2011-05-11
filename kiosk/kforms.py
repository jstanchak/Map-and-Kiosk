from django.db import models
from django import forms
from django.forms import ModelForm
from kiosk.models import Venue, MenuItem

class VenueForm(ModelForm):
	class Meta:
		model = Venue
		exclude = ('slug', 'author')
		
class MenuItemForm(forms.Form):
	item_name = forms.CharField(max_length = 100)
	price = forms.DecimalField(max_digits=10, decimal_places=2)
	description = forms.CharField(max_length=100, required=False)
	image = forms.FileField(required=False)
	
	def __init__(self, venue=None, *args, **kwargs):
		self.venue = venue
		super(MenuItemForm, self).__init__(*args, **kwargs)
		
	def save(self, image=None):
		menu_item = MenuItem(venue = self.venue, item_name = self.cleaned_data['item_name'], description = self.cleaned_data['description'], price = self.cleaned_data['price'], image=image)
		menu_item.save()
		
class NewMenuItemForm(ModelForm):
	class Meta:
		model = MenuItem
		exclude = ('venue',)
