from django.http import HttpResponse
from models import *
import json

def cars(request):
	data = [maker.json() for maker in Maker.objects.all().order_by('name')]
	nice = "nice" in request.GET
	callback = request.GET.get('callback')
	jsonString = json.dumps(data, sort_keys=nice, indent=4 if nice else None)
	if callback:
		jsonString = '%s(%s)' % (callback,jsonString)
	return HttpResponse(jsonString, content_type='application/json')

# Create your views here.
