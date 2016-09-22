inlets = 1;
outlets = 3;

step = 0;

autowatch = 1;

var start_times;
var out_patt_id;


function post_info(dictname, keys)
{
	post("Info regarding the dictionary named '", dictname, "': ");
	post();
	post("    Keys: " + keys);
	post();
}

function sortWithIndeces(toSort) {
  for (var i = 0; i < toSort.length; i++) {
    toSort[i] = [toSort[i], i];
  }
  toSort.sort(function(right, left) {
    return left[0] < right[0] ? -1 : 1;
  });
  toSort.sortIndices = [];
  for (var j = 0; j < toSort.length; j++) {
    toSort.sortIndices.push(toSort[j][1]);
    toSort[j] = toSort[j][0];
  }
  return toSort;
}


function random_sample(probs)
{
	// Random value with uniform distribution
	var U = Math.random();
	// Sort probs in descending order
	sort_probs = sortWithIndeces(probs);
	sort_idxs = sort_probs.sortIndices;

	//post("Sorted probs")
	//post(sort_probs);
	//post();
	//post("Sorted indices")
	//post(sort_idxs);
	//post();
	// Array to store cumulative probabilites
	var cum_prob = new Array(probs.length);
	// Compute cumulative probabilities
	for (var i = 1; i <= probs.length ; i++) {
		//post(probs.slice(0, i))
		cum_prob[i-1] = sort_probs.slice(0, i).reduce(function(a, b){ return a + b; });
	}
	//post("cumulative:");
	//post(cum_prob);
	//post();
	// Sample
	for (var i = 0; i < probs.length ; i++) {
		//If U(random number) is < than current cdf value 
		if(U <= cum_prob[i]) return sort_idxs[i];
	}
}



var step;

function genPattern()
{
  step = 0; 		
  var pattern = out_patt_id;
  post("New Pattern");
  post();
  var patt_dict = new Dict("patterns");
  //post(pattern);
  //post(pattern.length);

  // For each value in input create beat pattern
  var pitch_ = 42;
  var dur_ = 0.5;
  start_times = [];
  var tmp;

  for (var i = 0; i < pattern.length; i++) 
  {
    var patt_id = pattern[i];
    var st_tmp = patt_dict.get("patterns").get(patt_id.toString());
    //post(st_tmp);post();post();
    
    if(typeof(st_tmp) == 'object' && st_tmp !== null)
    {
      //post(typeof(st_tmp[0]));post();
      //post(st_tmp.length);post();

      //post(Object.prototype.toString.call(st_tmp));post();

      for (var j = 0; j < st_tmp.length; j++) {
      	//post("object sum");
      	//post(st_tmp[j]+ step);post();
      	start_times.push(st_tmp[j]+ step);
      }
      //post(st_tmp + step );post();
      //start_times.push(st_tmp + step);
    }
    else if(typeof(st_tmp) == 'number')
    {
      //post('test');post(st_tmp + step);post(); 
      start_times.push(st_tmp + step);		
    }

    step++;
  }


  //post(start_times);post(); 
  outlet(2, start_times);
}



function createPattern()
{
	var d = new Dict("init");

	// an optional 'true' arg to getnames() will get all dictionary names
	// rather than just explicitly named dictionaries
	//var names = d.getnames();
	
	//post("Names of existing dictionaries: " + names);
	//post();	
	out_patt_id = [];
	var tmp_id = 0;
	// getkeys() will return an array of strings, each string being a key for our dict
	var keys = d.getkeys();
	
	// access the name of a dict object as a property of the dict object
	var name = d.name;

	//post_info(name, keys);

	//post("Initial patterns:")
	//post(d.get("initial").get("pattern"));
	//post()
	//post("Initial probs:")
	//post(d.get("initial").get("prob"));
	//post()

	// Initial probabilities
	i_prob = d.get("initial").get("prob");
	i_patt = d.get("initial").get("pattern");
	
	//OUTLET to see prob distribution
	outlet(0,i_prob)

	// Sample probabilities
	//post("Chosen pattern")
	// If only one possible pattern avoid computing any sampling
	if (i_prob.length > 1)
	{
		tmp_id = i_patt[random_sample(i_prob)];
		out_patt_id.push(tmp_id);
		//post(tmp_id);
	}
	else 
	{
		out_patt_id.push(i_patt);
		//post(i_patt);
	}	
	//post();
	//post("TEST:");post(out_patt_id); post();
	// Random Walk routine
	d = new Dict("model");

	// Get from dictionary the pdf of last chosen pattern 
	//post(d.get("0").get(out_patt_id[0].toString()).get("pattern"));post();
	//post(d.get("0").get(out_patt_id[0].toString()).get("probs"));post();

	for( var i=0; i<d.getkeys().length; i++)
	{
		var prob = d.get(i.toString()).get(out_patt_id[i].toString()).get("probs")
		var patt = d.get(i.toString()).get(out_patt_id[i].toString()).get("pattern")
		//post(d.getkeys());
		if (prob.length > 1)
		{
			tmp_id = patt[random_sample(prob)];
			out_patt_id.push(tmp_id);
			//post(tmp_id);
		}
		else 
		{
			out_patt_id.push(patt);
			//post(i_patt);
		}	
		//post();
		////post("TEST:");post(out_patt_id); post();
	}
	outlet(1,out_patt_id)

}


function bang()
{
	//post("step:")
	//post(step)

	createPattern();
	post();
	genPattern()

	//step = step +1;
	
	// additional functions available for dict:
	
	// x.clone("ark");
	// x.remove("pig");
	// x.clear();
	
}
