import logging
from django.utils import simplejson
import urllib
import urllib2

class Foursquare(object):
    BASE_URL = "https://api.foursquare.com/v2"

    @classmethod    
    def get_venues(self, lat_long, timeout=9000):
        url = "https://api.foursquare.com/v2/venues/search"
        params = {
            "client_id": 'J4ZAL0YOTY4HQXKYWLIU1O3DULJD5UOJOBHSX2E32I2SIKSE',
            "client_secret": '05UNARYD201FM4NVF41Z5HAFFX5BN5HICYSQWLFCDEXWHGKN',
            "oauth_token": "VRRXHCCBZAKR0XXBB11BZJSA1K2TVBM5FIAEXWDRFKGJT44I",
            "ll": lat_long,
        }
        
        data = urllib.urlencode(params)
        request = urllib2.Request('%s?%s' % (url, data) )
        logging.debug("HELLO")
        resp = simplejson.load(urllib2.urlopen(request))
        try:
            resp = simplejson.load(urllib2.urlopen(request))
        except:
            logging.debug("[geo_utils.foursquare_get_venue_details] error parsing json response from foursquare %s" % locals())
            return {"locals": locals()}
        return resp
            
    @classmethod    
    def get_venue_checkins(self, venue_id, timeout=9000):
        url = "https://api.foursquare.com/v2/venues/"
        params = {
            "client_id": 'J4ZAL0YOTY4HQXKYWLIU1O3DULJD5UOJOBHSX2E32I2SIKSE',
            "client_secret": '05UNARYD201FM4NVF41Z5HAFFX5BN5HICYSQWLFCDEXWHGKN',
            "oauth_token": "VRRXHCCBZAKR0XXBB11BZJSA1K2TVBM5FIAEXWDRFKGJT44I"
        }
        
        endpoint = "%s%s%s" % (url, '12422', "/herenow")
        data = urllib.urlencode(params)
        request = urllib2.Request('%s?%s' % (endpoint, data) )
        logging.debug("HELLO")
        resp = simplejson.load(urllib2.urlopen(request))
        try:
            resp = simplejson.load(urllib2.urlopen(request))
        except:
            logging.debug("[geo_utils.foursquare_get_venue_details] error parsing json response from foursquare %s" % locals())
            return {"locals": locals()}
        return resp