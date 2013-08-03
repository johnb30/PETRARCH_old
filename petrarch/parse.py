from corenlp import StanfordCoreNLP
from nltk.tree import Tree

def parse(event_dict, stanford_dir, cores):
    output_dict = dict()
    corenlp_dir = stanford_dir
    corenlp = StanfordCoreNLP(corenlp_dir)
    print 'setup S-NLP...running sentences...'
    for key in event_dict:
        result = corenlp.raw_parse(event_dict[key]['story'])
        print 'Processed key: {}'.format(key)
        output_dict[key] = dict()
        if 'coref' in result:
            output_dict[key]['corefs'] = result['coref']
        if len(result['sentences']) == 1:
            output_dict[key]['parse_tree'] = (result['sentences'][0]
                                              ['parsetree'])
            tree = Tree(result['sentences'][0]['parsetree']
            output_dict[key]['word_info'] = (result['sentences'][0]
                                             ['words'])
            output_dict[key]['dependencies'] = (result['sentences'][0]
                                                ['dependencies'])
            output_dict[key].update(_get_np(tree))
            output_dict[key].update(_get_vp(tree))
        else:
            print 'More than one sentence.'

    return output_dict

def _get_np(parse_tree):
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree(filter=lambda x: s.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)
    
    output['noun_phrases'] = phrases
    output['np_words'] = words

    return output

def _get_vp(parse_tree):
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree(filter=lambda x: s.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)

    output['verb_phrases'] = phrases
    output['vp_words'] = words

    return output
