from nltk.tree import Tree


def coref_replace(tree, corefs):
    """
    Function to replace pronouns with the referenced noun phrase. Parse trees
    are modified in place, so nothing is returned. Replaces the pronoun with
    a nltk.tree object with node type `COREF`.

    Parameters
    ----------

    tree : nltk.tree object
            Parse tree in nltk.tree format.

    corefs : list
            List of tuples as produced by corenlp-python that contains
            information on pronouns and coreferences.
    """
    shift = 0
    errors = list()
    for item in corefs[0]:
        pronoun = item[0]
        ref = item[1]
        if any([word in ref[0] for word in pronoun[0].split()]):
            pass
        elif any([word in pronoun[0] for word in ref[0].split()]):
            pass
        elif pronoun[4] - pronoun[3] > 1:
            pass
        else:
            try:
                pronoun_pos = tree.leaf_treeposition(pronoun[3] + shift)
                coref_pos = tree.leaf_treeposition(ref[3])[:-2]
                coref_tree = Tree('COREF', [tree[coref_pos]])
                tree[pronoun_pos[:-1]] = coref_tree
                if len(coref_tree.leaves()) == 1:
                    shift += 0
                else:
                    shift += coref_tree.height()
                errors.append(False)
            except RuntimeError:
                errors.append(True)
                pass
    return tree, errors


def _get_np(parse_tree):
    """
    Private function to pull noun phrases from a parse tree.

    Parameters
    ----------

    parse_tree : NLTK.tree object
                Parse tree from which to pull noun phrases.

    Returns
    -------

    output : Dictionary
            Dictionary with two keys: `noun_phrases` and `np_words`.
            `noun_phrases` is a list of noun phrases in the parse tree, while
            `np_words` is a list of words contained in the noun phrases.
    """
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree.subtrees(filter=lambda x: x.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)

    output['noun_phrases'] = phrases
    output['np_words'] = words

    return output


def _get_vp(parse_tree):
    """
    Private function to pull verb phrases from a parse tree.

    Parameters
    ----------

    parse_tree : NLTK.tree object
                Parse tree from which to pull verb phrases.

    Returns
    -------

    output : Dictionary
            Dictionary with two keys: `verb_phrases` and `vp_words`.
            `verb_phrases` is a list of verb phrases in the parse tree, while
            `vp_words` is a list of words contained in the verb phrases.
    """
    phrases = list()
    words = list()
    output = dict()
    for node in parse_tree.subtrees(filter=lambda x: x.node == 'NP'):
        phrases.append(node)
        for word in node.leaves():
            words.append(word)

    output['verb_phrases'] = phrases
    output['vp_words'] = words

    return output
