"""
Read midi files from folder

Each of the tracks are composed by bassline and drums MIDI files.
Each bassline file has an associated drums file with same file name.


"""
import madmom
import numpy as np
import pickle

import pattern_analysis as PA
import rhythmic_analysis.utility_functions as uf

BARS = 8
RES = 4

NBEATS = BARS * RES

drum_dict = dict(KICK=36, RIM=37, SNARE=38, CLAP=39, CHH1=44, CHH2=42, OHH=46, CRASH1=49, CRASH2=50, RIDE=51)

KICK = 36
RIM = 37
SNARE = 38
CLAP = 39
CHH1 = 44
CHH2 = 42
OHH = 46
CRASH1 = 49
CRASH2 = 50
RIDE = 51

DRUMS = np.array([
	KICK,
	RIM,
	SNARE,
	CLAP,
	CHH1,
	CHH2,
	OHH,
	CRASH1,
	CRASH2,
	RIDE])

DRUMS_NAMES = np.array([
	'KICK',
	'RIM',
	'SNARE',
	'CLAP',
	'CHH1',
	'CHH2',
	'OHH',
	'CRASH1',
	'CRASH2',
	'RIDE'])

#print DRUMS


#bass_path = '../CORPUS/BookaShade_Interlocking/Bass'
#drum_path = '../CORPUS/BookaShade_Interlocking/Drums'


target_drums = ['KICK']
############# config file


