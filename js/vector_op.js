autowatch = 1;
inlets = 2;

var curr_pattern;
var var_mask;
var output;

function list()
{
	if(inlet == 0)
	{
		var_mask = []
		//post(arguments[0]);post("\n")
		for (var i = 0; i < arguments.length; i++) {
			var_mask.push(arguments[i])
		}
		mask();
	}
	else if(inlet == 1)
	{
		curr_pattern = []
		//post(arguments[0]);post("\n")
		for (var i = 0; i < arguments.length; i++) {
			curr_pattern.push(arguments[i])
		}
	}	
}

function mask()
{
	output = []
	for (var i = 0; i < curr_pattern.length; i++) {
		output.push(curr_pattern[i] * var_mask[i])
	}
	outlet(0, output)
}