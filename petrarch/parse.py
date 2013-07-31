from corenlp import StanfordCoreNLP

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
            output_dict[key]['word_info'] = (result['sentences'][0]
                                             ['words'])
            output_dict[key]['dependencies'] = (result['sentences'][0]
                                                ['dependencies'])
        else:
            print 'More than one sentence.'

    return output_dict
