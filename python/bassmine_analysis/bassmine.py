# Read Midi Folders from style
import madmom
import numpy as np
import utility_functions as uf
import markov
import pickle
import json
# Extract data from midi:
#   binary rhythms
#   markov:
#       temporal bass
#       kick - bass interlocking


def write2pickle(name,data, path='models/'):
	#path = 'rhythmic_analysis/graph_models/pickle/'

	with open(path + name + '.pickle', 'wb') as f:
		# Pickle the 'data' dictionary using the highest protocol available.
		pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)


def write2json(name, data, path='models/'):
	"""
	Write numpy array to json file
	:param name: name of the file
	:param data: array to encode
	:param path: path where the json file will be stored
	:return:
	"""
	with open(name + '.json', 'w') as outfile:
		json.dump(data.tolist(), outfile)


def quantize_pattern(pattern):
	RES = 4

	noBeats_bass = uf.numberOfBeats(pattern)  # Bass files length set the global length of analysis
	print '\n# of beats: ', noBeats_bass
	#beat_subdiv = np.arange(start=0, step=0.25, stop=(noBeats_bass * RES) - 1)
	subdiv_aux = np.array([0., 0.25, 0.5, 0.75])
	# Matrix to store the binary representation of the midi files
	# Basslines -> 1 matrix
	rhythm = np.zeros((noBeats_bass, RES), dtype=int)

	for o in pattern:
		# quantize to the closest subdivision
		i, d = divmod(o, 1)  # i = row(beat number) , d = column (beat subdivision)
		d_ = (abs(subdiv_aux - d)).argmin()
		rhythm[int(i), d_] = 1
	return rhythm


def translate_rhythm(rhythm):

	id = []

	for beat in rhythm:
		id.append((beat[0] * 8) + (beat[1] * 4) + (beat[2] * 2) + beat[3])
	return id


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

	# Markov analysis test
	model = markov.MarkovModel(16)
	kick_patterns = []

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
		bass_rhythm = quantize_pattern(onset_bass)
		print(bass_rhythm)
		bass_id = translate_rhythm(bass_rhythm)
		model.add_temporal(bass_id)

		# Read Drum files
		#
		drum_midi = madmom.utils.midi.MIDIFile.from_file(match_file)
		drum_midi.note_time_unit = 'b'
		# Filter kick notes
		onset_kick = []
		kick = 36
		for event in drum_midi.notes:
			#print event
			if int(event[1]) == kick:
				onset_kick.append(event[0])
		# Quantize
		kick_rhythm = quantize_pattern(onset_kick)
		print kick_rhythm
		# Translate
		kick_id = translate_rhythm(kick_rhythm)
		kick_patterns.append(kick_id)
		# Update interlocking model
		model.add_interlocking(kick_id, bass_id)

		file_it += 1

	return model, kick_patterns

