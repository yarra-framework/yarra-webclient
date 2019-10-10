var $id = i => document.getElementById(i)
var $s = i => document.querySelectorAll(i)
var $disable = i => i.setAttribute('disabled', true);
var $disable_id = i => $id(i).setAttribute('disabled', true);

var $enable = i => i.removeAttribute('disabled');
var $enable_id = i => $id(i).removeAttribute('disabled');

var $show = i => i.classList.remove('d-none');
var $show_id = i => $id(i).classList.remove('d-none');

var $hide = i => i.classList.add('d-none');
var $hide_id = i => $id(i).classList.add('d-none');



window.addEventListener('load', function() {
    var form = $id('form');
	var progress = $id('progress');

	var uploader = new Resumable({target:'/resumable_upload', chunkSize:1024*1024*10});

	$disable_id('extra_files');

	function select_server(server) { 
		$s('#modes select').forEach( s => {
			if (s.id == "mode_"+server) {
				$show(s);
				$enable(s);
				s.onchange({target:s})
			} else {
				$hide(s);
				$disable(s);
			}
		})
	} 
	$id('server').onchange = e => select_server(e.target.value);

	$s('#modes select').forEach( mode_select => {
		mode_select.onchange = (e) => {
			$s('.mode_param_entry').forEach(
				entry => { 
					if (entry.id == mode_select.id + "_"+mode_select.value+"_param") {
						$show(entry);
						$enable(entry.getElementsByTagName('input')[0]);
					} else {
						$hide(entry);
						$disable(entry.getElementsByTagName('input')[0]);
					}
				}
			);
		}
	});

    $id('cancel_btn').onclick = () => uploader.cancel();

    form.addEventListener('submit', function(event) {
	    event.preventDefault();
	    event.stopPropagation();
    	var form = event.target;
   		if (form.checkValidity()) {
        	var file = $id('files').files[0]
        	var files = Array.from($id('extra_files').files)
        	files.unshift(file);
			uploader.isComplete = false;
			uploader.wasCanceled = false;
			uploader.addFiles(files);
		} else {
		    form.classList.add('was-validated');
		}
      }, false);
    

	uploader.on('filesAdded', (file, e)  => {
	    $id('progress-outer').classList.toggle("expanded");
	    $disable_id('submit_btn');
	    $show_id('cancel_btn');
	    [...form.elements].forEach(field => field.setAttribute("readonly",true));
	    uploader.upload();
	});
	uploader.on('fileProgress', (file, ratio) => {
		progress.style.width = 100*file.progress()+'%';
		progress.textContent = 'Uploading... ' + Math.round(100*file.progress(),2)+'%';
	});
	uploader.on('error', (message,file) => {
		new Notification(message);
		console.log('error', message, file);
	})
	uploader.on('beforeCancel', () => uploader.wasCanceled = true);

	uploader.on('complete', () => {
		if (uploader.isComplete) { // sometimes this gets triggered several times??
			return false; 
		}
		uploader.isComplete = true;
		function reset_form() { 
			$id('progress-outer').classList.toggle("expanded");
			$hide_id('cancel_btn');
	    	$enable_id('submit_btn');
	    	[...form.elements].forEach(field => field.removeAttribute("readonly"));
			form.classList.remove('was-validated');
		}
		if (uploader.wasCanceled) {
			reset_form();
			return;
		}
		progress.textContent = 'Finalizing...';
		progress.classList.toggle('bg-info');
		submit_form();
		reset_form();
	});


  if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
    Notification.requestPermission()
  };
}, false);

