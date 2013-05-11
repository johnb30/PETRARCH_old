import nltk as nk
import nltk.corpus
import nltk.chunk
import itertools
import sys

#Chunker code pulled from
#http://streamhacker.wordpress.com/2009/02/23/chunk-extraction-with-nltk/


def conll_tag_chunks(chunk_sents):
    #Parse the training data for the chunker
    tag_sents = [nltk.chunk.tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]


def create_chunkers():
    #Get training data for chunker
    train_sents = nltk.corpus.conll2000.chunked_sents('train.txt')
    train_chunks = conll_tag_chunks(train_sents)

    #Training the chunker
    u_chunker = nltk.tag.UnigramTagger(train_chunks)
    ub_chunker = nltk.tag.BigramTagger(train_chunks, backoff=u_chunker)
    ubt_chunker = nltk.tag.TrigramTagger(train_chunks, backoff=ub_chunker)

    return ubt_chunker


class TagChunker(nltk.chunk.ChunkParserI):
    def __init__(self, chunk_tagger):
        self._chunk_tagger = chunk_tagger

    def parse(self, tokens):
        # split words and part of speech tags
        (words, tags) = zip(*tokens)
        # get IOB chunk tags
        chunks = self._chunk_tagger.tag(tags)
        # join words with chunk tags
        wtc = itertools.izip(words, chunks)
        # w = word, t = part-of-speech tag, c = chunk tag
        lines = [' '.join([w, t, c]) for (w, (t, c)) in wtc if c]
        # create tree from conll formatted chunk lines
        return nltk.chunk.conllstr2tree('\n'.join(lines))


def read_data(filepath, event_dict):
    data = open(filepath, 'r').read()
    sentences = data.split('\n\n')
    for sentence in sentences:
        #Strings are weird, so split into meta string, which contains meta info
        #and story part of the string
        meta_string = sentence[:sentence.find('\n')]
        day, ident, ident_long = meta_string.split(' ')
        story_string = sentence[sentence.find('\n'):].replace('\n', '')
        #Combine info into a dictionary
        story_info = {'day': day, 'id': ident, 'id_long': ident_long,
                      'story': story_string}
        #Add the new dict to the events dict with the ID as the key
        event_dict[ident] = story_info

def get_np(tree, event_dict):
    noun_phrases = []
    for sub in tree.subtrees(filter=lambda x: x.node == 'NP'):
        nouns = []
        for i in xrange(len(sub)):
            nouns.append(sub[i][0])
        nouns = ' '.join(nouns)
        noun_phrases.append(nouns)
    event_dict[key]['noun_phrases'] = noun_phrases


def get_vp(tree, event_dict):
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
    event_dict[key]['verb_phrases'] = verb_phrases


def parse_sent(sent, event_dict, key, input_chunker):
    #Tokenize the words
    toks = nk.word_tokenize(sent)
    #Part-of-speech tag the tokens
    tags = nk.pos_tag(toks)
    chunker = TagChunker(input_chunker)
    #Use chunker to chunk the tagged words and combine into a tree
    tree = chunker.parse(tags)
    event_dict[key]['tagged'] = tags
    event_dict[key]['sent_tree'] = tree
    get_np(tree, event_dict)
    get_vp(tree, event_dict)


if __name__ == '__main__':
    events = {}
    print 'Reading in data...'
    sentence_file = sys.argv[1]
    read_data(sentence_file, events)
    print 'Parsing sentences...'
    ubt_chunker = create_chunkers()
    for key in events:
        parse_sent(events[key]['story'], events, key, ubt_chunker)
    for event in events:
        print '=======================\n'
        print 'event id: {}\n'.format(event)
        print 'POS tagged sent:\n {}\n'.format(events[event]['tagged'])
        print 'NP tagged sent:\n {}\n'.format(events[event]['sent_tree'])
        print 'Noun phrases: \n {}\n'.format(events[event]['noun_phrases'])
        print 'Verb phrases: \n {}\n'.format(events[event]['verb_phrases'])
