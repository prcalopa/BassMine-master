autowatch=1;
outlets=1;

//post(this.patcher.getnamed("var_beat1"));
var toggles = [];
var root_name = "var_beat";


for (var i = 0; i < 8; i++) {
	var obj_name = root_name.concat(i.toString());
	post(obj_name);
	toggles.push(this.patcher.getnamed(obj_name));
}

//post(toggles[0].getvalueof())


//output a variation mask ==> if toggle==1 then -1 else 1
function genVariationMask()
{

	var var_mask = []

	for (var i = 0; i < toggles.length; i++) 
	{
		var tmp_val = toggles[i].getvalueof();
		if (tmp_val == 0) 
		{
			var_mask.push(1)
		} 
		else 
		{
			var_mask.push(-1)
		}
	}
	outlet(0,var_mask)

}