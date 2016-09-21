# Generate pattern dict
#
# 1st convert to binary(4dig)
# Assign beat start time [0,0.25,0.5,0.75]
# store array
import json

start_times = [0,0.25,0.5,0.75]

patt_dict = dict()
for p in range(16):
	# Binary pattern
	binpatt = format(p, '04b')
	st = []
	for i in range(len(start_times)):
		if binpatt[i] == '1':
			st.append(start_times[i])
	val = st
	patt_dict[str(p)] = val


print patt_dict

path = '../../models/'
name = 'pattern_dict'
data = patt_dict

with open(path + name + '.json', 'w') as outfile:
		json.dump(data, outfile)