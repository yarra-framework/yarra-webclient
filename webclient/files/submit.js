const $id = i => document.getElementById(i)
const $s = i => document.querySelectorAll(i)
const $disable = i => i.setAttribute('disabled', true);
const $disable_id = i => $id(i).setAttribute('disabled', true);

const $enable = i => i.removeAttribute('disabled');
const $enable_id = i => $id(i).removeAttribute('disabled');

const $show = i => i.classList.remove('d-none');
const $show_id = i => $id(i).classList.remove('d-none');

const $hide = i => i.classList.add('d-none');
const $hide_id = i => $id(i).classList.add('d-none');

const $cat = (r,f) => r.map(f).join('')
const $set_html = (id, val) => $id(id).innerHTML = val;

var pick_case = (id, patient, protocol, date, acc, filename) => {
	$id('search_box').value = [patient,protocol,date].join('; ');
	$id('search_box').setAttribute("readonly",true);

	$id('patientName').value = patient;
	$id('accession').value = acc;
	$id('taskId').value = filename.split('.').slice(0, -1).join('.')
	$id('protocol').value = protocol;
	$set_html('search_btn','Clear');
	$set_html('search_results', '');
	$hide_id('search_results_box');
	$enable_id('submit_btn');
	archive_case = {id:id, filename:filename}
}

