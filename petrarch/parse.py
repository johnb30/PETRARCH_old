import corenlp
import nltk.tree 

def parse(event_dict, stanford_dir):
    output_dict = dict()
    corenlp_dir = stanford_dir
    core = corenlp.StanfordCoreNLP(corenlp_dir)
    for key in event_dict:
        result = core.raw_parse(event_dict[key]['story'])
        output_dict[key] = dict()
        if 'coref' in result:
            output_dict[key]['corefs'] = result['coref']
        if len(result['sentences']) == 1:
            output_dict[key]['parse_tree'] = (result['sentences'][0]
                                              ['parsetree'])
            parsed = nltk.tree.Tree(result['sentences'][0]['parsetree'])
            output_dict[key]['word_info'] = (result['sentences']
                                             [0]['words'])
            output_dict[key]['dependencies'] = (result['sentences'][0]
                                                ['dependencies'])
            #output_dict[key].update(_get_np(parsed))
            #output_dict[key].update(_get_vp(parsed))

    return output_dict

def _get_np(parse_tree):
    print type(parse_tree)
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree(filter=lambda x: x.node == 'NP'):
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
    for node in parse_tree(filter=lambda x: x.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)

    output['verb_phrases'] = phrases
    output['vp_words'] = words

    return output
