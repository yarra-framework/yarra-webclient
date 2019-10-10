  window.addEventListener('load', function() {
    var forms = document.getElementsByClassName('needs-validation');
	var uploader = new Resumable({target:'/resumable_upload', chunkSize:1024*1024*10});
	var progress = document.getElementById('progress');

	function select_server(server) { 
		Array.from(document.querySelectorAll('#modes select')).forEach( (e) => {
			if (e.id == "mode_"+server) {
				e.classList.remove('d-none');
				e.removeAttribute('disabled');
			} else {
				e.classList.add('d-none');
				e.setAttribute('disabled', true);
			}
		})
	} 
	document.getElementById('server').onchange = function(e) {
		select_server(e.target.value);
	}
	Array.from(document.querySelectorAll('#modes select')).forEach( (e) => {
		e.onchange = function(e) {
			Array.from(document.querySelectorAll('.mode_param_entry input')).forEach( (e) => {
				e.setAttribute('disabled', true);
			});
			Array.from(document.querySelectorAll('.mode_param_entry')).forEach( (e) => {
				e.classList.add('d-none');
			});

			id = e.target.id + "_"+e.target.value+"_param";
			param = document.getElementById(id);
			console.log(id,param);
			if (param) {
				param.classList.remove('d-none')
				param.querySelectorAll('input')[0].removeAttribute('disabled');
			}
		}
	});

	  if (!("Notification" in window)) {
	  }  // Let's check whether notification permissions have already been granted
	  else if (Notification.permission === "granted") {
	  }  // Otherwise, we need to ask the user for permission
	  else if (Notification.permission !== "denied") {
	    Notification.requestPermission().then(function (permission) {
	      // If the user accepts, let's create a notification
	      if (permission === "granted") {
	        var notification = new Notification("Hi there!");
	      }
	    });
	  }
    document.getElementById('cancel_btn').onclick = function() {
    	uploader.cancel();
    };	
    var validation = Array.prototype.filter.call(forms, function(form) {
      form.addEventListener('submit', function(event) {
  		try {
	   		if (form.checkValidity()) {
	        	var file = document.getElementById('files').files[0]
	        	var files = Array.from(document.getElementById('extra_files').files)
	        	files.unshift(file);
				uploader.isComplete = false;
				uploader.wasCanceled = false;
				uploader.addFiles(files);
			} else {
			    form.classList.add('was-validated');
			}
		} finally {
		    event.preventDefault();
		    event.stopPropagation();
		}
      }, false);
    });

	uploader.on('filesAdded', function(file, e){
	    document.getElementById('progress-outer').classList.toggle("expanded");
	    document.getElementById('submit_btn').disabled = true;
	    document.getElementById('cancel_btn').classList.toggle('d-none');
	    Array.from(form.elements).forEach(field => field.setAttribute("readonly",true));
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
	uploader.on('beforeCancel', () => {
		console.log('was canceled');
		uploader.wasCanceled = true;
	})

	uploader.on('complete', () => {
		if (uploader.isComplete) { // sometimes this gets triggered several times??
			return false; 
		}
		uploader.isComplete = true;
		function resetForm(form) { 
			document.getElementById('progress-outer').classList.toggle("expanded");
			document.getElementById('cancel_btn').classList.toggle('d-none');
	    	document.getElementById('submit_btn').disabled = false;
	    	Array.from(form.elements).forEach(field => field.removeAttribute("readonly"));
		}
		var form = document.getElementById('form')
		if (uploader.wasCanceled) {
			resetForm(form);
			return;
		}
		progress.textContent = 'Finalizing...';
		progress.classList.toggle('bg-info');
		submit_form();
		resetForm(form);
	});



  }, false);

function submit_form(){
	var form = document.getElementById('form')
	var body = new FormData(form)		
	body.set('file',body.get('file').name);
	
	extra_files = body.getAll('extra_files');
	body.delete('extra_files');
	for (i=0;i<extra_files.length;i++){
		body.append('extra_files',extra_files[i].name);
	}
	body.set('mode',body.get('mode_'+body.get('server')))


	document.getElementById('extra_files').files
	body.delete('mode_'+body.get('server'))
	fetch(form.action, {
	    method: form.method,
	    body: body
	}).then((response) => {
		resetForm(form);
		document.getElementById('progress').classList.toggle('bg-info');
	    if (!response.ok) {
	    	new Notification("submission error");
	        throw Error(response.statusText);
		}
	}).then( (res) => {
		new Notification("task submitted");
	})
  }

  document.querySelector('#files').addEventListener("change", function () {
		document.getElementById('taskId').value = this.files[0].name.split('.').slice(0, -1).join('.')
		readHeader(this.files[0], function(header){
			try {
				var patient_name = getTagValue(header,'PatientName');
				console.log(patient_name)
				document.getElementById('patientName').value = patient_name;
			} catch(err) {
				var patient_name = null
				document.getElementById('patientName').value = "";
			}
			try { 
				var protocol_name = getTagValue(header, 'ProtocolName');
				document.getElementById('protocol').value = protocol_name;
			} catch(err) {

			}
			document.getElementById('extra_files').removeAttribute('disabled');
			document.getElementById('submit_btn').removeAttribute('disabled');
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



