import parse
import argparse
import pickle
import nltk as nk
import os


def _get_chunker(path):
    """Private function to get the absolute path to the installed files."""
    cwd = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(cwd, 'data', path)


def _check_reqs():
    """Private function to check whether the POS tagger is available. If not,
    downloads the tagger"""
    #TODO: This is a temporary, hackish work around. This should be moved to
    #the setup.py file at some point.
    try:
        nk.data.load(nk.tag._POS_Tagger)
    except LookupError:
        nk.download('maxent_treebank_pos_tagger')


def read_data(filepath):
    """
    Function to read in a file of news stories. Expects stories formatted
    in the traditional TABARI format. Adds each sentence, along with the
    meta data, to a dictionary.

    Parameters
    ----------

    filepath: String.
              Filepath of the file containing the sentence to be parsed.

    """
    event_dict = dict()
    data = open(filepath, 'r').read()
    sentences = data.split('\n\n')
    for sentence in sentences:
        #Strings are weird, so split into meta string, which contains meta
        #info and story part of the string
        meta_string = sentence[:sentence.find('\n')]
        day, ident = meta_string.split()[:2]
        story_string = sentence[sentence.find('\n'):].replace('\n', '')
        #Combine info into a dictionary
        story_info = {'day': day, 'id': ident, 'story': story_string}
        #Add the new dict to the events dict with the ID as the key
        event_dict[ident] = story_info

    return event_dict


def parse_cli_args():
    """Function to parse the command-line arguments for PETRARCH."""
    __description__ = """
PETRARCH
(eventdata.psu.edu) (v. 0.01)
    """
    aparse = argparse.ArgumentParser(prog='PETRARCH',
                                     description=__description__)

    sub_parse = aparse.add_subparsers(dest='command_name')
    parse_command = sub_parse.add_parser('parse', help="""Command to run the
                                         PETRARCH parser.""",
                                         description="""Command to run the
                                         PETRARCH parser.""")
    parse_command.add_argument('-i', '--inputs',
                               help='File, or directory of files, to parse.',
                               default=None)
    parse_command.add_argument('-o', '--output',
                               help='File to write parsed events',
                               default=None)
    parse_command.add_argument('-u', '--username',
                               help="geonames.org username", default=None)
    parse_command.add_argument('-P', '--postprocess', help="""Whether post
                               processing, such as geolocation and feature
                               extraction, should occur. Default False.""",
                               default=False, action='store_true')
#These will be used as the program develops further.
#    parse_command.add_argument('-g', '--geolocate', action='store_true',
#                          default=False, help="""Whether to geolocate events.
#                          parse_command to False""")
#    parse_command.add_argument('-f', '--features', action='store_true',
#                          default=False,
#                          help="""Whether to extract features from sentence.
#                          parse_command to False""")
    parse_command.add_argument('-n', '--n_cores', type=int, default=-1,
                               help="""Number of cores to use for parallel
                               processing. parse_command to -1 for all
                               cores""")

    temp_command = sub_parse.add_parser('temp', help="""Placeholder.""",
                                        description="""Placeholder.""")
    args = aparse.parse_args()
    return args


def main():
    """Main function"""
    cli_args = parse_cli_args()
    cli_command = cli_args.command_name
    inputs = cli_args.inputs
    out_path = cli_args.output
    username = cli_args.username
    post_proc = cli_args.postprocess
    _check_reqs()
    if cli_command == 'parse':
        print 'Reading in data...'
        chunk = get_chunker('ubt_chunker_trained.pickle')
        ubt_chunker = pickle.load(open(chunk))
        print 'Parsing sentences...'
        events = read_data(inputs)
        parse.parse(events, ubt_chunker, username, post_proc)
        for event in events:
            print '=======================\n'
            print 'event id: {}\n'.format(event)
            print 'POS tagged sent:\n {}\n'.format(events[event]['tagged'])
            print 'NP tagged sent:\n {}\n'.format(events[event]['sent_tree'])
            print 'Noun phrases: \n {}\n'.format(events[event]['noun_phrases'])
            print 'Verb phrases: \n {}\n'.format(events[event]['verb_phrases'])
            try:
                print 'Geolocate: \n {}, {}\n'.format(events[event]['lat'],
                                                      events[event]['lon'])
            except KeyError:
                pass
            try:
                print 'Feature extract: \n {}\n'.format(events[event]['num_involved'])
            except KeyError:
                pass
    else:
        print 'Please enter a valid command!'


if __name__ == '__main__':
    main()
