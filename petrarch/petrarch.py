import nltk as nk
import preprocess
import itertools
import argparse
from joblib import Parallel, delayed

#Chunker code pulled from
#http://streamhacker.wordpress.com/2009/02/23/chunk-extraction-with-nltk/


def _conll_tag_chunks(chunk_sents):
    """Private function to prepare the training data for the NLTK chunker"""
    #Parse the training data for the chunker
    tag_sents = [nk.chunk.tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]


def create_chunkers():
    """
    Function to create and train a chunker used to POS-tagged sentences.

    Returns
    -------

    ubt_chunker : NLTK trained chunker trained using unigrams, bigrams, and
                  trigrams.
    """
    #Get training data for chunker
    #Alternate between penn treebank and conll2000 to see which gets better
    #results
    #train_sents = nk.corpus.treebank_chunk.chunked_sents()
    train_sents = nk.corpus.conll2000.chunked_sents('train.txt')
    train_chunks = _conll_tag_chunks(train_sents)

    #Training the chunker
    u_chunker = nk.tag.UnigramTagger(train_chunks)
    ub_chunker = nk.tag.BigramTagger(train_chunks, backoff=u_chunker)
    ubt_chunker = nk.tag.TrigramTagger(train_chunks, backoff=ub_chunker)

    return ubt_chunker


class TagChunker(nk.chunk.ChunkParserI):
    def __init__(self, chunk_tagger):
        self._chunk_tagger = chunk_tagger

    def parse(self, tokens):
        """
        Function to chunk a POS-tagged sentence using a trained chunker.

        Inputs
        ------

        tokens : POS-tagged sentence.

        Returns
        -------

        chunked : chunked sentence.

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


def read_data(filepath):
    """
    Function to read in a file of news stories. Expects stories formatted
    in the traditional TABARI format. Adds each sentence, along with the
    meta data, to a dictionary.

    Input
    -----

    filepath : filepath of the file containing the sentence to be parsed.

    """
    event_dict = dict()
    data = open(filepath, 'r').read()
    sentences = data.split('\n\n')
    for sentence in sentences:
        #Strings are weird, so split into meta string, which contains meta
        #info and story part of the string
        meta_string = sentence[:sentence.find('\n')]
        day, ident, ident_long = meta_string.split(' ')
        story_string = sentence[sentence.find('\n'):].replace('\n', '')
        #Combine info into a dictionary
        story_info = {'day': day, 'id': ident, 'id_long': ident_long,
                      'story': story_string}
        #Add the new dict to the events dict with the ID as the key
        event_dict[ident] = story_info

    return event_dict


def _get_np(tree):
    """
    Private function to extract noun phrases from a parse tree of any given
    sentence.

    Inputs
    ------

    tree : parse tree for a particular sentence. NLTK tree object.

    Returns
    -------

    noun_phrases : noun phrases within a sentence. List.

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

    Inputs
    ------

    tree : parse tree for a particular sentence. NLTK tree object.

    Returns
    -------

    verb_phrases : collection of verb phrases in a sentence. List of tuples.
                   The tuples are of the form (verb, noun phrase), where the
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


def parse_sent(sent, key, input_chunker):
    """
    Function to parse a given sentence. Tokenizes, POS tags, and chunks a
    given sentence, along with extracting noun and verb phrases.

    Inputs
    ------

    sent : sentence to be parsed. String.

    key : key of the event used to access the event from the events
            dictionary. String.

    input_chunker : trained NLTK chunker.

    Returns
    -------

    sub_event_dict : dictionary containing the POS-tagged sentence, chunked
    sentence, noun phrases, and verb phrases for each event in the input file.

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


def parse(event_dict, input_chunker, username, process2=False):
    """
    Function that calls the `parse_sent` function in parallel. Helper
    function to make calling the necessary functions cleaner.


    Inputs
    ------

    event_dict : dictionary containing the sentences to be parsed. Assumes
                 each event has a unique identifier as the key.

    input_chunker : trained NLTK chunker.

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

if __name__ == '__main__':
    print 'Reading in data...'
    defaults = argparse.ArgumentParser()
    defaults.add_argument('-i', '--inputs',
                          help='File, or directory of files, to parse.', 
                          default=None)
    defaults.add_argument('-o', '--output', help='File to write parsed events',
                          default=None)
    defaults.add_argument('-u', '--username', help="geonames.org username",
                          default=None)
    defaults.add_argument('-p', '--postprocess', help="""Whether post 
                          processing, such as geolocation and feature 
                          extraction, should occur. Default False.""",
                          default=False, action='store_true')
#These will be used as the program develops further.
#    defaults.add_argument('-g', '--geolocate', action='store_true',
#                          default=False, help="""Whether to geolocate events.
#                          Defaults to False""")
#    defaults.add_argument('-f', '--features', action='store_true',
#                          default=False,
#                          help="""Whether to extract features from sentence.
#                          Defaults to False""")
    defaults.add_argument('-n', '--n_cores', type=int, default=-1,
                          help="""Number of cores to use for parallel
                          processing. Defaults to -1 for all cores""")
    args = defaults.parse_args()
    inputs = args.inputs
    out_path = args.output
    username = args.username
    post_proc = args.postprocess

    ubt_chunker = create_chunkers() 
    print 'Parsing sentences...'
    events = read_data(inputs)
    parse(events, ubt_chunker, username, post_proc)
    for event in events:
        print '=======================\n'
        print 'event id: {}\n'.format(event)
        print 'POS tagged sent:\n {}\n'.format(events[event]['tagged'])
        print 'NP tagged sent:\n {}\n'.format(events[event]['sent_tree'])
        print 'Noun phrases: \n {}\n'.format(events[event]['noun_phrases'])
        print 'Verb phrases: \n {}\n'.format(events[event]['verb_phrases'])
        try:
            print 'Geolocate: \n {}, {}\n'.format(events[event]['lat'],
                                                  events[event]['lon'])
        except KeyError:
            pass
        try:
            print 'Feature extract: \n {}\n'.format(events[event]['num_involved'])
        except KeyError:
            pass
