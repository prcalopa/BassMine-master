import bassmine
import markov
import json
import csv
import random

style = {1: 'booka_shade', 2: 'mr_scruff'}

style_id = 1

bass_path = '../../corpus/' + style[style_id] + '/bass'
drum_path = '../../corpus/' + style[style_id] + '/drums'

# Analyse corpus and build Markov model
MM, kick_patterns, pitch_model = bassmine.corpus_analysis(bass_path, drum_path)
MM.normalize_model()
pitch_model.normalize_model()
# Given a Kick pattern generate a NHMM with interlocking constraint
#target = kick_patterns[random.randint(0,len(kick_patterns)-1)]
#print target
#print kick_patterns


target = [8,8,8,9,8,8,9,0]


#markov.constrainMM(MM,target)


_path = '../../models/' + style[style_id] + '/'

"""
# Export to json
bassmine.write2json('initial', MM.get_initial(), _path)
bassmine.write2json('temporal', MM.get_temporal(), _path)
bassmine.write2json('interlocking', MM.get_interlocking(), _path)
"""
"""
# Export to pickle files
bassmine.write2pickle('initial', MM.get_initial(),_path)
bassmine.write2pickle('temporal', MM.get_temporal(),_path)
bassmine.write2pickle('interlocking', MM.get_interlocking(),_path)
"""
"""
print "Filtered initial"
print b0
print "NH model"
for b in B:
	print "\n New matrix"
	print b
"""

print "Initial"
print pitch_model.get_initial()
print "Temporal"
print pitch_model.get_temporal()

pitch_init_model = markov.markov_tm_2dict(pitch_model.get_initial())
pitch_temporal_model = markov.markov_tm_2dict(pitch_model.get_temporal())
pitch_dict = dict()
print(pitch_temporal_model)


## TEmporal model
for key,val in pitch_temporal_model.iteritems():
			pitch_dict[key] = {}
			print key # parent
			print list(val) # child
			tmp = [] # child
			for v in val:
				tmp.append(pitch_model.get_temporal()[key, int(v)])
			print list(tmp/sum(tmp))
			pitch_dict[key]['interval'] = [int(x) for x in val]
			pitch_dict[key]['probs'] = list(tmp/sum(tmp))

print "YYYYYYYYY", pitch_dict

with open(_path + 'pitch_model_'+ style[style_id] + '.json', 'w') as outfile:
		json.dump(pitch_dict, outfile)


#print "Interlocking"
#print MM.get_interlocking()

"""
with open('initial.csv', 'wb') as f:
	writer = csv.writer(f)
	writer.writerow(MM.get_initial())

with open('temporal.csv', 'wb') as f:
	writer = csv.writer(f)
	temp = MM.get_temporal()
	for row in temp:
		writer.writerow(row)

with open('interlocking.csv', 'wb') as f:
	writer = csv.writer(f)
	temp = MM.get_interlocking()
	for row in temp:
		writer.writerow(row)
"""