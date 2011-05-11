from django.db import models

class Maker(models.Model):
	name = models.CharField(max_length=128)
	url = models.URLField()
	
	def json(self):
		return {
			'name': self.name,
			'url': self.url,
			'cars': [car.json() for car in Car.objects.filter(maker=self).order_by('name')]
		}
	
	def __unicode__(self):
		return self.name
		
class Car(models.Model):
	maker = models.ForeignKey(Maker)
	name = models.CharField(max_length=128)
	url = models.URLField()
	image = models.URLField()
	
	def json(self):
		fields = ('name', 'url', 'image')
		return dict((field, self.__dict__[field]) for field in fields)
	
	def __unicode__(self):
		return self.name


