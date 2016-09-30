inlets= 1;
outlets = 1;
autowatch = 1;

function msg_int(pc)
{
	var d = new Dict("scale_mapping");

	var mapped_pc = d.get(pc);

	outlet(0,mapped_pc);
}