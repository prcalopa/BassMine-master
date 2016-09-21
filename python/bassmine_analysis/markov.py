import numpy as np
import copy
import json

def normalize(a):
	c = 0
	for row in a:
		factor = sum(row)
		if factor > 0:
			a[c, :] = row / factor
		c += 1
	return a


def indices(a, func):
	# UF.indices(tmp_sv, lambda x: x <= target_sv[i])
	return [i for (i, val) in enumerate(a) if func(val)]


class MarkovModel:
	def __init__(self, model_size, order=1):
		if type(model_size) == tuple:
			if len(model_size) == 2:
				self.model_size = model_size
			else:
				raise NameError("Model size must be an integer or a tuple of the form (x,y)")
		elif type(model_size) == int:
			self.model_size = (model_size, model_size)
		else:
			raise NameError("Model size must be an integer or a tuple of the form (x,y)")

		# Model state
		self.normalized = False

		# Temporal model
		self.support_temporal = np.zeros(self.model_size, dtype=float)
		self.support_initial = np.zeros(self.model_size[0], dtype=float)
		# Interlocking model
		self.support_interlocking = np.zeros(self.model_size, dtype=float)
		# Normalized model
		self.initial_model = []
		self.temporal_model = []
		self.interlocking_model = []

	def add_temporal(self, pattern):
		count = 0
		for p in pattern:
			if count == 0:
				self.update_initial(p)
			elif 0 < count < len(pattern) - 1:
				self.update_temporal(pattern[count - 1], p)
			elif count == len(pattern) - 1:
				self.update_temporal(pattern[count], pattern[0])
			count += 1

	def add_interlocking(self, patt_kick, patt_bass):

		l = min(len(patt_kick), len(patt_bass))

		for i in range(l):
			self.update_interlocking(patt_kick[i], patt_bass[i])

	def update_interlocking(self, x, y):
		self.support_interlocking[x, y] += 1.

	def update_temporal(self, x, y):
		self.support_temporal[x, y] += 1.

	def update_initial(self, x):
		self.support_initial[x] += 1.

	def normalize_model(self):

		self.initial_model = self.support_initial / sum(self.support_initial)
		self.temporal_model = normalize(self.support_temporal)
		self.interlocking_model = normalize(self.support_interlocking)

	def get_initial(self):
		return self.initial_model

	def get_temporal(self):
		return self.temporal_model

	def get_interlocking(self):
		return self.interlocking_model




def buildMNHM(markov_model, target):
	b0 = copy.copy(markov_model.get_initial())
	b = copy.copy(markov_model.get_temporal())
	inter = copy.copy(markov_model.get_interlocking())

	i = []
	# Iterate beat-by-beat to create NHMM
	B = []

	for t in range(len(target)):

		if t == 0:
			const_d = indices(inter[target[t]], lambda x: x == 0)
			init_const = indices(b0, lambda x: x == 0)
			if len(init_const) > 0:
				for ic in init_const:
					const_d.append(ic)
			for c in const_d:
				b0[c] = 0.
			#print b0

		else:
			bn = np.matrix(b)
			# Propagate constraint from previous iteration
			# delete rows
			for c in const_d:
				bn[c, :] = 0.

			# Interlocking contraint
			prop_const = indices(inter[target[t]], lambda x: x == 0)
			# delete columns
			for p in prop_const:
				bn[:, p] = 0.

			# Update propagation constraint to next iteration
			const_d = prop_const
			#print const_d
			#print bn
			B.append(bn)

	return b0, B

def constrainMM(markov_model, target):
	b0 = copy.copy(markov_model.get_initial())
	b = copy.copy(markov_model.get_temporal())
	inter = copy.copy(markov_model.get_interlocking())

	# b and inter are converted to dictionaries {row>0 : (idx columns>0)}
	# Domains
	Dom_init = markov_tm_2dict(b0)
	Dom_B = markov_tm_2dict(b)
	Dom_I = markov_tm_2dict(inter)

	print "Initial dict ", Dom_init
	print "Temporal dict ", Dom_B
	print "Interlocking dict ", Dom_I

	target_setlist = []
	for t in target:
		target_setlist.append(Dom_I[t])
	print target_setlist

	# V store the domain of each step
	V = []

	filter_init = Dom_init.intersection(target_setlist[0])
	print list(filter_init)
	# Look for possible continuations of filter_init in Dom_B, constrained to target_list[1]
	V.append(dict())
	tmp = []
	for f in filter_init:
		print "Possible intital continuations",f, Dom_B[int(f)]
		print "Kick constrain", target_setlist[1]
		print "Intersection", Dom_B[int(f)].intersection(target_setlist[1])

		if len(Dom_B[int(f)].intersection(target_setlist[1])) > 0:
			V[0][int(f)] = Dom_B[int(f)].intersection(target_setlist[1])
			tmp.append(f)


		print "\n\n"
	print "Kick constr", list(target_setlist[0])
	print "V0", V[0]
	#print "V1", V[1].keys()	# Domain for step 1 / rows  of transition matrix
	#print V[1]
	# Create rest of V
	for step in range(1, len(target)-1):
		V.append(dict())
		#print "Kick constr", list(target_setlist[step])
		# for each v in V[step] keep continuations that match interlocking with step+1
		for t in target_setlist[step]:
			if len(Dom_B[int(t)].intersection(target_setlist[step+1])):
				V[step][int(t)] =  Dom_B[int(t)].intersection(target_setlist[step+1])
		#print "check\n"
		print "V", step, V[step].keys()

	# Delete values from each key in V[i] that are not in V[i+1]
	val_del = dict()


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
	print val_del

	for step, value in val_del.iteritems():
		if len(value) > 0:
			for v in value:
				# Delete key
				print V[step-1].pop(v, None)
			# Delete in previous continuations
			print V[step-2]
			for idx in V[step-2].keys():
				V[step-2][idx] = set([str(x) for x in V[step-1].keys()]).intersection(V[step-2][idx])


	print len(V)
	print "\nFinal Model:"
	out_Model = {}
	init = []
	init_dict = dict()
	for key in V[0]:
		init.append(b0[key])
	init_dict['initial'] = dict()
	init_dict['initial']['prob'] = list(init/sum(init))
	init_dict['initial']['pattern'] = V[0].keys()

	print init_dict



	for i in range(len(V)):
		out_Model[i] = {}
		print "step:",i
		for key,val in V[i].iteritems():
			out_Model[i][key] = {}
			print key # parent
			print list(val) # child
			tmp = [] # child
			for v in val:
				tmp.append(b[key, int(v)])
			print list(tmp/sum(tmp))
			out_Model[i][key]['pattern'] = [int(x) for x in val]
			out_Model[i][key]['probs'] = list(tmp/sum(tmp))

	print out_Model
	# Merge all ditionaries
	"""
	Vdict = dict()
	for l in range(len(V)-1):
		print V[l]
		Vdict[l] = V[l]
"""
	# export to JSON
	with open( 'V_test.json', 'w') as outfile:
		json.dump(out_Model, outfile)
		outfile.close()
	with open( 'V_test_init.json', 'w') as outfile:
		json.dump(init_dict, outfile)
		outfile.close()

	print len(out_Model)


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