var archive_case = null
var submit_mode = "upload"
window.addEventListener('load', function() {
    const form = $id('form');
	const progress = $id('progress');

	const uploader = new Resumable({target:'/resumable_upload', chunkSize:1024*1024*10});


	$disable_id('extra_files');
	$s('#nav-tab .nav-item').forEach(
		e => e.onclick = (ev) => {
			ev.preventDefault();
			$s('#nav-tab .nav-item').forEach(e=>e.classList.remove('active'))
			$s('#nav-tabContent .tab-pane').forEach(e=>{e.classList.remove('show'); e.classList.remove('active')})
			e.classList.add('active')
			let tab = e.getAttribute('aria-controls')
			$id(tab).classList.add('active')
			$id(tab).classList.add('show')
			console.log(tab);
			if (tab == "nav-upload") {
				submit_mode = "upload"
				$id('files').setAttribute('required', true);
				$enable_id('files');
			    $disable_id('search_box');
			} else if (tab == "nav-archive") {
				submit_mode = "archive"
				$disable_id('files');
				$id('files').removeAttribute('required');
				$id('files').value = '';
				$id('extra_files').value = '';
			    $s('.custom-file-label').forEach(e=>e.innerHTML = e.getAttribute('default'))
			    $disable_id('extra_files');
			    $enable_id('search_box');
			}

		})


	$id('search_btn').onclick = function(e) {
	    e.preventDefault();
	    e.stopPropagation();
	    search_box = $id('search_box');
	    if (search_box.getAttribute('readonly')) {
	    	search_box.removeAttribute('readonly');
	    	$set_html('search_btn','Search');
			$disable_id('submit_btn');
	    	search_box.value = '';
	    	archive_case = null;
	    	return;
	    }
	    url = "/search?needle="+encodeURIComponent(search_box.value)
		fetch(url, {
			    method: 'get',
			}).then(r=>r.json()).then( r => {$set_html('search_results',`
		<tbody>
		    ${$cat(r, a => `<tr><td>${a.patient_name}</td>
		    	 <td>${a.accession}</td> <td>${a.protocol}</td> 
		    	 <td>${a.acquisition_date}&nbsp;${a.acquisition_time}</td>
		    	 <td>
					<div class="form-check form-check-inline mt-2">
					  <button class="btn btn-primary" 
					  	onclick="event.preventDefault(); pick_case(${a.id},'${a.patient_name}','${a.protocol}', '${a.acquisition_date}', '${a.accession}','${a.filename}');">Select</button>
					</div>
				 </td>
		    	 </tr>`)}
		</tbody>`);
		$show_id('search_results_box');
		})
	}


	const select_server = server => {
		console.log(server)
		console.log(servers[server])
		$s('#modes select').forEach( s => {
			if (s.id == "mode_"+server) {
				$show(s);
				$enable(s);
				s.onchange({target:s})
			} else {
				$hide(s);
				$disable(s);
			}
		});
	}

	$id('server').onchange = e => select_server(e.target.value);

	$s('#modes select').forEach( mode_select => {
		mode_select.onchange = e => {
			mode_details = (servers[$id('server').value][e.target.value]);
			if(mode_details.request_additional_files) {
				$show_id('extra_files_entry');
				if (!$id('files').value) {
					$disable_id('extra_files_entry')
				} else {
					$enable_id('extra_files_entry')
				}
			} else {
				$hide_id('extra_files_entry');
				$id('extra_files').value = '';
			    $id('extra_files_label').innerHTML = $id('extra_files_label').getAttribute('default')
			}

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
	select_server($id('server').value);

    $id('cancel_btn').onclick = () => uploader.cancel();

    form.addEventListener('submit', e => {
	    e.preventDefault();
	    e.stopPropagation();
    	const form = e.target;
   		if (!form.checkValidity()) {
   			form.classList.add('was-validated');
   			return;
   		}
    	if (submit_mode == 'archive') {
   			//$id('progress-outer').classList.toggle("expanded");
			// progress.style.width = '100%';
			// [...form.elements].forEach(field => field.setAttribute("readonly",true));
			submit_form()
			//reset_form()
    	}

		uploader.isComplete = false;
		uploader.wasCanceled = false;
    	const files = [...$id('files').files, ...$id('extra_files').files]
		uploader.addFiles(files);
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
		error = JSON.parse(message);
		uploader.error = error.description ||  message || 'unknown error';
	})
	uploader.on('beforeCancel', () => uploader.wasCanceled = true);
	uploader.on('catchAll',(event) => {
		console.log(event);
	})
	uploader.on('complete', () => {
		if (uploader.isComplete) { // sometimes this gets triggered several times??
			return false; 
		}
		uploader.isComplete = true;
		uploader.files = []
		if (uploader.error) {
			console.log("Error:", uploader.error);
			new Notification("Error: "+uploader.error);
			reset_form()
			return
		}
		function reset_form() { 
			$id('progress-outer').classList.toggle("expanded");
			progress.style.width = '0%';
			$hide_id('cancel_btn');
	    	$enable_id('submit_btn');
	    	[...form.elements].forEach(field => field.removeAttribute("readonly"));
			form.classList.remove('was-validated');
		}
		if (uploader.wasCanceled) {
			reset_form();
			return;
		}
		submit_form();
		reset_form();
	});


  if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
    Notification.requestPermission()
  };
}, false);

function submit_form(){
	const form = $id('form');
	const progress = $id('progress');
	const body = new FormData(form);
	if (submit_mode == 'upload') {
		body.set('file',body.get('file').name);
		extra_files = body.getAll('extra_files');
		body.delete('extra_files');
		for ( const file of extra_files ) {
			body.append('extra_files',file.name);
		}
	} else if (submit_mode == 'archive') {
		body.set('archive_id', archive_case.id)
		body.set('archive_file', archive_case.filename)
	}
	body.set('mode',body.get('mode_'+body.get('server')))
	body.delete('mode_'+body.get('server'))
	
	progress.textContent = 'Finalizing...';
	progress.classList.toggle('bg-info');
	console.log(body);
	fetch(form.action, {
	    method: form.method,
	    body: body
	}).then( response => {
		progress.classList.toggle('bg-info');
	    if (!response.ok) {
	    	response.json().then(r=>{
		        alert("Error: "+r.description);
	    	})
	        throw Error(r);
		}
	}).then( res => {
		new Notification("task submitted");
		if (submit_mode == 'archive') {
			window.location.reload()
		}
	})
  }

  $id('files').addEventListener("change", function () {
  		if (this.files.length == 0 ) {
			$disable_id('extra_files');
			$id('protocol').value = '';
			return;
  		}
		$id('taskId').value = this.files[0].name.split('.').slice(0, -1).join('.')
		readHeader(this.files[0], function(header){
			try {
				$id('patientName').value = getTagValue(header,'PatientName');
			} catch(err) {
				$id('patientName').value = "";
			}
			try { 
				$id('protocol').value = getTagValue(header, 'ProtocolName');
			} catch(err) {
				console.log(err)
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
			// alert("Unknown file format.")
			// return;
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

  const tag_contents = data.subarray(braces_begin,braces_end)

  // Find the last quoted thing in the subarray...
  const val_end = tag_contents.lastIndexOf(char('"'))
  if (val_end == -1) return braces_end; // oh, it's just empty, never mind
  const val_begin = tag_contents.lastIndexOf(char('"'),val_end-1)+1
  if (val_begin == -1) throw new Error('Invalid tag detected'); // Can't find the opening quote

  const tag_value = tag_contents.subarray(val_begin,val_end);
  return utf8(tag_value);
  // found_tag_values.add(utf8(tag_value));
  // tag_value.set(asUint8Array(do_replace(val_end-val_begin)));
  // return braces_end+1;
}

function find_tag(data, name_, start) {
  var s = start || 0
  const name = asUint8Array(name_);
  let tag_begin = -1;
  do {
	  tag_begin = data.indexOf(char('<'),s)
	  if ( tag_begin == -1 ) return -1
	  let tag_begin_check = data.indexOf(char('<'),tag_begin+1)
	  let tag_end = data.indexOf(char('>'),tag_begin+1)
	  if (tag_begin_check > -1 && tag_begin_check < tag_end) {
	  	throw new Error('Invalid tag detected');
	  }
	  let tag_value = new Uint8Array(data.slice(tag_begin+1,tag_end))
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
    for (let i = 0; i < input.length; i++) {
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
    for (let i=0; i < dv1.length; i++)
    {
        if (dv1[i] != dv2[i]) return false;
    }
    return true;
}
function char(c) {
	return c.charCodeAt(0)
}



