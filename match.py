#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from operator import itemgetter
import unicodedata

# src: http://stackoverflow.com/questions/653157/a-better-similarity-ranking-algorithm-for-variable-length-strings
def get_bigrams(string):
    '''
    Takes a string and returns a list of bigrams
    '''
    s = string.lower()
    return [s[i:i+2] for i in xrange(len(s) - 1)]

# src: http://stackoverflow.com/questions/653157/a-better-similarity-ranking-algorithm-for-variable-length-strings
def similarity(str1, str2):
    '''
    Perform bigram comparison between two strings
    and return a percentage match in decimal form
    '''
    pairs1 = get_bigrams(str1)
    pairs2 = get_bigrams(str2)
    union  = len(pairs1) + len(pairs2)
    hit_count = 0
    for x in pairs1:
        for y in pairs2:
            if x == y:
                hit_count += 1
                break
    return (2.0 * hit_count) / union

def fuzzy_match(name, names):
    sims = []
    for other in names:
        n = unicodedata.normalize('NFKD', unicode(u' '.join(sorted(name.split())))).encode('ascii','ignore')
        o = unicodedata.normalize('NFKD', unicode(u' '.join(sorted(other.split())))).encode('ascii','ignore')
        sim=similarity(n,o)
        sims.append((other,sim))
    return sorted(sims, key=itemgetter(1), reverse=True)[0]