def corpus_analysis(bass_path, drum_path):

	bass_files = madmom.utils.search_files(bass_path, '.mid')
	drum_files = madmom.utils.search_files(drum_path, '.mid')

	bass_names = []
	drum_names = []

	print "Bass Files"
	for bf in bass_files:
		bass_names.append(bf[len(bass_path) + 1:-len('.mid')])
	print "\nNumber of files: ", len(bass_files)

	print "\nDrums Files"
	for df in drum_files:
		drum_names.append(df[len(drum_path) + 1:-len('.mid')])
	print "\nNumber of files: ", len(drum_files)


	# File counter
	file_it = 0

	# Pattern analysis
	pattern_stats = PA.patternstats(BARS * RES, len(DRUMS_NAMES)+1)
	pattern_drum = []  # empty array to store pattern_struct() instances
	pattern_bass = []  #

	# LOOP THROUGH THE DIFFERENT MIDI INSTANCES
	for f in range(len(drum_files)):
		# for f in range(0,2):
		match = str(madmom.utils.match_file('drums' + bass_names[f][4:], drum_names))
		match_file = drum_path + '/' + match[2:-2] + '.mid'

		print ('Bass file: '), bass_files[f]
		print ('Drum file: '), match_file
		print bass_names[f][5:-3]
		"""
		BASSLINE
		"""
		# Read Bassline files
		bass_midi = madmom.utils.midi.MIDIFile.from_file(bass_files[f])
		bass_midi.note_time_unit = 'b'
		onset_bass = bass_midi.notes[:, 0]
		noBeats_bass = uf.numberOfBeats(onset_bass)  # Bass files length set the global length of analysis
		print '\n# of beats: ', noBeats_bass
		beat_subdiv = np.arange(start=0, step=0.25, stop=(noBeats_bass * RES) - 1)
		subdiv_aux = np.array([0., 0.25, 0.5, 0.75])
		# Matrix to store the binary representation of the midi files
		# Basslines -> 1 matrix
		bass_rhythm = np.zeros((noBeats_bass, RES), dtype=int)

		for o in onset_bass:
			# quantize to the closest subdivision
			i, d = divmod(o, 1)  # i = row(beat number) , d = column (beat subdivision)
			d_ = (abs(subdiv_aux - d)).argmin()
			bass_rhythm[int(i), d_] = 1
		pattern_stats.fillhistogram(bass_rhythm, 0)
		"""
		DRUMS
		"""
		# Read Drum files
		#
		drum_midi = madmom.utils.midi.MIDIFile.from_file(match_file)
		drum_midi.note_time_unit = 'b'
		noBeats_drums = uf.numberOfBeats(drum_midi.notes[:, 0])

		print '\n# of beats: ', noBeats_drums
		#print drum_midi.notes

		# Check lenght of drums and bass, the idea is to match it.
		print "CHECK SIZE :", noBeats_bass/float(noBeats_drums)


		drum_instr = np.unique(drum_midi.notes[:, 1])  # number of drum sounds
		print 'Num of instruments: ', len(drum_instr)
		print 'Instrumnts: ', drum_instr


		# FIND WHICH DRUMS ARE IN THE FILE
		file_drums = []
		file_drums_idx = []
		drum_mask = np.zeros(len(DRUMS), dtype=bool)
		for i in drum_instr:
			it = 0
			for d in DRUMS:
				if int(i) == d:
					file_drums.append(DRUMS_NAMES[it])
					file_drums_idx.append(it)
					drum_mask[it] = 1
					break
				it += 1

		print file_drums
		print "Drums in file:", drum_mask

		drum_rhythms = np.zeros((noBeats_drums, 4, len(drum_instr)), dtype=int)
		drum_kit = np.zeros((len(DRUMS_NAMES), noBeats_bass * RES), dtype=int)

		# print drum_rhythms[:,:,1]

		aux = 0
		for dr in drum_instr:
			for o in drum_midi.notes:
				if o[1] == int(dr):  # Check if the onset is from the current target instrument
					i, d = divmod(o[0], 1)  # i = row(beat number) , d = column (beat subdivision)
					d_ = (abs(subdiv_aux - d)).argmin()  # Determine the subdivision location in the beat
					if i < noBeats_drums:
						drum_rhythms[int(i), int(d_), int(aux)] = 1
			aux += 1

		aux = 0
		check_length = noBeats_bass/float(noBeats_drums)
		for i in file_drums_idx:
			if check_length > 1:
				tmp = np.reshape(drum_rhythms[:, :, aux], noBeats_drums * RES)
				drum_kit[i, :] = np.resize(tmp, (1, tmp.shape[0]*check_length))
			else:
				drum_kit[i, :] = np.reshape(drum_rhythms[:, :, aux], noBeats_drums * RES)
			aux += 1
		#plt.imshow(drum_kit, interpolation='nearest')
		#plt.show()

		# FILTER DRUM INSTRUMENTS TO GROUP
		drum_kit = pattern_stats.filter_drums(drum_kit,target_drums, DRUMS_NAMES)

		drum_kit_patt, bass_patt =  pattern_stats.drumkit_similarity(drum_kit, bass_rhythm, file_it)
		for patt in drum_kit_patt:
			#plt.imshow(patt.pattern, interpolation='nearest')
			#plt.show()
			pattern_drum.append(patt)
		for patt in bass_patt:
			#plt.imshow(patt.pattern, interpolation='nearest')
			#plt.show()
			pattern_bass.append(patt)


		file_it += 1
		"""
		OUT OF FILES LOOP!
		"""

	print("PATTERN STATS")
	print pattern_stats.totalpattern_histogram()
	print("PATTERN STATS")
	#print len(pattern_stats.find_unique_patterns(pattern_drum))
	#print len(pattern_drum)
	#print pattern_stats.find_unique_patterns(pattern_bass)
	#print len(pattern_stats.find_unique_patterns(pattern_bass))
	#print len(pattern_bass)


	global_drum_patt = pattern_stats.find_unique_patterns(pattern_drum)
	global_bass_patt = pattern_stats.find_unique_patterns(pattern_bass)


	#for p in global_drum_patt:
	#	plt.imshow(p.pattern, interpolation='nearest')
	#	plt.show()

	# Find drums/bass patterns for each beat
	beat_drum_patt = pattern_stats.pattern_beat_matching(global_drum_patt)[0]
	beat_bass_patt = pattern_stats.pattern_beat_matching(global_bass_patt)[0]

	# Find unique drum patterns within the full drum-kit
	global_drumkit_patt = pattern_stats.find_unique_drum_patterns(global_drum_patt, target_drums)

	#print "DEBUG : ", len(global_drumkit_patt[0])
	# Associate individual drum patterns to the different drumkit patterns
	for dk in global_drum_patt:
		# instance of drum kit pattern
		tmp_patt = dk.pattern
		#print tmp_patt
		inst_idx = 0
		for target_patt in tmp_patt:
			# individual drum pattern within drum kit pattern
			for inst_patt in global_drumkit_patt[inst_idx]:
				# global pattern instances for each individual instrument
				if np.array_equal(target_patt, inst_patt.pattern):
					# coincident patterns, assign to dk.drum_ids the id of inst_patt
					dk.drum_ids.append(inst_patt.id)
					break
			inst_idx += 1
		print dk.pattern
		print dk.drum_ids


	# Pattern ids for each beat
	beat_drumkit_patt = []
	for n in global_drumkit_patt:
		print n[0].drum_instr
		tmp = pattern_stats.pattern_beat_matching(n)[0]
		beat_drumkit_patt.append(tmp)

	print beat_drumkit_patt
	print (beat_drumkit_patt[0][3])
	print "Clap Patterns in beat 0"
	for n in beat_drumkit_patt[0][0]:
		print n
		print global_drumkit_patt[0][n].pattern

	#print beat_bass_patt
	#print beat_drum_patt





	interlock_bass2drums, interlock_drums2bass = pattern_stats.pattern_interlocking(beat_drum_patt, beat_bass_patt, global_drum_patt, global_bass_patt)

	# Temporal context model
	bass_time_nodes, bass_time_edges = pattern_stats.pattern_continuation(len(drum_files), NBEATS, global_bass_patt, 'bass')
	drum_time_nodes, drum_time_edges = pattern_stats.pattern_continuation(len(drum_files), NBEATS, global_drum_patt, 'drum')
	# Interlocking context model
	drum_nodes, inter_edges_b2d, inter_edges_d2b = pattern_stats.interlocking_graph(interlock_bass2drums, interlock_drums2bass, global_bass_patt, global_drum_patt, beat_bass_patt, beat_drum_patt)
	# Draw graph model
	beat_graph_d2b = GV.draw_beatgraph(bass_time_nodes, bass_time_edges, drum_nodes, drum_time_edges, inter_edges_d2b,draw=True)
	#beat_graph_b2d = GV.draw_beatgraph(bass_time_nodes, bass_time_edges, drum_nodes, drum_time_edges, inter_edges_b2d)


	# Use pickle to store requiered variables for generation
	picklepath = 'rhythmic_analysis/graph_models/pickle/'

	with open(picklepath + 'interd2b.pickle', 'wb') as f:
		# Pickle the 'data' dictionary using the highest protocol available.
		pickle.dump(inter_edges_d2b, f, pickle.HIGHEST_PROTOCOL)
