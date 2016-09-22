import bassmine
import markov
import json
import csv
import random

style = {1: 'booka_shade', 2: 'mr_scruff'}

style_id = 2

bass_path = '../../corpus/' + style[style_id] + '/bass'
drum_path = '../../corpus/' + style[style_id] + '/drums'

# Analyse corpus and build Markov model
MM, kick_patterns = bassmine.corpus_analysis(bass_path, drum_path)
MM.normalize_model()

# Given a Kick pattern generate a NHMM with interlocking constraint
#target = kick_patterns[random.randint(0,len(kick_patterns)-1)]
#print target
#print kick_patterns
target = [8,8,8,9,8,8,9,0]

#b0, B = markov.buildMNHM(MM, target)
markov.constrainMM(MM,target)


_path = '../../models/' + style[style_id] + '/'

"""
# Export to json
bassmine.write2json('initial', MM.get_initial(), _path)
bassmine.write2json('temporal', MM.get_temporal(), _path)
bassmine.write2json('interlocking', MM.get_interlocking(), _path)
"""
# Export to pickle files
bassmine.write2pickle('initial', MM.get_initial(),_path)
bassmine.write2pickle('temporal', MM.get_temporal(),_path)
bassmine.write2pickle('interlocking', MM.get_interlocking(),_path)

"""
print "Filtered initial"
print b0
print "NH model"
for b in B:
	print "\n New matrix"
	print b
"""
"""
print "Initial"
print MM.get_initial()
print "Temporal"
print MM.get_temporal()
print "Interlocking"
print MM.get_interlocking()
"""
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