try:
	import pyext
	import sys
	import random
	import copy
	import pickle
	import json
	import os
except:
	print "ERROR: This script must be loaded by the PD/Max pyext external"



#################################################################
def indices(a, func):
    # UF.indices(tmp_sv, lambda x: x <= target_sv[i])
    return [i for (i, val) in enumerate(a) if func(val)]

def write2pickle(name,data, path='models/'):
	#path = 'rhythmic_analysis/graph_models/pickle/'

	with open(path + name + '.pickle', 'wb') as f:
		# Pickle the 'data' dictionary using the highest protocol available.
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)    

def normalize(a):
	c = 0
	for row in a:
		factor = sum(row)
		if factor > 0:
			a[c, :] = row / factor
		c += 1
	return a

class build(pyext._class):
	"""Build Non Homogeneuous Markov Model with interlocking constraint"""

	# number of inlets and outlets
	_inlets=2
	_outlets=2


	style = 0 # 0:BookaShade 1:MrScruff
	# methods for first inlet

	def bang_1(self):
		print "Bang into first inlet"

	def int_1(self,f):
		print "Integer",f,"into first inlet"
		if (0<=f<2):
			style = f
			print "Style changed!"

	def float_1(self,f):
		print "Float",f,"into first inlet"

	def list_1(self,*s):
		# print "List",s,"into first inlet"
		target = list(s)
		####
		# STYLE CHANGE
		if int(self.style) == 0:
			style_path = 'booka_shade/'
		elif int(self.style) == 1:
			style_path = 'mr_scruff/' 	
		####
		# Load Models
		tmp = os.path.dirname(__file__)
		tmp_ = '/'.join(tmp.split('/')[:-2])
		#print tmp
		path = tmp_ + "/models/"
		#path = "/Users/Pere/Github Repo/BassMine/BassMine-master/models/" 
		#b0 = pickle.load( open(path+ style_path + "initial.pickle", "rb") )
		b = pickle.load( open(path + style_path+ "temporal.pickle", "rb") )
		#inter = pickle.load( open(path + style_path + "interlocking.pickle", "rb") )

		## b and inter are converted to dictionaries {row>0 : (idx columns>0)}
		## Domains
		#Dom_init = markov_tm_2dict(b0)
		Dom_B = markov_tm_2dict(b)
		#Dom_I = markov_tm_2dict(inter)

		#print "Initial dict ", Dom_init
		#print "Temporal dict ", Dom_B
		#print "Interlocking dict ", Dom_I
		
		# target
		#target = [8,8,4,-2,2,0,4,-2,8]

		# Create V : variable domain for transitions
		V = []


		# target
		#target = [8,8,4,14,4,10,8,2,8]

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

				#print "h"


		#V.append(dict())

		#V[len(target)-1][target[len(target)-1]] = set([str(target[len(target)-1])])		

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
		#print "\nFinal Model:"

		for key,val in V[len(V)-1].iteritems():
			tmp_val  = val.intersection(set([str(target[len(target)-1])]))
			print tmp_val
			if len(tmp_val)>0:
				V[len(V)-1][key] = tmp_val

		out_Model = {}
		

		# Force last beat 


		#init = []
		init_dict = dict()
		#for key in V[0]:
		#	init.append(b0[key])
		init_dict['initial'] = dict()
		init_dict['initial']['prob'] = 1.00
		init_dict['initial']['pattern'] = target[0]
		#print init_dict
		
		for i in range(len(V)):
			out_Model[i] = {}
			#print "step:",i
			for key,val in V[i].iteritems():
				out_Model[i][key] = {}
				#print key # parent
				#print list(val) # child
				tmp = [] # child
				for v in val:
					tmp.append(b[key, int(v)])
				#print list(tmp/sum(tmp))
				#print tmp
				out_Model[i][key]['pattern'] = [int(x) for x in val]
				out_Model[i][key]['probs'] = list(tmp/sum(tmp))
		#print out_Model
		with open( path + 'NHModel_var.json', 'w') as outfile:
			json.dump(out_Model, outfile)
			outfile.close()
		
		with open( path + 'Model_init_var.json', 'w') as outfile:
			json.dump(init_dict, outfile)
			outfile.close()
		
		print("Model build!")
		self._outlet(1,1)	


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
	 	


		