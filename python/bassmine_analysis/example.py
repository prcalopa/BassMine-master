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
with open('test.json', 'w') as outfile:
    json.dump(MM.get_initial().tolist(), outfile)
with open('test2.json', 'w') as outfile:
    json.dump(MM.get_temporal().tolist(), outfile)

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