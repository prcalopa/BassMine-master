import pickle
import os

def markov_tm_2dict(a):
	out = dict()
	key = 0

	if len(a.shape) == 2:
		for row in a:
			value = 0
			tmp_dom = []
			if sum(row) > 0:
				for col in row:
					if col > 0:
						tmp_dom.append(str(value))
					value += 1
				out[key] = set(tmp_dom)
			key += 1
		return out
	elif len(a.shape) == 1:
		tmp_dom = []
		value = 0
		for col in a:
			if col > 0:
				tmp_dom.append(str(value))
			value += 1
		return set(tmp_dom)
	else:
		print "Wrong size"





style_path = 'mr_scruff/' 	
		
tmp = os.path.dirname(__file__)
tmp_ = '/'.join(tmp.split('/')[:-2])
#print tmp
path = tmp_ + "/models/"
b = pickle.load( open(path + style_path+ "temporal.pickle", "rb") )
		
Dom_B = markov_tm_2dict(b)


# target
target = [8,8,4,14,4,10,8,2,8]

# Create V : variable domain for transitions
V = []

V.append(dict())

if target[1] >= 0:
	V[0][target[0]] = set([str(target[1])])
else:
	V[0][target[0]] = Dom_B[target[0]]


for i in range(1,len(target)-1):

	V.append(dict())

	if target[i] >= 0:  # Current beat don't vary

		for key, value in V[i-1].iteritems():
		
			# store keys that match target[i]
			tmp_key = value.intersection(set([str(target[i])]))
			if len(tmp_key) > 0:
				V[i][int(list(tmp_key)[0])] = Dom_B[int(list(tmp_key)[0])]
			#V[i][target[i-1]] = set([str(target[i])])

	else:  # Current beat varies

		#Check possible continuations from V[i-1] as Key candidates in V[i]
		for key, value in V[i-1].iteritems():

			for v in value:
				V[i][int(v)] = Dom_B[int(v)]

		print "h"


V.append(dict())

V[len(target)-1][target[len(target)-1]] = Dom_B[target[len(target)-1]]		

#print V		
for v in V:
	print v
	print "\n"


## Delete values from each key in V[i] that are not in V[i+1]
val_del = dict()
## Font-propagation	
for step in range(1,len(target)-1):
	val_del_temp = []
	next_key = set([str(x) for x in V[step].keys()])
	#print next_key
	for key, value in V[step-1].iteritems():
		#print key, value
		tmp_int = value.intersection(next_key)
		#if len(tmp_int) > 0:
		V[step-1][key] = tmp_int
		if len(tmp_int) == 0:
			val_del_temp.append(key)
	val_del[step] = val_del_temp
#print val_del
## Back-propagation
for step, value in val_del.iteritems():
	if len(value) > 0:
		for v in value:
			## Delete key
			V[step-1].pop(v, None)
		## Delete in previous continuations
		#print V[step-2]
		for idx in V[step-2].keys():
			V[step-2][idx] = set([str(x) for x in V[step-1].keys()]).intersection(V[step-2][idx])
# BUILD FINAL DICTIONARY		

print "Cleaned-UP"		
for v in V:
	print v
	print "\n"
