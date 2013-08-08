import utilities
import corenlp
import nltk.tree 

def parse(event_dict, stanford_dir):
    """Function to parse sentences using StanfordNLP.

    Parameters
    ----------

    event_dict : Dictionary
                Dictionary of that contains the events and text. Excepts story
                IDs as keys with an additional dictionary as the value. Within
                each story ID value dictionary should be an item named 'story'.

    Returns
    --------

    output_dict : Dictionary
                  Dictionary with story ID as key and a dictionary as the value.
                  Within the value dictionary are keys 'parse_tree', 'word_info',
                  'dependencies', and, optionally, 'corefs'.
 
    """
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
            output_dict[key].update(utilities._get_np(parsed))
            output_dict[key].update(utilities._get_vp(parsed))

    return output_dict
