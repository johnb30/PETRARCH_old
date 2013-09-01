import corenlp
import nltk.tree
import utilities


def parse(event_dict, stanford_dir):
    """Function to parse single-sentence input using StanfordNLP. The function
    parses the input, and performs pronoun coreferencing where appropriate. If
    the input is longer than one setence as determined by StanfordNLP, the
    program will pass on that input.

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
                    Output dictionary format is of the following form. The
                    main level has keys of event IDs, e.g., AFPN-0301-01, with
                    dictionaries as values. At this stage, the value dictionary
                    has one key, `sent_info`, which has another dictionary as
                    the value. Within the `sent_info` dictionary are keys
                    `sents` and `coref_info`. Each has dictionaries as their
                    values. The `sents` dictionary has integers as keys, which
                    represent the different sentences within a text input. Each
                    individual sentence dictionary contains the keys
                    `parse_tree` (nltk.tree), `dependencies` (list),
                    `np_words` (list), `word_info` (list),
                    `verb_phrases` (list), `vp_words` (list), and
                    `noun_phrases` (list). The `coref_info` dictionary has a
                    similar structure, with each sentence having its own
                    individual dictionary with keys `shift` (integer) and
                    `corefs` (list). Given this, the final structure of the
                    output resembles:
                    {'event_id': {'sent_info': {'sents': {0: {'parse_tree': tree
                                                              'dependencies': list}
                                                          1: {...}}
                                                'coref_info': {0: {'shift': 0
                                                               'corefs': []}}
                                                }}}
    """
    output_dict = dict()
    corenlp_dir = stanford_dir
    core = corenlp.StanfordCoreNLP(corenlp_dir)
    for key in event_dict:
        result = core.raw_parse(event_dict[key]['story'])
        if len(result['sentences']) == 1:
            output = _parse_sents(key, result)
            output_dict.update(output)
            if 'coref' in result:
                utilities.coref_replace(output_dict, key)
        else:
            print """Key {} is longer than one sentence, passing. Please check
the input format if you would like this key to be parsed!""".format(key)
            pass

    return output_dict


def batch_parse(text_dir, stanford_dir):
    """Function to parse multi-sentence input using StanfordNLP in batch mode.
    The function parses the input, and performs pronoun coreferencing where
    appropriate. Coreferences are linked across sentences.

    Parameters
    ----------

    text_dir: String.
                Directory of text files to parse using StanfordNLP.

    stanford_dir: String.
                    Directory that contains the StanfordNLP files.

    Returns
    --------

    output_dict : Dictionary
                    Output dictionary format is of the following form. The
                    main level has keys of story IDs, e.g., story1.txt, with values
                    of dictionaries. At this stage, the value dictionary has
                    one key, `sent_info`, which has another dictionary as
                    the value. Within the `sent_info` dictionary are keys
                    `sents` and `coref_info`. Each has dictionaries as their
                    values. The `sents` dictionary has integers as keys, which
                    represent the different sentences within a text input. Each
                    individual sentence dictionary contains the keys
                    `parse_tree` (nltk.tree), `dependencies` (list),
                    `np_words` (list), `word_info` (list),
                    `verb_phrases` (list), `vp_words` (list), and
                    `noun_phrases` (list). The `coref_info` dictionary has a
                    similar structure, with each sentence having its own
                    individual dictionary with keys `shift` (integer) and
                    `corefs` (list). Given this, the final structure of the
                    output resembles:
                    {'event_id': {'sent_info': {'sents': {0: {'parse_tree': tree
                                                              'dependencies': list}
                                                          1: {...}}
                                                'coref_info': {0: {'shift': 0
                                                               'corefs': []}}
                                                }}}

    """
    output_dict = dict()
    results = corenlp.batch_parse(text_dir, stanford_dir)
    for index in xrange(len(results)):
        parsed = results[index]
        name = parsed['file_name']
        output = _parse_sents(name, parsed)
        output_dict.update(output)
    for article in output_dict:
        utilities.coref_replace(output_dict, article)

    return output_dict


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
