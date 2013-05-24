import urllib2
import simplejson as json


def make_params(params_dict):
    """
    Function to transform a dictionary of parameters into search terms
    for geonames.

    Parameters
    ----------

    params_dict: Dictionary.
                 Dictionary of search parameters.
    """
    params = ''
    for key in params_dict:
        params += str(key) + '=' + str(params_dict[key]) + '&'
    return params


#Pulled from https://github.com/gregrobbins/geonames-python
def fetch_JSON(params, username):
    """
    Function to search geonames for a given parameter.

    Parameters
    ----------

    params: String.
            Search parameters for geonames.

    username: String.
              Geonames username.
    """
    domain = 'http://api.geonames.org/searchJSON?'
    uri = domain + params + 'username=' + username
    resource = urllib2.urlopen(uri).readlines()
    js = json.loads(resource[0])
    return js


def get_lat_lon(params, username):
    """
    Function to retrieve geographical information from geonames.org,
    parse the returned data and retrieve the latitude and longitude.

    Parameters
    ----------

    params: String.
            Search parameters for geonames.

    username: String.
              Geonames username.
    """
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
