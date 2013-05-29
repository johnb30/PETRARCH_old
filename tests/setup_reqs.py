import nltk as nk

print 'Checking reqs...'
try:
    nk.data.load(nk.tag._POS_TAGGER)
    print 'Everything looks good!'
except LookupError:
    print 'Exception. Downloading POS Tagger...'
    nk.download('maxent_treebank_pos_tagger')
    print 'Data downloaded!'

print 'Done!'
