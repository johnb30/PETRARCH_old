class ReadDictionaries():
    def __init__(self, actors, verbs):
        self.actors = actors
        self.verbs = verbs
        self.verb_dict = {}
        self.actor_dict = {}

    def read_verb_dictionary(self):
    # Verb lists
    # 1. True: primary form; False: next item points to primary form
    # 2. Code
    # remainder: 3-tuples of lower/upper pattern and code
        fin = open(self.verbs, 'r')

        theverb = ''
        ka = 0
        for line in fin:  # loop through the file
            part = line.partition('[')
            verb = part[0].strip() + ' '
            scr = part[2].partition(']')
            code = scr[0]
        #print verb, code
            if verb[0] == '-':
#			print 'RVD-1',verb
                if not hasforms:
                    self._make_verb_forms()
                    hasforms = True
                targ = verb[1:].partition('*')
                highpat = self._make_phrase_list(targ[0].lstrip())
#			print 'RVD-2',highpat
                highpat.reverse()
                lowphrase = targ[2].rstrip()
                if len(lowphrase) == 0:
                    lowpat = []
                else:
                    lowpat = [targ[2][0]]   # start with connector
                    loclist = self._make_phrase_list(lowphrase[1:])
                    lowpat.extend(loclist[:-1])   # don't need the final blank
#			print 'RVD-3',lowpat
                self.verb_dict[theverb].append([highpat, lowpat, code])
            elif verb[0] == '{':
                self._get_verb_forms()
                hasforms = True
            else:
#		if theverb != '': print '::', theverb, verb_dict[theverb]
                theverb = verb
                self.verb_dict[verb] = [True, code]
                hasforms = False
                ka += 1   # counting primary verbs
#			if ka > 10: break

    def _make_verb_forms(self):
    # create the regular forms of a verb
        global theverb
        vroot = theverb[:-1]
        vscr = vroot + "S "
        self.verb_dict[vscr] = [False, theverb]
        if vroot[-1] == 'E':  # root ends in 'E'
            vscr = vroot + "D "
            self.verb_dict[vscr] = [False, theverb]
            vscr = vroot[:-1] + "ING "
        else:
            vscr = vroot + "ED "
            self.verb_dict[vscr] = [False, theverb]
            vscr = vroot + "ING "
        self.verb_dict[vscr] = [False, theverb]

    def _make_phrase_list(thepat):
    # converts a pattern phrase into a list of alternating words and connectors
        if len(thepat) == 0:
            return []
        phlist = []
        start = 0
        maxlen = len(thepat) + 1  # this is just a telltail
        while start < len(thepat):  # break phrase on ' ' and '_'
            spfind = thepat.find(' ', start)
            if spfind == -1:
                spfind = maxlen
            unfind = thepat.find('_', start)
            if unfind == -1:
                unfind = maxlen
            if unfind < spfind:   # somehow think I don't need this check...well, I just need the terminating point, still need to see which is lower
                phlist.append(thepat[start:unfind])
                phlist.append('_')
                start = unfind + 1
            else:
                phlist.append(thepat[start:spfind])
                phlist.append(' ')
                start = spfind + 1
        return phlist

    def _get_verb_forms(self):
    # get the irregular forms of a verb
        global verb, theverb
        scr = verb.partition('{')
        sc1 = scr[2].partition('}')
        forms = sc1[0].split()
        for wrd in forms:
            vscr = wrd + " "
            self.verb_dict[vscr] = [False, theverb]

    def read_actor_dictionary(self):
    # Actors are stored in a dictionary of pattern lists keyed on the first word
    # of the phrase. the Pattern lists begin with the code, the connector from then
    # key, and then a series of 2-tuples containing the remaining words and
    # connectors.
    # Still need date restrictions and synonym
    # Still need: optional POS info from patterns, which will be stored in the tuple
        fin = open(self.actors, 'r')

        #Are these two still necessary?
        #theverb = ''
        #ka = 0
        for line in fin:  # loop through the file
            part = line.partition('[')
            actor = part[0].strip() + ' '
            code = part[2].partition(']')[0]
#	print verb, code  # debug
            start = 0
            maxlen = len(actor) + 1  # this is just a telltail
            phlist = [code]
            while start < len(actor):  # break phrase on ' ' and '_'
                spfind = actor.find(' ', start)
                if spfind == -1:
                    spfind = maxlen
                unfind = actor.find('_', start)
                if unfind == -1:
                    unfind = maxlen
                if unfind < spfind:   # somehow think I don't need this check...well, I just need the terminating point, still need to see which is lower
                    if len(phlist) == 1:
                        keyword = actor[start:unfind]
                        phlist.append('_')
                    else:
                        phlist.append((actor[start:unfind], '_'))  # this won't change, so use a tuple
                    start = unfind + 1
                else:
                    if len(phlist) == 1:
                        keyword = actor[start:spfind]
                        phlist.append(' ')
                    else:
                        phlist.append((actor[start:spfind], ' '))
                    start = spfind + 1
            if keyword in self.actor_dict:  # we don't need to store the first word, just the connector
                self.actor_dict[keyword].append(phlist)
            else:
                self.actor_dict[keyword] = [phlist]

        # sort the patterns by the number of words
        for lockey in self.actor_dict.keys():
            self.actor_dict[lockey].sort(key=len, reverse=True)

        return self.actor_dict
