#!/usr/bin/env python

import json
import csv
from operator import itemgetter
import match

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

meps={}
countries={}
cmembers={}
parties={}
pmembers={}
mepids={}
mepnames={}
for mep in json.load(open('data/ep_meps_current.json','r')):
    if mep['Constituencies'][0]['start'] > '2009-07-13T00:00:00':
        mepids[mep['UserID']]={'name': mep['Name']['full'].title(),
                               'mepid': mep['UserID'],
                               'country': mep['Constituencies'][-1]['country'],
                               'party': mep['Constituencies'][-1]['party']}
        mepnames[mep['Name']['full'].title()]={'country': mep['Constituencies'][-1]['country'],
                                               'mepid': mep['UserID'],
                                               'party': mep['Constituencies'][-1]['party']}
        try:
            cmembers[mep['Constituencies'][-1]['country']]+=1
        except KeyError:
            cmembers[mep['Constituencies'][-1]['country']]=1
        try:
            pmembers[mep['Constituencies'][-1]['party']]+=1
        except:
            pmembers[mep['Constituencies'][-1]['party']]=1

############################################
# lobbyplag

lp_ams = json.load(open('data/amendments.json','r'))
lp_scores = json.load(open('data/classified.json','r'))

ams = {am['uid']: am for am in lp_ams}

for c in lp_scores:
    if c['vote'] == 'weaker':
        pt = -1
    elif c['vote'] == 'stronger':
        pt = 1
    else:
        continue
    for mep in ams[c['uid']]['authors']:
        try:
            meps[mep]['pt']+=float(pt)/len(ams[c['uid']]['authors'])
            meps[mep]['cnt']+=1
        except KeyError:
            meps[mep]={'pt': float(pt)/len(ams[c['uid']]['authors']),
                       'cnt': 1}
        try:
            parties[mepnames[mep.title()]['party']]['pt']+=float(pt)/len(ams[c['uid']]['authors'])
            parties[mepnames[mep.title()]['party']]['cnt']+=1
        except KeyError:
            parties[mepnames[mep.title()]['party']]={'pt': float(pt)/len(ams[c['uid']]['authors']),
                                                     'cnt': 1}
        try:
            countries[mepnames[mep.title()]['country']]['pt']+=float(pt)/len(ams[c['uid']]['authors'])
            countries[mepnames[mep.title()]['country']]['cnt']+=1
        except KeyError:
            countries[mepnames[mep.title()]['country']]={'pt': float(pt)/len(ams[c['uid']]['authors']),
                                                         'cnt': 1}

meps = {mep: {'privacy': v['pt']/v['cnt'],
              'party': mepnames[mep.title()]['party'],
              'country': mepnames[mep.title()]['country'],
              'mepid': mepnames[mep.title()]['mepid'],
              'total': v['pt']/v['cnt']}
        for mep, v in meps.items()}
countries = {country: v['pt']/v['cnt']
             for country, v in countries.items()}
parties = {party: v['pt']/v['cnt']
           for party, v in parties.items()}

############################################
# sandbag/ffoe

csvfile = open("data/climate.csv")
dialect = csv.Sniffer().sniff(csvfile.read(1024*64))
csvfile.seek(0)
reader = unicode_csv_reader(csvfile, dialect=dialect)
headers = reader.next()
for line in reader:
    if not line[0].strip(): continue
    mep = line[0].strip().title()
    if mep in meps and 'climate' in meps[mep]:
        #print "duplicate in climate", mep.encode('utf8'), line[4], meps[mep]
        continue
    try:
        meps[mep]['climate']=float(line[4])
        meps[mep]['total']+=float(line[4])
    except KeyError:
        meps[mep] = {'climate':float(line[4]),
                     'mepid': mepnames[mep.title()]['mepid'],
                     'party': mepnames[mep.title()]['party'],
                     'country': mepnames[mep.title()]['country'],
                     'total': float(line[4])}

    try:
        parties[mepnames[mep.title()]['party']] += float(line[4])
    except KeyError:
        parties[mepnames[mep.title()]['party']] = float(line[4])

    try:
        countries[mepnames[mep.title()]['country']] += float(line[4])
    except KeyError:
        countries[mepnames[mep.title()]['country']] = float(line[4])
############################################
# memopol

