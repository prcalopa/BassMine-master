import bassmine
import markov
import json
import csv

bass_path = 'Bass'
drum_path = 'Drums'

# Analyse corpus and build Markov model
MM, kick_patterns = bassmine.corpus_analysis(bass_path, drum_path)
MM.normalize_model()

# Given a Kick pattern generate a NHMM with interlocking constraint
target = kick_patterns[0][0:5]
#print target
#print kick_patterns
target = [8,6,0,9,8,2,4,0]

#b0, B = markov.buildMNHM(MM, target)
markov.constrainMM(MM,target)

"""
# Export to json
json_path = '../../models/'
bassmine.write2json('initial', MM.get_initial(), json_path)
bassmine.write2json('temporal', MM.get_temporal(), json_path)
bassmine.write2json('interlocking', MM.get_interlocking(), json_path)

# Export to pickle files
bassmine.write2pickle('b0', MM.get_initial())
bassmine.write2pickle('b', MM.get_temporal())
bassmine.write2pickle('inter', MM.get_interlocking())
"""
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