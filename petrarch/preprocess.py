import geonames_api
import nltk as nk


class Process():
    def __init__(self, sent):
        self.trigrams = nk.trigrams(sent)

    def geolocate(self, username):
        """
        Function to pull location information from a sentence. The location
        is then passed to the `geonames_api` to obtain latitude and
        longitudes for each event.

        Inputs
        ------
        username : username for geonames.org. String.

        Returns
        -------

        lat : latitude coordinate

        lon : longitude coordinate

        """
        #TODO: What about two word cities? Baton Rouge, New Orleans, etc.

        #Create bigrams
        loc = None
        #Words that indicate a location
        keep = ['in', 'to', 'from']
        #Select words from the bigram where the first word is 'to' or 'in'
        #and the second word has a proper noun tag.
        for (w1, t1), (w2, t2), (w3, t3) in self.trigrams:
            if (w1 in keep) and (t2 == 'NNP'):
                loc = w2
            elif (t1.startswith('N') and w2 in keep and t3 == 'NNP'):
                loc = w3
        #If it found a location
        if loc:
            #Create parameters to pass to the geonames_api
            loc = nk.stem.PorterStemmer().stem(loc)
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

    def _english_to_digit(textnum, numwords={}):
        """
        Private function to convert written numbers to digits. Copy-pasta from
        http://stackoverflow.com/questions/493174/is-there-a-way-to-convert- \
        number-words-to-integers-python

        Inputs
        ------

        textnum : number written as text. String.

        Returns
        -------

        out : number represented as a digit. String.

        """

        if not numwords:
            units = [
                "zero", "one", "two", "three", "four", "five", "six", "seven",
                "eight", "nine", "ten", "eleven", "twelve", "thirteen",
                "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
                "nineteen"]

            tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty",
                    "seventy", "eighty", "ninety"]

            scales = ["hundred", "thousand", "million", "billion", "trillion"]

            numwords["and"] = (1, 0)
            for idx, word in enumerate(units):
                numwords[word] = (1, idx)
            for idx, word in enumerate(tens):
                numwords[word] = (1, idx * 10)
            for idx, word in enumerate(scales):
                numwords[word] = (10 ** (idx * 3 or 2), 0)

        current = result = 0
        for word in textnum.split():
            word = str.lower(word)
            if word not in numwords:
                raise Exception("Illegal word: " + word)

            scale, increment = numwords[word]
            current = current * scale + increment
            if scale > 100:
                result += current
                current = 0

        out = str(result + current)
        return out

    def num_involved(self):
        """
        Function to obtain information regarding the number of individuals
        involved in a given event.

        Returns
        -------

        number : number of people involved in an event. Integer.

        """
        #Create trigrams
        number = str()
        #Select words with cardinal number POS tags that are preceded or
        #followed by verbs. This attemps to capture things such as '15 were
        #killed' or '15 killed' or 'killed 15'.
        for (w1, t1), (w2, t2), (w3, t3) in self.trigrams:
            if (t1 == 'CD') and (t3.startswith('V') or t2.startswith('V')):
                number = w1
            elif ((t1.startswith('V') or (t2.startswith('V') or t2 == 'CD'))
                  and (t3 == 'CD')):
                number = w3
        try:
            number = self._english_to_digit(number)
        except Exception:
            pass
        return number
