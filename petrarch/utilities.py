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
