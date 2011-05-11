from django.db import models

class Venue(models.Model):
    author = models.ForeignKey('auth.User')
    slug = models.SlugField()
    venue_name = models.CharField(max_length=200)
    venmo_account = models.CharField(max_length=100, verbose_name='venmo account name')
    image = models.ImageField(upload_to='photos/venues/%Y-%m-%d', blank=True, null=True)

    def __unicode__(self):
        return '%s - %s' % (self.author, self.venue_name)

    def get_absolute_url(self):
        return '/kiosk/%s/' % self.slug
	
	def get_cart_url(self):
		return '/kiosk/%s/cart' % self.slug
        
class MenuItem(models.Model):
    venue = models.ForeignKey(Venue)
    item_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=100, blank=True)
    image = models.ImageField(upload_to='photos/menuitems/%Y-%m-%d', blank=True, null=True)

    def __unicode__(self):
        return '%s - $%s' % (self.item_name, self.price)
   