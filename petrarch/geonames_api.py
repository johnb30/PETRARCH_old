import urllib2
import simplejson as json


def make_params(params_dict):
    params = ''
    for key in params_dict:
        params += str(key) + '=' + str(params_dict[key]) + '&'
    return params


def fetch_JSON(params, username):
    domain = 'http://api.geonames.org/searchJSON?'
    uri = domain + params + 'username=' + username
    resource = urllib2.urlopen(uri).readlines()
    js = json.loads(resource[0])
    return js


def get_lat_lon(params, username):
    domain = 'http://api.geonames.org/searchJSON?'
    uri = domain + params + 'username=' + username
    resource = urllib2.urlopen(uri).readlines()
    js = json.loads(resource[0])
    lat = str(js['geonames'][0]['lat'])
    lng = str(js['geonames'][0]['lng'])
    return lat, lng


if __name__ == '__main__':
    params = make_params({'q': 'Karachi'})
    results = fetch_JSON(params)
    lat = results['geonames'][0]['lat']
    lng = results['geonames'][0]['lng']
    print 'The latitude is: %s' % (str(lat))
    print 'The longitude is: %s' % (str(lng))
