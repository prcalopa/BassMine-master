inlets= 2;
outlets = 2;
autowatch = 1;

function createScale(){

	var d = new Dict("scale_mapping");
	//post(arguments[1]);
	var tones = arguments;
	var num_tones = arguments.length;
	post(num_tones);post();

	var scale_map = Array(12);
	
	for (var i = 0; i < num_tones; i++) {
		scale_map[tones[i]] = tones[i];
	}
	

	for (var i = 0; i < 12; i++) {
		if (typeof scale_map[i] == 'undefined') {
			scale_map[i] = scale_map[i-1];
		}

		d.set(i, scale_map[i]);
	}
	post(scale_map);post();

	



}