import numpy as np


def numberOfBeats(data):
	"""
	Number of beats of a midi file
	:param data: number of last beat position of the midi file  np.array[()] 1D
	:return: number of beats in the midi file. The size is approximated to be proportional to 4 beats.
	"""
	aux = np.array([4, 8, 16, 32, 64, 128, 256])
	idx = abs(max(data) - aux).argmin()
	nob = aux[idx]
	return nob

def indices(a, func):
    # UF.indices(tmp_sv, lambda x: x <= target_sv[i])
    return [i for (i, val) in enumerate(a) if func(val)]
