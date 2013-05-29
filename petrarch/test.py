import os
import petrarch
import parse
import pickle

def test_main():
    cwd = os.path.abspath(os.path.dirname(__file__))
    test_sent = os.path.join(cwd, 'test_files', 'test_sentences.txt')
    test_output = open(os.path.join(cwd, 'test_files', 'test_output.txt')).read()
    test_output = test_output.replace('\n', '')
    petrarch._check_reqs()
    chunker = petrarch._get_chunker('ubt_chunker_trained.pickle')
    ubt_chunker = pickle.load(open(chunker))
    events = petrarch.read_data(test_sent)
    username = None
    parse.parse(events, ubt_chunker, username)
    output = ""
    for event in events:
        output += '=======================\n\n'
        output += 'event id: {}\n'.format(event)
        output += 'POS tagged sent:\n {}\n\n'.format(events[event]['tagged'])
        output += 'NP tagged sent:\n {}\n\n'.format(events[event]['sent_tree'])
        output += 'Noun phrases: \n {}\n\n'.format(events[event]['noun_phrases'])
        output += 'Verb phrases: \n {}\n\n'.format(events[event]['verb_phrases'])
        try:
            output += 'Geolocate: \n {}, {}\n\n'.format(events[event]['lat'],
                                                    events[event]['lon'])
        except KeyError:
            pass
        try:
            output += 'Feature extract: \n {}\n\n'.format(events[event]['num_involved'])
        except KeyError:
            pass 
    output = output.replace('\n', '')

    assert test_output == output

if __name__ == '__main__':
    test_main()
