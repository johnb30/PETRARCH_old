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
        print '\nProcessing key {}'.format(key)
        result = core.raw_parse(event_dict[key]['story'])
        if len(result['sentences']) == 1:
            output = _parse_sents(key, result)
            output_dict.update(output)
            if 'coref' in result:
                utilities.coref_replace2(output_dict, key)
#                coref_tree = copy.deepcopy(output_dict[key]['parse_tree'])
#                coref_tree, errors = utilities.coref_replace(coref_tree,
#                                                             result['coref'])
#                if not any(errors):
#                    output_dict[key]['coref_tree'] = coref_tree
#        if output_dict[key]['coref_tree'] == output_dict[key]['parse_tree']:
#            del output_dict[key]['coref_tree']
        else:
            print """Key {} is longer than one sentence, passing. Please check
                  the input format if you would like this key to be
                  parsed!""".format(key)
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
        parsed = results[index]
        name = parsed['file_name']
        output_dict = _parse_sents(output_dict, name, parsed)


def _parse_sents(key, results):
    sent_output = dict()
    num_sents = len(results['sentences'])
    sent_info = dict()
    for i, content in enumerate(results['sentences']):
        sent_info[i] = dict()
        sent_info[i]['parse_tree'] = (content['parsetree'])
        sent_info[i]['word_info'] = (content['words'])
        sent_info[i]['dependencies'] = (content['dependencies'])

        parsed = nltk.tree.Tree(content['parsetree'])
        sent_info[i].update(utilities._get_np(parsed))
        sent_info[i].update(utilities._get_vp(parsed))
        del parsed
    sent_output[key] = {'sent_info': {'sents': sent_info}}

    if 'coref' in results.keys():
        corefs = results['coref']
        ordered_corefs = dict()
        for i in xrange(num_sents):
            ordered_corefs[i] = {'corefs': list(), 'shift': 0,
                                 'errors': list()}
        for i in xrange(len(corefs)):
            for x in xrange(len(corefs[i])):
                pronoun_sent = corefs[i][x][0][1]
                ordered_corefs[pronoun_sent]['corefs'].append(corefs[i][x])
        sent_output[key]['sent_info']['coref_info'] = ordered_corefs

    return sent_output
