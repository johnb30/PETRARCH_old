from nltk import chunk
from nltk import word_tokenize
import itertools
from joblib import Parallel, delayed
from datetime import datetime


def parse(event_dict, input_chunker, input_tagger, cores):
    """
    Function that calls the `parse_sent` function in parallel. Helper
    function to make calling the necessary functions cleaner.

    Parameters
    ----------

    event_dict: Dictionary.
                Dictionary containing the sentences to be parsed. Assumes
                each event has a unique identifier as the key.

    input_chunker: trained NLTK chunker.

    Note
    ----

    This is the function that should be called directly in a script.

    """
    parsed = Parallel(n_jobs=cores)(delayed(parse_call)
                                 (sent=event_dict[key]['story'], key=key,
                                  input_chunker=input_chunker,
                                  input_tagger=input_tagger)
                                 for key in event_dict)

    for parsed_sent in parsed:
        key = parsed_sent.keys()[0]
        event_dict[key].update(parsed_sent[key])


def parse_call(sent, key, input_chunker, input_tagger):
    sent_parser = SentParse(sent, key)
    parsed_info = sent_parser.parse_sent(input_chunker, input_tagger)

    return parsed_info


class SentParse():
    def __init__(self, sent, key):
        self.sent = sent
        self.key = key

    def parse_sent(self, input_chunker, input_tagger):
        """
        Function to parse a given sentence. Tokenizes, POS tags, and chunks a
        given sentence, along with extracting noun and verb phrases.

        Parameters
        ----------

        input_chunker: trained NLTK chunker.

        Returns
        -------

        sub_event_dict: Dictionary.
                        Container for  the POS-tagged sentence, chunked
                        sentence, noun phrases, and verb phrases for each event
                        in the input file.

        """
        time1 = datetime.now()
        sub_event_dict = {self.key: {}}
        #Tokenize the words
        toks = word_tokenize(self.sent)
        #Part-of-speech tag the tokens
        tags = input_tagger.tag(toks)
        tags = [tag for tag in tags if tag[1] != 'POS']
        chunker = TagChunker(input_chunker)
        #Use chunker to chunk the tagged words and combine into a tree
        self.tree = chunker.parse(tags)
        sub_event_dict[self.key]['tagged'] = tags
        sub_event_dict[self.key]['sent_tree'] = self.tree

        noun_phrases = self._get_np()
        verb_phrases = self._get_vp()
        time2 = datetime.now()

        time3 = time2-time1
        sub_event_dict[self.key]['parse_chunk_time'] = time3

        sub_event_dict[self.key]['noun_phrases'] = noun_phrases
        sub_event_dict[self.key]['verb_phrases'] = verb_phrases

        return sub_event_dict

    def _get_np(self):
        """
        Private function to extract noun phrases from a parse tree of any given
        sentence.

        Parameters
        ----------

        tree: NLTK tree object.
            Parse tree for a particular sentence.

        Returns
        -------

        noun_phrases: List.
                    Noun phrases within a sentence.
        """
        noun_phrases = []
        for sub in self.tree.subtrees(filter=lambda x: x.node == 'NP'):
            nouns = []
            for i in xrange(len(sub)):
                nouns.append(sub[i][0])
            nouns = ' '.join(nouns)
            noun_phrases.append(nouns)

        return noun_phrases

    def _get_vp(self):
        """
        Private function to extract verb phrases from a parse tree of any given
        sentence.

        Parameters
        ----------

        tree: NLTK tree object.
            Parse tree for a particular sentence.

        Returns
        -------

        verb_phrases: List of tuples.
                    Collection of verb phrases in a sentence. The tuples are
                    of the form (verb, noun phrase), where the
                    noun phrase is one that immediately follows the verb.

        """
        verb_phrases = []
        prev_type = None
        prev_chunk = None
        for sub in self.tree.subtrees(filter=lambda x: x != 'S'):
            if prev_type == 'VP' and sub.node == 'NP':
                verb = ' '.join([vw[0] for vw in prev_chunk])
                noun = ' '.join([nw[0] for nw in sub])
                verb_phrases.append((verb, noun))
            prev_type = sub.node
            prev_chunk = sub

        return verb_phrases


#Chunker code pulled from
#http://streamhacker.wordpress.com/2009/02/23/chunk-extraction-with-nltk/
class TagChunker(chunk.ChunkParserI):
    """Class used to create a chunker for use in parsing POS-tagged
    sentences."""
    def __init__(self, chunk_tagger):
        self._chunk_tagger = chunk_tagger

    def parse(self, tokens):
        """
        Function to chunk a POS-tagged sentence using a trained chunker.

        Parameters
        ----------

        tokens: List.
                POS-tagged sentence.

        Returns
        -------

        chunked: NLTK tree object.
                 Chunked sentence in NLTK tree form.

        """
        # split words and part of speech tags
        (words, tags) = zip(*tokens)
        # get IOB chunk tags
        chunks = self._chunk_tagger.tag(tags)
        # join words with chunk tags
        wtc = itertools.izip(words, chunks)
        # w = word, t = part-of-speech tag, c = chunk tag
        lines = [' '.join([w, t, c]) for (w, (t, c)) in wtc if c]
        # create tree from conll formatted chunk lines
        chunked = chunk.conllstr2tree('\n'.join(lines))

        return chunked
