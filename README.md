Python Engine for Text Resolution And Related Coding Hierarchy (PETRARCH)
========

Repository for the development of the Python-language successor to the [TABARI](http://eventdata.psu.edu/software.dir/tabari.html)
event-data coding program. You can find the documentation for PETRARCH [here](http://eventdata.readthedocs.org/). You can read more about event data [here](http://eventdata.psu.edu/).

### Current Usage

We seem to have settled on a few core functions at this point. Each function 
is designed to do a slightly different task.

#####`parse`

The `parse` command is the key functionality of PETRARCH. The expected input
is the standard TABARI-formatted lead sentences. If the input is longer than
one sentence, then the program will skip it. To run the `parse` command:

    python petrarch.py parse -i SENTENCE_FILE -o output.txt 

#####`parallel_parse`

The `parallel_parse` command does the same thing as the `parse` command,
but makes use of multiple cores. This command requires the Parallel Python
library (`pip install pp`). To run:

    python petrarch.py parallel_parse -i SENTENCE_FILE -o output.txt

#####`batch_parse`

The `batch_parse` command is designed to take as input a directory of article-length
news stories, and parse them in the same manner as the single sentences in the other
commands. The main difference between `batch_parse` and the other parse commands is
the manner in which the program interacts with StanfordNLP. To run the command:

    python petrarch.py batch_parse -i ~/sentence_directory -o output.txt
