import geonames_api
import nltk.stem
from nltk import trigrams
from joblib import Parallel, delayed

def process(event_dict, username=None, geolocate=False, feature_extract=False):

    processed = list()
    for key in event_dict.keys():
        tagged_sent  = event_dict[key]['tagged']
        noun_phrases = event_dict[key]['noun_phrases']
        verb_phrases = event_dict[key]['verb_phrases']
        temp = post_process(tagged_sent, key, noun_phrases, verb_phrases, 
            geo=geolocate, username=username, feature=feature_extract)                            
        processed.append(temp)

    for processed_sent in processed:
        key = processed_sent.keys()[0]
        event_dict[key].update(processed_sent[key])

#    post_parsed = Parallel(n_jobs=-1)(delayed(process_call)
#                                        (sent=event_dict[key]['story'],
#                                        key=key, input_tagger=input_tagger,
#                                        geolocate=geolocate,
#                                        feature_extract=feature_extract,
#                                        username=username)
#                                        for key in event_dict)
#
#    for post_parsed_sent in post_parsed:
#        key = post_parsed_sent.keys()[0]
#        event_dict[key].update(post_parsed_sent[key])


#def process_call(sent, key, input_tagger, username=None, geolocate=False, feature_extract=False):
#    post_processor = ProcessSuite(sent, key, input_tagger)
#    processed_info = post_processor.post_process(geolocate, username, feature_extract)

def post_process(pos_tagged, key, noun_phrases, verb_phrases, geo=False, username=None, feature=False):
    """
    Helper function to call the various post-processing functions, e.g.
    geolocation and feature extraction.

    Parameters
    ----------

    Username: String.
            Geonames username.

    """
    tri = nltk.trigrams(pos_tagged)
    if geo and not username:
        print """You must enter a username for geonames.org if you wish to
                    geolocate events."""
    sub_event_dict = {key: {}}
    if geo:
        lat, lon = geolocate(tri, username)
        sub_event_dict[key]['lat'] = lat
        sub_event_dict[key]['lon'] = lon

    if feature:
        #_v_to_cd_dist(pos_tagged)
        #sub_event_dict[key]['num_involved'] = []
        sub_event_dict[key]['num_involved'] = num_involved(pos_tagged, noun_phrases, verb_phrases)

    return sub_event_dict


def geolocate(trigrams, username):
    """
    Function to pull location information from a sentence. The location
    is then passed to the `geonames_api` to obtain latitude and
    longitudes for each event.

    Parameters
    ------
    username: String.
                Username for geonames.org.

    Returns
    -------

    lat: String.
            latitude coordinate

    lon: String.
            longitude coordinate

    """
    #TODO: What about two word cities? Baton Rouge, New Orleans, etc.

    #Create bigrams
    loc = None
    #Words that indicate a location
    keep = ['in', 'to', 'from']
    #Select words from the bigram where the first word is 'to' or 'in'
    #and the second word has a proper noun tag.
    for (w1, t1), (w2, t2), (w3, t3) in trigrams:
        if (w1 in keep) and (t2 == 'NNP'):
            loc = w2
        elif (t1.startswith('N') and w2 in keep and t3 == 'NNP'):
            loc = w3
    #If it found a location
    if loc:
        #Create parameters to pass to the geonames_api
        loc = nltk.stem.PorterStemmer().stem(loc)
        params = geonames_api.make_params({'q': loc})
        #Try to obtain coordinates from geonames
        try:
            lat, lon = geonames_api.get_lat_lon(params, username)
            return lat, lon
        #but if something went wrong, return 'NA' for lat, lon
        except IndexError:
            lat, lon = 'NA', 'NA'
            return lat, lon
    #If a location hasn't been found, return 'NA' for lat, lon
    if not loc:
        lat, lon = 'NA', 'NA'
        return lat, lon

def _is_number(numstr):
    """
    Private function to check whether a string is a number

    Parameters
    ------
    numstr: String.
            String to check.

    Returns
    ------
        Boolean. True if string a number. False otherwise.
    """
    try:
        float(numstr)
        return True
    except ValueError:
        return False


def _english_to_digit(textnum, numwords={}):
    """
    Private function to convert written numbers to digits. Copy-pasta from
    http://stackoverflow.com/questions/493174/is-there-a-way-to-convert- \
    number-words-to-integers-python

    Parameters
    ------

    textnum: String.
                Number written as text.

    Returns
    -------

    out: Tuple.
            The number represented as a digit, and the string describing
            the type of object that the number is describing.

    """

    ## TK: Need a way to deal with phrases likes "a few", "a number of",
    ## "hundreds of thousands", etc
    textnum = textnum.lower()

    if not numwords:
        ## Adding fixed values here

        ## TK: This is a placeholder for scale-type numbers
        ## Need a better way to handle these. One solution is to have
        ## a scale variable that assigns something like 5-25 for "several",
        ## 50-99 for "dozens", etc.
        approxs = {
            "several"   : 5,
            "tens"      : 50,
            "dozens"    : 50,
            "scores"    : 50,
            "hundreds"  : 10 ** 2,
            "thousands" : 10 ** 3,
            "millions"  : 10 ** 6,
            "billions"  : 10 ** 9,
            "trillions" : 10 ** 12 
        }

        ## unused right now, but possibly in the future.
        range_words = {
            "several"   : "5-24",
            "tens"      : "10-99",
            "dozens"    : "50-99",
            "scores"    : "50-99",
            "hundreds"  : "100-999",
            "thousands" : "1000-9999"
        }

        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven",
            "eight", "nine", "ten", "eleven", "twelve", "thirteen",
            "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
            "nineteen"]

        tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty",
                "seventy", "eighty", "ninety"]

        scales  = {
            "hundred"  : 2,
            "thousand" : 3, 
            "million"  : 6,
            "billion"  : 9,
            "trillion" : 12
            }

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)

        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)

        for word, exp in scales.iteritems():
            numwords[word] = (10 ** exp, 0)

        for word, number in approxs.iteritems():
            numwords[word] = (1, number) 

    current = result = 0
    type_words = []
    for word in textnum.split():
        if _is_number(word):
            current = float(word)
        elif word in numwords:
            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0
        else:            
            type_words.append(word)

    out = result + current
    return (out, " ".join(type_words))

def num_involved(pos_tagged, noun_phrases, verb_phrases):
    """
    Function to obtain information regarding the number of individuals
    involved in a given event.

    The algorithm works as follows:
        Go through verb phrases and attempt to pull out number from direct object
        and associate it with the verb phrase.

        Then, go through noun phrases and look for a number.
        If one exists, check if the noun phrase comes right before a verb phrase.
        Assign the verb in that phrase to the number.


    Parameters
    ------

    noun_phrases: List.
                List of noun phrases.
    verb_phrases: List.
                List of tuples containing verbs and their direct objects.

    Returns
    -------

    num_phrases: Array.
            Array of tuples in the format (number, type, verb)

    """

    num_phrases = []
    for verb, obj in verb_phrases:
        ## TK: Eventually change this to account for numbers like
        ## "two million"

        num, type = _english_to_digit(obj)

        if num:
            num_phrases.append( (num, type, verb) )

    ## TK: Need to implement the noun phrase part of this

    return num_phrases
