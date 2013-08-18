import copy
import corenlp
import nltk.tree
import utilities


def parse(event_dict, stanford_dir):
    """Function to parse single-sentence input using StanfordNLP.

    Parameters
    ----------

    event_dict : Dictionary
                Dictionary of that contains the events and text. Excepts story
                IDs as keys with an additional dictionary as the value. Within
                each story ID value dictionary should be an item named 'story'.

    stanford_dir: String.
                    Directory that contains the StanfordNLP files.

    Returns
    --------

    output_dict : Dictionary
                  Dictionary with story ID as key and a dictionary as the
                  value. Within the value dictionary are keys 'parse_tree',
                  'word_info', 'dependencies', and, optionally, 'corefs'.

    """
    output_dict = dict()
    corenlp_dir = stanford_dir
    core = corenlp.StanfordCoreNLP(corenlp_dir)
    for key in event_dict:
        result = core.raw_parse(event_dict[key]['story'])
        output_dict[key] = dict()
        if len(result['sentences']) == 1:
            sent_info = {0: dict()}
            sent_info[0]['parse_tree'] = (result['sentences'][0]
                                              ['parsetree'])
            sent_info[0]['word_info'] = (result['sentences'][0]['words'])
            sent_info[0]['dependencies'] = (result['sentences'][0]
                                                ['dependencies'])

            parsed = nltk.tree.Tree(result['sentences'][0]['parsetree'])
            sent_info[0].update(utilities._get_np(parsed))
            sent_info[0].update(utilities._get_vp(parsed))
            del parsed

            if 'coref' in result:
                corefs = result['coref']

                ordered_corefs = {0: {'corefs': corefs, 'shift': 0}}

                coref_tree = copy.deepcopy(sent_info[0]['parse_tree'])
                coref_tree, errors = utilities.coref_replace(coref_tree,
                                                             result['coref'])
                if not any(errors):
                    output_dict[key]['coref_tree'] = coref_tree
        if output_dict[key]['coref_tree'] == output_dict[key]['parse_tree']:
            del output_dict[key]['coref_tree']
        else:
            print """Key {} is longer than one sentence, passing. Please check
                  the input format if you would like this key to be parsed!"""
            pass

    return output_dict

def batch_parse(text_dir, stanford_dir):
    """Function to parse sentences using StanfordNLP.

    Parameters
    ----------

    text_dir: String.
                Directory of text files to parse using StanfordNLP.

    stanford_dir: String.
                    Directory that contains the StanfordNLP files.

    Returns
    --------

    output_dict : Dictionary
                  Dictionary with filename as key and a dictionary as the
                  value. Within the value dictionary are keys 'parse_tree',
                  'word_info', 'dependencies', and, optionally, 'corefs'.

    """
    output_dict = dict()
    results = corenlp.batch_parse(text_dir, stanford_dir)
    for index in xrange(len(results)):
        name = results[index]['file_name']
        num_sents = len(results[index]['sentences'])
        sent_info = dict()
        for i, content in enumerate(results[index]['sentences']):
            sent_info[i] = dict()
            sent_info[i]['parse_tree'] = (content['parsetree'])
            sent_info[i]['word_info'] = (content['words'])
            sent_info[i]['dependencies'] = (content['dependencies'])

            parsed = nltk.tree.Tree(content['parsetree'])
            sent_info[i].update(utilities._get_np(parsed))
            sent_info[i].update(utilities._get_vp(parsed))
            del parsed

        if 'coref' in results[index].keys():
            corefs = results[index]['coref']

            ordered_corefs = dict()
            for i in xrange(num_sents):
                ordered_corefs[i] = {'corefs': list(), 'shift': 0}
            for i in xrange(len(corefs)):
                for x in xrange(len(corefs[i])):
                    pronoun_sent = corefs[i][x][0][1]
                    ordered_corefs[pronoun_sent]['corefs'].append(corefs[i][x])
        else:
            corefs = None

