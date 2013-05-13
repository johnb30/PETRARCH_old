import nltk as nk
import itertools
import sys
from joblib import Parallel, delayed

#Chunker code pulled from
#http://streamhacker.wordpress.com/2009/02/23/chunk-extraction-with-nltk/


def conll_tag_chunks(chunk_sents):
    #Parse the training data for the chunker
    tag_sents = [nk.chunk.tree2conlltags(tree) for tree in chunk_sents]
    return [[(t, c) for (w, t, c) in chunk_tags] for chunk_tags in tag_sents]


def create_chunkers():
    #Get training data for chunker
    train_sents = nk.corpus.conll2000.chunked_sents('train.txt')
    train_chunks = conll_tag_chunks(train_sents)

    #Training the chunker
    u_chunker = nk.tag.UnigramTagger(train_chunks)
    ub_chunker = nk.tag.BigramTagger(train_chunks, backoff=u_chunker)
    ubt_chunker = nk.tag.TrigramTagger(train_chunks, backoff=ub_chunker)

    return ubt_chunker


class TagChunker(nk.chunk.ChunkParserI):
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
        return nk.chunk.conllstr2tree('\n'.join(lines))


class Parser():
    def __init__(self, filepath, chunker):
        self.event_dict = dict()
        self.filepath = filepath
        self.input_chunker = chunker

    def read_data(self):
        """
        Function to read in a file of news stories. Expects stories formatted
        in the traditional TABARI format. Adds each sentence, along with the
        meta data, to a dictionary.

        """
        data = open(self.filepath, 'r').read()
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
            self.event_dict[ident] = story_info

    def get_np(self, tree, key):
        """
        Function to extract noun phrases from a parse tree of any given
        sentence.

        Inputs
        ------

        tree : parse tree for a particular sentence. nk tree object.

        key : key for the event being parsed. Used to add the noun phrase
        data to the events dictionary. String.

        Note
        ----

        Function adds a list of noun phrases to the events dictionary.

        """
        noun_phrases = []
        for sub in tree.subtrees(filter=lambda x: x.node == 'NP'):
            nouns = []
            for i in xrange(len(sub)):
                nouns.append(sub[i][0])
            nouns = ' '.join(nouns)
            noun_phrases.append(nouns)
        self.event_dict[key]['noun_phrases'] = noun_phrases

    def get_vp(self, tree, key):
        """
        Function to extract verb phrases from a parse tree of any given
        sentence.

        Inputs
        ------

        tree : parse tree for a particular sentence. nk tree object.

        key : key for the event being parsed. Used to add the noun phrase
        data to the events dictionary. String.

        Note
        ----

        Function adds a list of tuples to the events dictionary. The tuples
        are of the form (verb, noun phrase), where the noun phrase is one that
        immediately follows the verb.

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
        self.event_dict[key]['verb_phrases'] = verb_phrases

    def parse_sent(self, sent, key):
        """
        Function to parse a given sentence. Tokenizes, POS tags, and chunks a
        given sentence, along with extracting noun and verb phrases.

        Inputs
        ------

        sent : sentence to be parsed. String.

        key : key of the event used to access the event from the events
              dictionary. String.

        Note
        ----

        Adds tagged and parsed sentence to the events dictionary, along with
        the extracted noun and verb phrases.

        """
        #Tokenize the words
        toks = nk.word_tokenize(sent)
        #Part-of-speech tag the tokens
        tags = nk.pos_tag(toks)
        chunker = TagChunker(self.input_chunker)
        #Use chunker to chunk the tagged words and combine into a tree
        tree = chunker.parse(tags)
        self.event_dict[key]['tagged'] = tags
        self.event_dict[key]['sent_tree'] = tree
        self.get_np(tree, key)
        self.get_vp(tree, key)

    def parse(self):
        """
        Function that calls the `parse_sent` function in parallel. Helper
        function to make calling the necessary functions cleaner.

        Note
        ----

        This is the function that should be called directly in a script.

        """
        self.read_data()
#TODO: Parallel doesn't work because class methods aren't pickle-able.
#TODO: there are some things that can help, i.e., `copy_reg`, or just break
#apart the class somehow.
#        Parallel(n_jobs=3)(delayed(self.parse_sent)
#                          (sent=self.event_dict[key]['story'], key=key)
#                          for key in self.event_dict)
        for key in self.event_dict:
            self.parse_sent(self.event_dict[key]['story'], key)

        return self.event_dict

if __name__ == '__main__':
    print 'Reading in data...'
    sentence_file = sys.argv[1]
    ubt_chunker = create_chunkers()
    parser = Parser(sentence_file, ubt_chunker)
    print 'Parsing sentences...'
    events = parser.parse()
    for event in events:
        print '=======================\n'
        print 'event id: {}\n'.format(event)
        print 'POS tagged sent:\n {}\n'.format(events[event]['tagged'])
        print 'NP tagged sent:\n {}\n'.format(events[event]['sent_tree'])
        print 'Noun phrases: \n {}\n'.format(events[event]['noun_phrases'])
        print 'Verb phrases: \n {}\n'.format(events[event]['verb_phrases'])
