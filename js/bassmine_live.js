inlets = 1;
outlets = 1;
autowatch = 1;

//Globals
var drum_track_id = 1;
var chord_track_id = 2;
var bass_track_id = 0; // to do : set dinamycally


// Global variables for pitch generation
var _root_note = 0; // 
var _octave = 3;

function log() {
  for(var i=0,len=arguments.length; i<len; i++) {
    var message = arguments[i];
    if(message && message.toString) {
      var s = message.toString();
      if(s.indexOf("[object ") >= 0) {
        s = JSON.stringify(message);
      }
      post(s);
    }
    else if(message === null) {
      post("<null>");
    }
    else {
      post(message);
    }
  }
  post("\n");
}
 
log("___________________________________________________");
log("Reload:", new Date);

//--------------------------------------------------------------------
// Clip class
 
function Clip(p) {
  //var path = "live_set view highlighted_clip_slot clip";
  var path = p;
  this.liveObject = new LiveAPI(path);
}
  
Clip.prototype.getLength = function() {
  return this.liveObject.get('length');
}

Clip.prototype.getTrack = function() {
  return this.liveObject.path.split(" ")[2];
}

Clip.prototype.getSlot = function() {
  return this.liveObject.path.split(" ")[4];
}

Clip.prototype._parseNoteData = function(data) {
  var notes = [];
  // data starts with "notes"/count and ends with "done" (which we ignore)
  for(var i=2,len=data.length-1; i<len; i+=6) {
    // and each note starts with "note" (which we ignore) and is 6 items in the list
    var note = new Note(data[i+1], data[i+2], data[i+3], data[i+4], data[i+5]);
    notes.push(note);
  }
  return notes;
}
 
Clip.prototype.getSelectedNotes = function() {
  var data = this.liveObject.call('get_selected_notes');
  return this._parseNoteData(data);
} 

Clip.prototype.getNotes = function(startTime, timeRange, startPitch, pitchRange) {
  if(!startTime) startTime = 0;
  if(!timeRange) timeRange = this.getLength();
  if(!startPitch) startPitch = 0;
  if(!pitchRange) pitchRange = 128;
  
  var data = this.liveObject.call("get_notes", startTime, startPitch, timeRange, pitchRange);
 
  var notes = [];
  // data starts with "notes"/count and ends with "done" (which we ignore)
  for(var i=2,len=data.length-1; i<len; i+=6) {
    // each note starts with "note" (which we ignore) and is 6 items in the list
    var note = new Note(data[i+1], data[i+2], data[i+3], data[i+4], data[i+5]);
    notes.push(note);
  }
  return notes;
}

 
Clip.prototype._sendNotes = function(notes) {
  var liveObject = this.liveObject;
  liveObject.call("notes", notes.length);
  notes.forEach(function(note) {
    liveObject.call("note", note.getPitch(),
                    note.getStart(), note.getDuration(),
                    note.getVelocity(), note.getMuted());
  });
  liveObject.call('done');
}
 
Clip.prototype.replaceSelectedNotes = function(notes) {
  this.liveObject.call("replace_selected_notes");
  this._sendNotes(notes);
}
 
Clip.prototype.setNotes = function(notes) {
  this.liveObject.call("set_notes");
  this._sendNotes(notes);
}

Clip.prototype.selectAllNotes = function() {
  this.liveObject.call("select_all_notes");
}
 
Clip.prototype.replaceAllNotes = function(notes) {
  this.selectAllNotes();
  this.replaceSelectedNotes(notes);
}

// Not working
Clip.prototype.setLoopEnd = function() {
  this.liveObject.call("loop_end", 16);
  this._sendNotes(notes);
}
 
//--------------------------------------------------------------------
// Note class
 
function Note(pitch, start, duration, velocity, muted) {
  this.pitch = pitch;
  this.start = start;
  this.duration = duration;
  this.velocity = velocity;
  this.muted = muted;
}
 
Note.prototype.toString = function() {
  return '{pitch:' + this.pitch +
         ', start:' + this.start +
         ', duration:' + this.duration +
         ', velocity:' + this.velocity +
         ', muted:' + this.muted + '}';
}
 
