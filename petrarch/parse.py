import nltk as nk
import preprocess
import itertools
from joblib import Parallel, delayed


def parse(event_dict, input_chunker, username, process2=False):
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
    parsed = Parallel(n_jobs=-1)(delayed(parse_sent)
                                 (sent=event_dict[key]['story'], key=key,
                                  input_chunker=input_chunker)
                                 for key in event_dict)

    for parsed_sent in parsed:
        key = parsed_sent.keys()[0]
        event_dict[key].update(parsed_sent[key])

    if process2:
        post_parsed = Parallel(n_jobs=-1)(delayed(post_process)
                                         (sent=event_dict[key]['story'],
                                          key=key,
                                          username=username)
                                          for key in event_dict)

        for post_parsed_sent in post_parsed:
            key = post_parsed_sent.keys()[0]
            event_dict[key].update(post_parsed_sent[key])


def parse_sent(sent, key, input_chunker):
    """
    Function to parse a given sentence. Tokenizes, POS tags, and chunks a
    given sentence, along with extracting noun and verb phrases.

    Parameters
    ----------

    sent: String.
          Sentence to be parsed.

    key: String.
         Key of the event used to access the event from the events
         dictionary.

    input_chunker: trained NLTK chunker.

    Returns
    -------

    sub_event_dict: Dictionary.
                    Container for  the POS-tagged sentence, chunked
                    sentence, noun phrases, and verb phrases for each event
                    in the input file.

    """
    sub_event_dict = {key: {}}
    #Tokenize the words
    toks = nk.word_tokenize(sent)
    #Part-of-speech tag the tokens
    tags = nk.pos_tag(toks)
    tags = [tag for tag in tags if tag[1] != 'POS']
    chunker = TagChunker(input_chunker)
    #Use chunker to chunk the tagged words and combine into a tree
    tree = chunker.parse(tags)
    sub_event_dict[key]['tagged'] = tags
    sub_event_dict[key]['sent_tree'] = tree

    noun_phrases = _get_np(tree)
    verb_phrases = _get_vp(tree)

    sub_event_dict[key]['noun_phrases'] = noun_phrases
    sub_event_dict[key]['verb_phrases'] = verb_phrases

    return sub_event_dict


def post_process(sent, key, username):
    """
    Helper function to call the various post-processing functions, e.g.
    geolocation and feature extraction.

    Parameters
    ----------

    sent: String.
          Sentence to parse.

    key: String.
         Key of the sentence in the general events dictionary.

    Username: String.
              Geonames username.

    """
    sub_event_dict = {key: {}}
    #Tokenize the words
    toks = nk.word_tokenize(sent)
    #Part-of-speech tag the tokens
    tags = nk.pos_tag(toks)
    pp = preprocess.Process(tags)
    lat, lon = pp.geolocate(username)
    sub_event_dict[key]['lat'] = lat
    sub_event_dict[key]['lon'] = lon

    sub_event_dict[key]['num_involved'] = pp.num_involved()

    return sub_event_dict


def _get_np(tree):
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
    for sub in tree.subtrees(filter=lambda x: x.node == 'NP'):
        nouns = []
        for i in xrange(len(sub)):
            nouns.append(sub[i][0])
        nouns = ' '.join(nouns)
        noun_phrases.append(nouns)

    return noun_phrases


def _get_vp(tree):
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
    for sub in tree.subtrees(filter=lambda x: x != 'S'):
        if prev_type == 'VP' and sub.node == 'NP':
            verb = ' '.join([vw[0] for vw in prev_chunk])
            noun = ' '.join([nw[0] for nw in sub])
            verb_phrases.append((verb, noun))
        prev_type = sub.node
        prev_chunk = sub

    return verb_phrases


class TagChunker(nk.chunk.ChunkParserI):
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
        chunked = nk.chunk.conllstr2tree('\n'.join(lines))

        return chunked
