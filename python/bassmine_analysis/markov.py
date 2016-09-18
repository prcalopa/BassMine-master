import numpy as np
import copy


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



"""
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
"""