function submit_form(){
	var form = $id('form')
	var body = new FormData(form)		
	body.set('file',body.get('file').name);
	
	extra_files = body.getAll('extra_files');
	body.delete('extra_files');
	for ( file of extra_files ) {
		body.append('extra_files',file.name);
	}
	body.set('mode',body.get('mode_'+body.get('server')))
	body.delete('mode_'+body.get('server'))
	fetch(form.action, {
	    method: form.method,
	    body: body
	}).then( response => {
		resetForm(form);
		$id('progress').classList.toggle('bg-info');
	    if (!response.ok) {
	    	new Notification("submission error");
	        throw Error(response.statusText);
		}
	}).then( res => {
		new Notification("task submitted");
	})
  }

  $id('files').addEventListener("change", function () {
		$id('taskId').value = this.files[0].name.split('.').slice(0, -1).join('.')
		readHeader(this.files[0], function(header){
			try {
				var patient_name = getTagValue(header,'PatientName');
				$id('patientName').value = patient_name;
			} catch(err) {
				var patient_name = null
				$id('patientName').value = "";
			}
			try { 
				var protocol_name = getTagValue(header, 'ProtocolName');
				$id('protocol').value = protocol_name;
			} catch(err) {

			}
			$enable_id('extra_files');
			$enable_id('submit_btn');
		})
	}, false);

  function readHeader(file, onload) {
    var reader = new FileReader();
	reader.readAsArrayBuffer(file.slice(0, 11244)); // This might be too short for some files and fail
	reader.onloadend = function(evt) {
      if (evt.target.readyState == FileReader.DONE) { // DONE == 2
		var data = new Uint32Array(evt.target.result) // Interpret as a bunch of 32bit uints
		var preamble = new Uint8Array(evt.target.result) // Interpret as a bunch of bytes
		var num_scans,meas_id,file_id,header_start
		var file_format
		if (data[0] < 10000 && data[1] <= 64) { // Looks like a VD format
			file_format = 'VD'
			var num_scans = data[1]; // The number of measurements in this file
			// if (num_scans > 1) { // Only supporting simple files for now
			// 	alert("Only supports dat files with a single scan.");
			// 	return;
			// }
    		measID = data[2];  // Unused, but this is where they are
    		fileID = data[3];
    		header_start = data[4]; // Where the header of the first measurement starts 

		    // % header_start: points to beginning of header, usually at 10240 bytes
		    console.log(num_scans,measID,fileID,header_start)
		    // console.log(new TextDecoder("utf-8").decode(new Uint8Array(preamble).slice(0,11240)))
		    //var measOffset = new Uint64Array(data.slice(4,6))[0]
		    //var measLength = new Uint64Array(data.slice(6,8))[0]
		} else {
			file_format = 'VB'
			header_start = 0 // There's only one measurement in VB files, so it starts at 0.
		}
		var header_size = data[header_start/4];
		if (header_size <= 0) {
			alert("Unknown file format.")
			return;
		}

		var headerBlob = file.slice(header_start+19,header_start+header_size); // skip the binary part
		var headerReader = new FileReader();
		headerReader.onload = function(event) {
		    var header = new Uint8Array(event.target.result);
		    onload(header);
		    
		}
		headerReader.readAsArrayBuffer(headerBlob);
   	  }
    }
  }	

function getTagValue(data,tagName,do_replace,start=0) {
  loc = find_tag(data,'ParamString."'+tagName+'"',start);
  if (loc == -1) return -1;

  // Find the braces that surround the tag contents
  braces_begin = data.indexOf(char('{'),loc)+1

  braces_end = data.indexOf(char('}'),loc)

  // looks like } {
  if (braces_begin > braces_end ) throw new Error('Invalid tag detected');

  var tag_contents = data.subarray(braces_begin,braces_end)

  // Find the last quoted thing in the subarray...
  var val_end = tag_contents.lastIndexOf(char('"'))
  if (val_end == -1) return braces_end; // oh, it's just empty, never mind
  var val_begin = tag_contents.lastIndexOf(char('"'),val_end-1)+1
  if (val_begin == -1) throw new Error('Invalid tag detected'); // Can't find the opening quote

  var tag_value = tag_contents.subarray(val_begin,val_end);
  return utf8(tag_value);
  // found_tag_values.add(utf8(tag_value));
  // tag_value.set(asUint8Array(do_replace(val_end-val_begin)));
  // return braces_end+1;
}

function find_tag(data, name, start) {
  var s = start || 0
  var name = asUint8Array(name);
  do {
	  var tag_begin = data.indexOf(char('<'),s)
	  if ( tag_begin == -1 ) return -1
	  var tag_begin_check = data.indexOf(char('<'),tag_begin+1)
	  var tag_end = data.indexOf(char('>'),tag_begin+1)
	  if (tag_begin_check > -1 && tag_begin_check < tag_end) {
	  	throw new Error('Invalid tag detected');
	  }
	  var tag_value = new Uint8Array(data.slice(tag_begin+1,tag_end))
	  // console.log("tag_value", tag_value, new TextDecoder("utf-8").decode(tag_value))
	  // console.log("name", name, new TextDecoder("utf-8").decode(name))
	  s = tag_end+1
	  if (arrays_equal(tag_value,name)) {
	  	return tag_end
	  }
   } while (tag_begin != -1)
   return -1
}

function utf8(t){
	return new TextDecoder("utf-8").decode(t)
}

function asUint8Array(input) {
  if (input instanceof Uint8Array) {
    return input;
  } else if (typeof(input) === 'string') {
    // This naive transform only supports ASCII patterns. UTF-8 support
    // not necessary for the intended use case here.
    var arr = new Uint8Array(input.length);
    for (var i = 0; i < input.length; i++) {
      var c = input.charCodeAt(i);
      if (c > 127) {
        //throw new TypeError("Only ASCII patterns are supported");
      }
      arr[i] = c;
    }
    return arr;
  } else {
    // Assume that it's already something that can be coerced.
    return new Uint8Array(input);
  }
}

function arrays_equal(dv1, dv2)
{
    if (dv1.length != dv2.length) return false;
    for (var i=0; i < dv1.length; i++)
    {
        if (dv1[i] != dv2[i]) return false;
    }
    return true;
}
function char(c) {
	return c.charCodeAt(0)
}



