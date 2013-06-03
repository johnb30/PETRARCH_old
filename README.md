PETRARCH
========

[![Build Status](https://travis-ci.org/eventdata/PETRARCH.png?branch=master)](https://travis-ci.org/eventdata/PETRARCH)

Repository for the development of the Python-language successor to the TABARI
event-data coding program. 

###Current Usage

Current options are:

command: parse

- -i : Input file
- -u : Geonames username. Optional.
- -F : Boolean argument indicating whether to run feature extraction. Optional.
- -G : Boolean argument indicating whether to run geolocation. Username required. Optional.
- -h : help

The command as of now should look (something) like:

    python petrarch.py parse -i SENTENCE_FILE -u USERNAME -G -F

####Tests

To run the (single) test, just navigate to the toplevel of the directory
and run `nosetests`. 

##NOTE

The setup.py file seems to work now. Since this software is in sub-alpha 
development installing the program probably isn't the best idea. If you do
install it, the use of a temporary virtual environment is advisable. Once
installed, it should be possible to run the program using the following
command:

    petrarch parse -i SENTENCE_FILE -u USERNAME -G -F
