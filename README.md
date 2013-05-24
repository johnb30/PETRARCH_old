PETRARCH
========

Repository for the devlopment of the Python-language successor to the TABARAI
event-data coding program. 

###Current Usage

Current options are:

command: parse

- -i : Input file
- -u : Geonames username
- -P : Boolean argument indicating whether to run postprocessing. 
- -h : help

The command as of now should look (something) like:

    python petrarch.py parse -i SENTENCE_FILE -u USERNAME -p

##NOTE

The setup.py file is currently experimental and is in no way, shape, or form
guaranteed to actually install the program in a proper manner. There's also
no clear reason to install the program at this point.