memopol = json.load(open('data/memopol.json','r'))
for mep in memopol['objects']:
    if mepids.get(int(mep['ep_id'])) and mep['total_score']:
        if not int(mep['ep_id']) in mepids: continue
        try:
            meps[mepids[int(mep['ep_id'])]['name']]['information'] = mep['total_score'] / float(mep['max_score_could_have'])
            meps[mepids[int(mep['ep_id'])]['name']]['total'] += mep['total_score'] / float(mep['max_score_could_have'])
        except KeyError:
            meps[mepids[int(mep['ep_id'])]['name']] = {'information': mep['total_score'] / float(mep['max_score_could_have']),
                                                       'mepid': int(mep['ep_id']),
                                                       'party': mepids[int(mep['ep_id'])]['party'],
                                                       'country': mepids[int(mep['ep_id'])]['country'],
                                                       'total': mep['total_score'] / float(mep['max_score_could_have']),}


        try:
            parties[mepids[int(mep['ep_id'])]['party']] += mep['total_score'] / float(mep['max_score_could_have'])
        except KeyError:
            parties[mepids[int(mep['ep_id'])]['party']] = mep['total_score'] / float(mep['max_score_could_have'])

        try:
            countries[mepids[int(mep['ep_id'])]['country']] += mep['total_score'] / float(mep['max_score_could_have'])
        except KeyError:
            countries[mepids[int(mep['ep_id'])]['country']] = mep['total_score'] / float(mep['max_score_could_have'])

############################################
# phillip morris

csvfile = open("data/pm.csv")

dialect = csv.Sniffer().sniff(csvfile.read(1024*64))
csvfile.seek(0)
reader = unicode_csv_reader(csvfile, dialect=dialect)
headers = reader.next()
for line in reader:
    if not line[0].strip(): continue
    if len([x for x in line[1:] if x.strip()]) == 0: continue
    mep = ' '.join(line[0].strip().title().split(',')[::-1]).strip()
    if mep not in mepnames:
        mep = match.fuzzy_match(mep, mepnames.keys())[0]
    score = (len([x for x in line[1:] if x == u'[RED]']) - len([x for x in line[1:] if x == u'[GREEN]']))/6.0

    try:
        meps[mep]['tobacco']=score
        meps[mep]['total']+=score
    except KeyError:
        meps[mep] = {'tobacco': score,
                     'mepid': mepnames[mep.title()]['mepid'],
                     'party': mepnames[mep]['party'],
                     'country': mepnames[mep]['country'],
                     'total': score}

    try:
        parties[mepnames[mep]['party']] += score
    except KeyError:
        parties[mepnames[mep]['party']] = score

    try:
        countries[mepnames[mep]['country']] += score
    except KeyError:
        countries[mepnames[mep]['country']] = score


tots=0
print ', '.join(['mepid','total','climate','information','privacy','tobacco'])
for rank, (mep, scores) in enumerate(sorted(meps.items(), key=lambda (k,v): v['total'])):
    print '%s,%s,' % (scores['mepid'], scores['total']),
    print ', '.join(["%s" % scores.get(k) for k in ['climate','information','privacy','tobacco']])
    tots+=scores['total']
#print '---------   meps   ---------'
#print ', '.join(['rank','name','total','country','party','climate','information','privacy','tobacco'])
#for rank, (mep, scores) in enumerate(sorted(meps.items(), key=lambda (k,v): v['total'])):
#    print '%4d, "%s", %s, "%s", "%s",' % (rank+1, mep.encode('utf8'), scores['total'], scores['country'].encode('utf8'), scores['party'].encode('utf8')),
#    print ', '.join(["%s" % scores.get(k) for k in ['climate','information','privacy','tobacco']])
#print '\n-------   countries   ------'
#print ', '.join(['rank','country','avg','total'])
#for rank, (country, scores) in enumerate(sorted(countries.items(), key=lambda (k,v): v/cmembers[k])):
#    print '%4d, "%s", %f, %f' % (rank+1, country.encode('utf8'), scores/cmembers[country], scores)
#print '\n--------   parties   -------'
#print ', '.join(['rank','party','avg','total'])
#for rank, (party, scores) in enumerate(sorted(parties.items(), key=lambda (k,v): v/pmembers[k])):
#    print '%4d, "%s", %f, %f' % (rank+1, party.encode('utf8'), scores/pmembers[party], scores, )
print tots
