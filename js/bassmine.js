inlets = 1;

step = 0;

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

	post("Sorted probs")
	post(sort_probs);
	post();
	post("Sorted indices")
	post(sort_idxs);
	post();
	// Array to store cumulative probabilites
	var cum_prob = new Array(probs.length);
	// Compute cumulative probabilities
	for (var i = 1; i <= probs.length ; i++) {
		//post(probs.slice(0, i))
		cum_prob[i-1] = sort_probs.slice(0, i).reduce(function(a, b){ return a + b; });
	}
	post("cumulative:");
	post(cum_prob);
	post();
	// Sample
	for (var i = 0; i < probs.length ; i++) {
		//If U(random number) is < than current cdf value 
		if(U <= cum_prob[i]) return sort_idxs[i];
	}
}


function import()
{
	var d = new Dict("init");

	// an optional 'true' arg to getnames() will get all dictionary names
	// rather than just explicitly named dictionaries
	//var names = d.getnames();
	
	//post("Names of existing dictionaries: " + names);
	//post();	

	// getkeys() will return an array of strings, each string being a key for our dict
	var keys = d.getkeys();
	
	// access the name of a dict object as a property of the dict object
	var name = d.name;

	post_info(name, keys);

	post("Initial patterns:")
	post(d.get("initial").get("pattern"));
	post()
	post("Initial probs:")
	post(d.get("initial").get("prob"));
	post()

	// Initial probabilities
	i_prob = d.get("initial").get("prob");
	i_patt = d.get("initial").get("pattern")
	
	//OUTLET to see prob distribution
	outlet(0,i_prob)

	// Sample probabilities
	post("Chosen pattern")
	// If only one possible pattern avoid computing any sampling
	if (i_prob.length > 1)
	{
		post(i_patt[random_sample(i_prob)])
	}
	else 
	{
		post(i_patt)
	}	
	
	// Random Walk routine
	d = new Dict("model");

	// Get from dictionary the pdf of last chosen pattern 

	//post(d.getkeys());

}


function bang()
{
	post("step:")
	post(step)
	
	import();
	post()

	step = step +1;
	
	// additional functions available for dict:
	
	// x.clone("ark");
	// x.remove("pig");
	// x.clear();
	
}