import dateutil.parser
import postprocess
import argparse
import parse
import glob
import sys
import os
from ConfigParser import ConfigParser
from datetime import datetime


def _get_data(path):
    """Private function to get the absolute path to the installed files."""
    cwd = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(cwd, 'data', path)


def read_data(filepath):
    """
    Function to read in a file of news stories. Expects stories formatted
    in the traditional TABARI format. Adds each sentence, along with the
    meta data, to a dictionary.

    Parameters
    ----------

    filepath : String
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
        day = dateutil.parser.parse(day)
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
                               required=True)
    parse_command.add_argument('-o', '--output',
                               help='File to write parsed events',
                               required=True)
    parse_command.add_argument('-u', '--username',
                               help="geonames.org username", default=None)
    parse_command.add_argument('-G', '--geolocate', action='store_true',
                               default=False, help="""Whether to geolocate
                               events. Defaults to False""")
    parse_command.add_argument('-F', '--features', action='store_true',
                               default=False,
                               help="""Whether to extract features from
                               sentence. Defaults to False""")

    parallel_command = sub_parse.add_parser('parallel_parse',
                                            help="""Command to run the
                                            PETRARCH parser in parallel.""",
                                            description="""Command to run the
                                            PETRARCH parser in parallel.""")
    parallel_command.add_argument('-i', '--inputs',
                                  help="""File, or directory of files, to
                                  parse.""", required=True)
    parallel_command.add_argument('-o', '--output', help="""File to write
                                  parsed events""", required=True)
    parallel_command.add_argument('-u', '--username',
                                  help="geonames.org username", default=None)
    parallel_command.add_argument('-G', '--geolocate', action='store_true',
                                  default=False, help="""Whether to geolocate
                                  events. Defaults to False""")
    parallel_command.add_argument('-F', '--features', action='store_true',
                                  default=False, help="""Whether to extract
                                  features from sentence. Defaults to False""")
    parallel_command.add_argument('-n', '--n_cores', type=int, default=-1,
                                  help="""Number of cores to use for parallel
                                  processing. parse_command to -1 for all
                                  cores""")

    args = aparse.parse_args()
    return args


def parse_config():
    """Function to parse the config file for PETRARCH."""
    config_file = glob.glob('config.ini')
    parser = ConfigParser()
    print os.path.dirname(sys.executable)
    if config_file:
        print 'Found a config file in working directory.'
        parser.read(config_file)
        try:
            cwd = os.getcwd()
            actors_file = parser.get('Dictionary Files', 'actors')
            verbs_file = parser.get('Dictionary Files', 'verbs')
            actors_file = os.path.join(cwd, 'dictionaries', actors_file)
            verbs_file = os.path.join(cwd, 'dictionaries', verbs_file)
            direct = parser.get('StanfordNLP', 'stanford_dir')
            stanfordnlp = os.path.expanduser(direct)
            return actors_file, verbs_file, stanfordnlp
        except Exception, e:
            print 'Problem parsing config file. {}'.format(e)
    else:
        cwd = os.path.abspath(os.path.dirname(__file__))
        config_file = os.path.join(cwd, 'default_config.ini')
        parser.read(config_file)
        print 'No config found. Using default.'
        try:
            actors_file = parser.get('Dictionary Files', 'actors')
            verbs_file = parser.get('Dictionary Files', 'verbs')
            actors_file = os.path.join(cwd, 'dictionaries', actors_file)
            verbs_file = os.path.join(cwd, 'dictionaries', verbs_file)
            direct = parser.get('StanfordNLP', 'stanford_dir')
            stanfordnlp = os.path.expanduser(direct)
            return actors_file, verbs_file, stanfordnlp
        except Exception, e:
            print 'Problem parsing config file. {}'.format(e)


def main():
    """Main function"""
    actors, verbs, stanford_dir = parse_config()

    cli_args = parse_cli_args()
    cli_command = cli_args.command_name
    inputs = cli_args.inputs
    out_path = cli_args.output
    username = cli_args.username
    if cli_command == 'parallel_parse':
        cpus = cli_args.n_cores
    geo_boolean = cli_args.geolocate
    feature_boolean = cli_args.features

    if cli_command == 'parse':
        print 'Reading in sentences...{}:{}.{}'.format(datetime.now().hour,
                                                       datetime.now().minute,
                                                       datetime.now().second)
        events = read_data(inputs)

        print 'Parsing sentences...{}:{}.{}'.format(datetime.now().hour,
                                                    datetime.now().minute,
                                                    datetime.now().second)
        results = parse.parse(events, stanford_dir)
        for key in results:
            events[key].update(results[key])
        del results
        print 'Done processing...{}:{}.{}'.format(datetime.now().hour,
                                                  datetime.now().minute,
                                                  datetime.now().second)

        if geo_boolean or feature_boolean:
            print 'Feature extraction...{}:{}.{}'.format(datetime.now().hour,
                                                         datetime.now().minute,
                                                         datetime.now().second)
            postprocess.process(events, username, geo_boolean, feature_boolean)
            print 'Done...{}:{}.{}'.format(datetime.now().hour,
                                           datetime.now().minute,
                                           datetime.now().second)
    elif cli_command == 'parallel_parse':
        import pp

        print 'Reading in sentences...{}:{}.{}'.format(datetime.now().hour,
                                                       datetime.now().minute,
                                                       datetime.now().second)
        events = read_data(inputs)

        ppservers = ()
        if cpus == -1:
            job_server = pp.Server(ppservers=ppservers)
        else:
            job_server = pp.Server(cpus, ppservers=ppservers)

        chunks = list()

        if len(events) % int(len(events) / (job_server.get_ncpus())) == 1:
            chunk_size = int(len(events) / (job_server.get_ncpus()-1))
        else:
            chunk_size = int(len(events) / (job_server.get_ncpus()))

        for i in xrange(0, len(events), chunk_size):
            chunks.append(dict(events.items()[i:i+chunk_size]))

        print 'Parsing sentences...{}:{}.{}'.format(datetime.now().hour,
                                                    datetime.now().minute,
                                                    datetime.now().second)
        jobs = [job_server.submit(parse.parse, (chunk, stanford_dir,), (),
                                  ("corenlp", "nltk.tree", "utilities",))
                for chunk in chunks]

        results = list()
        for job in jobs:
            results.append(job())

        for chunk in results:
            for key in chunk:
                events[key].update(chunk[key])
        del results
        print 'Done processing...{}:{}.{}'.format(datetime.now().hour,
                                                  datetime.now().minute,
                                                  datetime.now().second)

        if geo_boolean or feature_boolean:
            print 'Feature extraction...{}:{}.{}'.format(datetime.now().hour,
                                                         datetime.now().minute,
                                                         datetime.now().second)
            postprocess.process(events, username, geo_boolean, feature_boolean)
            print 'Donel..{}:{}.{}'.format(datetime.now().hour,
                                           datetime.now().minute,
                                           datetime.now().second)
    else:
        print 'Please enter a valid command!'

    event_output = str()

    print 'Writing the events to file...'
    for event in events:
        event_output += '\n=======================\n\n'
        event_output += 'event id: {}\n\n'.format(event)
        try:
            event_output += 'Word info:\n {}\n\n'.format(events[event]['word_info'])
            event_output += 'Parse tree:\n {}\n\n'.format(events[event]['parse_tree'])
            event_output += 'Word dependencies:\n {}\n\n'.format(events[event]['dependencies'])
        except KeyError:
            print 'There was a key error'
            print events[event].keys()
            print events[event]['story']
        if 'corefs' in events[event].keys():
            event_output += 'Coref info:\n {}\n'.format(events[event]['corefs'])
        if 'coref_tree' in events[event].keys():
            try:
                event_output += 'Coref tree:\n {}\n\n'.format(events[event]['coref_tree'])
            except Exception, e:
                print 'There was an error for key {}: {}'.format(event, e)
                print events[event]['coref_tree']
                pass
        try:
            event_output += '\nGeolocate: \n {}, {}\n'.format(events[event]['lat'],
                                                              events[event]['lon'])
        except KeyError:
            pass
        try:
            event_output += 'Feature extract: \n {}\n'.format(events[event]['num_involved'])
        except KeyError:
            pass

    with open(out_path, 'w') as f:
        f.write(event_output)


if __name__ == '__main__':
    main()
