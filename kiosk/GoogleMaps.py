import logging
from django.utils import simplejson
import urllib
import urllib2

class gMaps(object):
    BASE_URL = "https://api.foursquare.com/v2"

    @classmethod    
    def get_latlong(self, address_string, timeout=9000):
        url = "http://maps.googleapis.com/maps/api/geocode/"
        params = {
            "address": address_string,
            "sensor": "false",
        }
        output = 'json'
        data = urllib.urlencode(params)
        request = urllib2.Request('%s%s?%s' % (url, output, data) )
        logging.debug("HELLO")
        resp = simplejson.load(urllib2.urlopen(request))
        try:
            resp = simplejson.load(urllib2.urlopen(request))
        except:
            logging.debug("[geo_utils.foursquare_get_venue_details] error parsing json response from foursquare %s" % locals())
            return {"locals": locals()}
        return resp