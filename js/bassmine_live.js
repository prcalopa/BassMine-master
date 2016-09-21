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
 
function Clip() {
  var path = "live_set view highlighted_clip_slot clip";
  this.liveObject = new LiveAPI(path);
}
  
Clip.prototype.getLength = function() {
  return this.liveObject.get('length');
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
function bang()
{    
  var clip = new Clip();
  var notes = clip.getNotes();
  var notes = clip.getSelectedNotes();  
  notes.forEach(function(note){
    log(note);
  });

  var notes = [];
  notes.push( new Note(60, 0, 1, 100, 0) );
  notes.push( new Note(64, 1, 1, 100, 0) );
  notes.push( new Note(67, 2, 1, 100, 0) );
 
  var clip = new Clip();
  //clip.setNotes(notes);
  //clip.replaceSelectedNotes(notes);
  clip.replaceAllNotes(notes);
} 



function list()
{

  var pattern = arguments;
  post("New Pattern");
  post();
  var d = new Dict("patterns");
  //post(pattern);
  //post(pattern.length);

  // For each value in input create beat pattern
  var pitch_ = 42;
  var dur_ = 0.5;
  var start_times = [];

  for (var i = 0; i < pattern.length; i++) 
  {
    var patt_id = pattern[i];
    var st_tmp = d.get("patterns").get(patt_id.toString());
    
    if(patt_id>0)
    {
      for(var j = 0; j<st_tmp.length; j++)
      {
        
        start_times.push(st_tmp[j] + i); 
          //post(st_tmp[j] + i)
      } 
      post(st_tmp);post();
    }
  }


  post(start_times) 

}