Note.MIN_DURATION = 1/128;
 
Note.prototype.getPitch = function() {
  if(this.pitch < 0) return 0;
  if(this.pitch > 127) return 127;
  return this.pitch;
}
 
Note.prototype.getStart = function() {
  // we convert to strings with decimals to work around a bug in Max
  // otherwise we get an invalid syntax error when trying to set notes
  if(this.start <= 0) return "0.0";
  return this.start.toFixed(4);
}
 
Note.prototype.getDuration = function() {
  if(this.duration <= Note.MIN_DURATION) return Note.MIN_DURATION;
  return this.duration.toFixed(4); // workaround similar bug as with getStart()
}
 
Note.prototype.getVelocity = function() {
  if(this.velocity < 1) return 1;
  if(this.velocity > 127) return 127;
  return this.velocity;
}
 
Note.prototype.getMuted = function() {
  if(this.muted) return 1;
  return 0;
}

//--------------------------------------------------------------------
//function bang()
//{    
//  var clip = new Clip();
//  var notes = clip.getNotes();
//  var notes = clip.getSelectedNotes();  
//  notes.forEach(function(note){
//    log(note);
//  });

  
  
  //for (var i = 0; i < notes.length; i++) 
  //{
    //notes.push( new Note(32, start_times[i], 0.25, 100, 0) );
  //}



//}

function genPattern()
{
  
  //post("New Pattern");
  //post();
  
  var note_clip = new Dict("clip_notes_live");
  note_clip.import_json("notes.json");
  var notes = [];
  
  var _pitch;
  var _start;
  var _dur;
  var _vel;

  
  for (var i = 0; i < note_clip.getkeys().length; i++) 
  {
    //post("Que pasa??");
    var tmp = note_clip.get(i.toString())
    //post(tmp[1]);
    // Pitch should be determined
    _pitch = tmp[0] + (_root_note + (12 * _octave));
    _start = tmp[1];
    _dur = tmp[2];
    _vel = tmp[3];


    notes.push( new Note(_pitch, _start, _dur, _vel, 0) );
  }
  
  var clip = new Clip("live_set view highlighted_clip_slot clip");
  post(clip.getTrack());post();
  post(clip.getSlot());post();
  ////clip.setNotes(notes);
  ////clip.replaceSelectedNotes(notes);
  if(clip.getTrack() == bass_track_id)
  {
    post("New Bassline");post();
    clip.replaceAllNotes(notes);
  }
  //clip.setLoopEnd();

}

function new_clip()
{
  // CREATE NEW PATTERN
  post("HEYYYYYYY");
  genPattern();
}

function readClip()
{
  var clip = new Clip("live_set view highlighted_clip_slot clip");
  var notes_all = clip.getNotes();
  //var notes = clip.getSelectedNotes();  

  if (clip.getTrack() == drum_track_id)
  {
    post("drums");post();
    //  Only kick notes
    var kick = format_kick_pattern(notes_all);
    //post(kick);post();
    outlet(0,kick);

  }
  else if(clip.getTrack() == chord_track_id)
  {
    post("chords");post();
    //log(notes_all);

  }
  else if(clip.getTrack() == bass_track_id)
  {
    post("bass");post();
  }
  //else
  //{
  //  post("not determined");post();
  //}


}

//parse drums
var kick_note = 36; // default value of 909 & 808 Live clips

function format_kick_pattern(notes)
{
  var kick_onsets = [];

  notes.forEach(function(note){
    //log(note);
    if(note.pitch == kick_note)
    {
      kick_onsets.push(note.start);
    }
  });

  return kick_onsets;
}

function set_kick_note()
{
  drum_track_id = arguments[0];
}

//Update globals
function set_drum_track()
{
  drum_track_id = arguments[0] - 1;
  //post(drum_track_id);post();  
}

function set_chord_track()
{
  chord_track_id = arguments[0] - 1;
  //post(chord_track_id);post();  
}

function set_octave()
{
  _octave = arguments[0];
}

function get_octave()
{
  post(_octave);post();
}

function set_rootnote()
{
  _root_note = arguments[0];
}

function get_rootnote()
{
  post(_root_note);post();
}

