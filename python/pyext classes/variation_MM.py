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
		
		## Representation of target kick pattern as variable domain
		target_setlist = []
		for t in target:
			# RELAXATION RULE: if the target kick is not in the model consider metronome pulse as kick
			if t >= 0:
				target_setlist.append(t)
			else:
				target_setlist.append(Dom_B.keys())	
				#print "Kick pattern mistmatch"
		#print target_setlist

		## V store the domain of patterns at each step
		V = []

		#filter_init = Dom_init.intersection(target_setlist[0])
		#print list(filter_init)
		## Look for possible continuations of filter_init in Dom_B, constrained to target_list[1]
		V.append(dict())
		tmp = []
		#for f in filter_init:
		#	print "Possible intital continuations",f, Dom_B[int(f)]
		#	print "Kick constrain", target_setlist[1]
		#	print "Intersection", Dom_B[int(f)].intersection(target_setlist[1])

		#	if len(Dom_B[int(f)].intersection(target_setlist[1])) > 0:
		#		V[0][int(f)] = Dom_B[int(f)].intersection(target_setlist[1])
		#		tmp.append(f)
		#	print "\n\n"
		V[0][target_setlist[0]] = Dom_B[target_setlist[0]]
		#print "Kick constr", list(target_setlist[0])
		#print "V0", V[0]
		#print "V1", V[1].keys()	# Domain for step 1 / rows  of transition matrix
		#print V[1]

		## Create rest of V
		##############################################
		## Make backtrack free Non-Homogeneuous Markov Model ordr 1
		##############################################
		for step in range(1, len(target)-1):
			V.append(dict())
			#print "Kick constr", list(target_setlist[step])
			# for each v in V[step] keep continuations that match interlocking with step+1
			for t in target_setlist[step]:
				if len(Dom_B[int(t)].intersection(target_setlist[step+1])):
					V[step][int(t)] =  Dom_B[int(t)].intersection(target_setlist[step+1])
			#print "check\n"
			#print "V", step, V[step].keys()

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
		out_Model = {}
		init = []
		init_dict = dict()
		for key in V[0]:
			init.append(b0[key])
		init_dict['initial'] = dict()
		init_dict['initial']['prob'] = list(init/sum(init))
		init_dict['initial']['pattern'] = V[0].keys()
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
				out_Model[i][key]['pattern'] = [int(x) for x in val]
				out_Model[i][key]['probs'] = list(tmp/sum(tmp))
		#print out_Model
		with open( path + 'NHModel_var.json', 'w') as outfile:
			json.dump(out_Model, outfile)
			outfile.close()

		with open( path + 'Model_init.json', 'w') as outfile:
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
	 	


		