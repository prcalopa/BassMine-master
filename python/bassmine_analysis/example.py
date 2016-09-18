import bassmine
import markov
import json

bass_path = 'Bass'
drum_path = 'Drums'

# Analyse corpus and build Markov model
MM, kick_patterns = bassmine.corpus_analysis(bass_path, drum_path)
MM.normalize_model()

# Given a Kick pattern generate a NHMM with interlocking constraint
target = kick_patterns[0]
print kick_patterns

#b0, B = markov.buildMNHM(MM, target)

# Export to json
json_path = '../../models/'
bassmine.write2json('initial', MM.get_initial(), json_path)
bassmine.write2json('temporal', MM.get_temporal(), json_path)
bassmine.write2json('interlocking', MM.get_interlocking(), json_path)

# Export to pickle files
bassmine.write2pickle('b0',MM.get_initial())
bassmine.write2pickle('b',MM.get_temporal())
bassmine.write2pickle('inter',MM.get_interlocking())
"""
print "Filtered initial"
print b0
print "NH model"
for b in B:
	print "\n New matrix"
	print b
"""