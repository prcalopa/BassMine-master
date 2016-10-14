def zeros2dlist(size):

	out = []

	for i in range(size[0]):
		out.append([])
		for j in range(size[1]):
			out[i].append(0)
	return out		


def numberOfBeats(data):
	"""
	Number of beats of a midi file
	:param data: number of last beat position of the midi file  np.array[()] 1D
	:return: number of beats in the midi file. The size is approximated to be proportional to 4 beats.
	"""
	aux = [4, 8, 16, 32, 64, 128, 256]
	#idx = abs(max(data) - aux).argmin()
	idx = [abs(max(data)-x) for x in aux]
	#nob = aux[idx]
	nob = aux[idx.index(min(idx))]
	return nob

def quantize_pattern(pattern):
	RES = 4

	noBeats_bass = numberOfBeats(pattern)  # Bass files length set the global length of analysis
	print '\n# of beats: ', noBeats_bass
	#beat_subdiv = np.arange(start=0, step=0.25, stop=(noBeats_bass * RES) - 1)
	subdiv_aux = [0., 0.25, 0.5, 0.75]
	# Matrix to store the binary representation of the midi files
	# Basslines -> 1 matrix
	#rhythm = np.zeros((noBeats_bass, RES), dtype=int)
	rhythm =  zeros2dlist([noBeats_bass,RES])
	print rhythm

	for o in pattern:
		# quantize to the closest subdivision
		i, d = divmod(o, 1)  # i = row(beat number) , d = column (beat subdivision)
		print "beat", i
		xx = [abs(x-d) for x in subdiv_aux]
		print xx
		d_ = xx.index(min(xx))
		print d_
		if i < noBeats_bass:
			rhythm[int(i)][d_] = 1
	print rhythm
	return rhythm


def translate_rhythm(rhythm):

	id = []

	for beat in rhythm:
		id.append((beat[0] * 8) + (beat[1] * 4) + (beat[2] * 2) + beat[3])
	return id



target = [0,0.26,0.51,1,2,3.56]
####
# Quantize
kick_rhythm = quantize_pattern(target)
print kick_rhythm
# Translate
kick_id = translate_rhythm(kick_rhythm)	
print kick_id