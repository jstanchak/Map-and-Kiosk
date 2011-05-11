from kiosk.models import Venue, MenuItem
from django.contrib import admin


class MenuItemInline(admin.TabularInline):
	model = MenuItem
	extra = 5
	
class VenueAdmin(admin.ModelAdmin):
	list_display = ('venue_name', 'author')
	list_filter = ('author',)
	exclude = ['slug']
	inlines = [MenuItemInline]

	def queryset(self, request):
		qs = super(VenueAdmin, self).queryset(request)
		if request.user.is_superuser:
			return qs
		else:
			return qs.filter(author = request.user)
			
	def save_model(self, request, obj, form, charnge):
		obj.author = request.user 
		obj.save()
		
	def has_change_permission(self, request, obj=None):
		if not obj:
			return True
		if request.user.is_superuser or obj.author == request.user:
			return True
		else:
			return False
			
	has_delete_permission = has_change_permission

admin.site.register(Venue, VenueAdmin)
