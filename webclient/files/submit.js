const $id = i => !!i.toUpperCase? document.getElementById(i) : i
const $ids = (...is) => is.map($id);

const $s = i => document.querySelectorAll(i)

const _r = (r,_) => r

const $require = i => {e=$id(i);e.setAttribute('required', true); return e}

const $unrequire = i => {e=$id(i); e.removeAttribute('required'); return e}

const $disable = i => {e=$id(i); e.setAttribute('disabled', true); return e;}

const $enable = i => {e=$id(i); e.removeAttribute('disabled'); return e;}

const $show = i => {e=$id(i); e.classList.remove('d-none'); return e;}

const $hide = i => {e=$id(i); e.classList.add('d-none'); return e;}

const $toggle = (i, c) => {e=$id(i); e.classList.toggle(c); return e;}

const $cat = (r,f) => r.map(f).join('')
const $set_html = (i, val) => {e=$id(i); e.innerHTML = val; return e}
const $append_html = (i, val) => {e=$id(i); e.innerHTML += val; return e}

var pick_case = (evt, id, patient, protocol, date, acc, filename) => {
	$id('search_box').value = [patient,protocol,date].join('; ');
	$id('search_box').setAttribute("readonly",true);

	$id('patientName').value = patient;
	$id('accession').value = acc;
	$id('taskId').value = filename.split('.').slice(0, -1).join('.')
	$id('protocol').value = protocol;
	$set_html('search_btn','Clear');
	$set_html('search_results', '');
	$hide('search_results_box');
	$enable('submit_btn');
	archive_case = {id:id, filename:filename}
}

batch_cases = {}
var toggle_case = (evt, id, patient_name, protocol, date, accession, filename) => {
	if (id in batch_cases) {
		delete batch_cases[id]
		if (!Object.keys(batch_cases).length) {
			$disable('submit_btn');
		}
		console.log(batch_cases)
		return false;	
	} else {
		batch_cases[id] = {id, filename, patient_name, protocol, date, accession, taskid: filename.split('.').slice(0, -1).join('.')}
		evt.target.innerHTML = "OK"
		$enable('submit_btn');
		$id('batch_box').setAttribute("readonly",true);
		console.log(batch_cases)
		return true;
	}
}

var archive_case = null
var submit_mode = "upload"
var search_offset = 0
var search_page_length = 20
window.addEventListener('load', function() {
    const form = $id('form');
	const progress = $id('progress');


	const uploader = new Resumable({target:'/resumable_upload', chunkSize:1024*1024*10, maxChunkRetries:10, xhrTimeout:5000});

	for (file_input of $s('.custom-file input')) {
		file_input.onchange = e => {
			var file_input = e.target;
			var files = Array.from(file_input.files)
					.map(f=>f.name)
					.join(', ');
			file_input.parentElement.querySelector('.custom-file-label').innerText = files;
		}
	};

	$s('#nav-tab .nav-item').forEach(
		e => {
			e.onclick = (ev) => {
			ev.preventDefault();
			$s('#nav-tab .nav-item').forEach(e=>e.classList.remove('active'))
			$s('#nav-tabContent .tab-pane').forEach(e=>{e.classList.remove('show'); e.classList.remove('active')})
			e.classList.add('active')
			let tab = e.getAttribute('aria-controls')
			$id(tab).classList.add('active')
			$id(tab).classList.add('show')
			if (tab == "nav-upload") {
				submit_mode = "upload"
				window.location.hash = '#upload';
				$enable($require('files'))
				$ids('batch_box','accession_file').map($unrequire)
				$ids('search_box', 'extra_files').map($disable);
			} else {
				$unrequire('files');
				$id('files').value = '';
				$id('extra_files').value = '';
			    $s('.custom-file-label').forEach(e=>e.innerHTML = e.getAttribute('default'))
			    $disable('extra_files');
			}
			if (tab == "nav-archive" && submit_mode != "archive") {
				submit_mode = "archive"
				window.location.hash = '#archive';
			    $enable('search_box');
				$hide('search_results_box');
				$set_html('search_results','');
			}
			if (tab == "nav-batch" && submit_mode != "batch") {
				submit_mode = "batch"
				window.location.hash = '#batch';
				$hide('scan_information_box');
				$ids('patientName', 'taskId').map($unrequire);

				$set_html('search_results','');
				$hide('search_results_box');

				$enable('batch_box');
			} else {
				$ids('patientName', 'taskId').map($require);
				$show('scan_information_box')
				$hide('accessions_missing')
			}
		};
		tab = e.getAttribute('aria-controls')
		if (tab == "nav-upload" && window.location.hash == '#upload') {
			e.click();
		}
		if (tab == "nav-archive" && window.location.hash == '#archive') {
			e.click();
		}
		if (tab == "nav-batch" && window.location.hash == '#batch') {
			e.click();
		}
	})

	var search = async function(needle, offset, endpoint="search") {
	    url = `/${endpoint}?needle=${encodeURIComponent(needle)}&offset=${offset||0}`;
		r = await fetch(url, {
			    method: 'get',
			})
		k = await r.json()
		console.log(k);
		r = k.records;
		search_page_length = r.length;
		if ( r.length == 0 ) {
			if (offset == 0) {
				$set_html('search_results', "<tbody><tr><td>No results found!</tr></td></tbody>")
				$hide('search_prev_btn');
			} else {
				$set_html('search_results', "<tbody><tr><td>No more results found!</tr></td></tbody>")
				$show('search_prev_btn');
			}
			$hide('search_next_btn');
			$show('search_results_box');
			return k;
		}
		$set_html('search_results',
		`<thead><tr><td>Name</td><td>MRN</td><td>ACC</td><td>Protocol</td><td>Date</td><td></td></tr></thead>
		<tbody>
			${$cat(r, a => 
				`<tr>
					<td>${a.patient_name}</td>
					<td>${a.patient_id}</td>
					<td>${a.accession}</td> 
					<td>${a.protocol}</td> 
					<td>${a.acquisition_date}&nbsp;${a.acquisition_time}</td>
					<td style="padding: 0px">
						<div class="form-check form-check-inline">
							<button class="btn btn-primary btn-sm mt-2" 
							onclick="event.preventDefault(); ${submit_mode == 'archive'? 'pick_case' : 'toggle_case'}(event, ${a.id},'${a.patient_name}','${a.protocol}', '${a.acquisition_date}', '${a.accession}','${a.filename}');">Select</button>
						</div>
					</td>
					</tr>`)}
		</tbody>`);
		if (offset > 0) {
			$show('search_prev_btn');
		} else {
			$hide('search_prev_btn');
		}
		if (r.length == 20) {
			$show('search_next_btn');
		} else {
			$hide('search_next_btn');
		}
		$show('search_results_box');
	}
	$id('batch_btn').onclick = async function(e) {
		e.preventDefault();
		e.stopPropagation();
		search_box = $id('batch_box');
		search_offset = 0
		result = await search(search_box.value,0,"batch_search")
		records = result.records
		for (r of records) {
			r.taskid = r.filename.split('.').slice(0, -1).join('.')
			batch_cases[r.id] = r
		}
		if (result.accessions_missing.length) {
			$show('accessions_missing')
			$id('accessions_missing_list').innerHTML = $cat(result.accessions_missing, (acc) => acc+"<br>");
			console.warn(result.accessions_missing)
		}else {
			$hide('accessions_missing')
		}
		if (result.records.length) {
			$enable('submit_btn');
		} else {
			$disable('submit_btn');
		}
	}

	if ($id('search_btn')) {
		$id('search_btn').onclick = function(e) {
		    e.preventDefault();
		    e.stopPropagation();
		    search_box = $id('search_box');
		    if (search_box.getAttribute('readonly')) {
		    	search_box.removeAttribute('readonly');
		    	$set_html('search_btn','Search');
				$disable('submit_btn');
		    	search_box.value = '';
		    	archive_case = null;
		    	return;
		    }
		    search_offset = 0
		    search(search_box.value,0)
		}
	$id('search_next_btn').onclick = function(e) {
		    e.preventDefault();
		    e.stopPropagation();
		    search_box = $id('search_box');
		    search_offset += search_page_length;

		    search(search_box.value, search_offset)
		}
	$id('search_prev_btn').onclick = function(e) {
		    e.preventDefault();
		    e.stopPropagation();
		    search_box = $id('search_box');
		    search_offset -= 20;

		    search(search_box.value, search_offset)
		}
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
			if (!mode_details) {
				return;
			}
			console.log(mode_details);
			if(mode_details['requires_acc']) {
				$id('accession').setAttribute('required',true);
				$id('accession-label').style['font-weight'] = 700;
			} else {
				$id('accession-label').style['font-weight'] = 400;
				$id('accession').removeAttribute('required');
			}
			if(mode_details['request_additional_files']) {
				$show('extra_files_entry');
				if (!$id('files').value) {
					$disable('extra_files_entry')
				} else {
					$enable('extra_files_entry')
				}
			} else {
				$hide('extra_files_entry');
				$id('extra_files').value = '';
			    $id('extra_files_label').innerHTML = $id('extra_files_label').getAttribute('default')
			}

			$s('.mode_param_entry').forEach(
				entry => { 
					if (entry.id == mode_select.id + "_"+mode_select.value+"_param") {
						$show(entry);
						input = entry.getElementsByTagName('input')[0]
						$enable(input);
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
    	} else if (submit_mode == 'batch') {
			submit_form_batch()
		}

		uploader.isComplete = false;
		uploader.wasCanceled = false;
    	const files = [...$id('files').files, ...$id('extra_files').files]
		uploader.addFiles(files);
      }, false);
    
	uploader.on('filesAdded', (file, e)  => {
	    $toggle("progress-outer", "expanded");
	    $disable('submit_btn');
	    $show('cancel_btn');
	    [...form.elements].forEach(field => field.setAttribute("readonly",true));
	    uploader.upload();
	});
	uploader.on('fileProgress', (file, ratio) => {
		progress.style.width = 100*file.progress()+'%';
		progress.textContent = 'Uploading... ' + Math.round(100*file.progress(),2)+'%';
	});
	uploader.on('error', (message,file) => {
		try {
			error = JSON.parse(message);
			uploader.error = error.description
			return
		} catch {}
		uploader.error = message || `unknown error ${message}`;
	})
	uploader.on('beforeCancel', () => uploader.wasCanceled = true);
	// uploader.on('catchAll',(event) => {
	// 	console.log(event);
	// })
	uploader.on('complete', () => {
		if (uploader.isComplete) { // sometimes this gets triggered several times??
			return false; 
		}
		uploader.isComplete = true;
		uploader.files = []
		
		function reset_form() { 
			$toggle("progress-outer", "expanded");
			progress.style.width = '0%';
			$hide('cancel_btn');
	    	$enable('submit_btn');
	    	[...form.elements].forEach(field => field.removeAttribute("readonly"));
			form.classList.remove('was-validated');
		}

		if (uploader.error) {
			console.log("Error:", uploader.error);
			new Notification("Error: "+uploader.error);
			alert(uploader.error);
			reset_form()
			return
		}
		if (uploader.wasCanceled) {
			reset_form();
			return;
		}
		submit_form();
		reset_form();
	});


}, false);
document.addEventListener('click', () => {
	if ("Notification" in window && Notification.permission !== "granted" && Notification.permission !== "denied") {
		Notification.requestPermission()
	};
});

async function submit_form_batch() {
	const form = $id('form');
	const body = new FormData(form);
	body.set('mode',body.get('mode_'+body.get('server')))
	body.delete('mode_'+body.get('server'))

	progress.textContent = 'Finalizing...';
	$toggle(progress, "expanded");

	body.delete('archive_id');
	body.delete('archive_file');
	body.delete('protocol');
	body.delete('accession');
	body.delete('taskid');
	body.delete('patient_name');

	for (var c of Object.values(batch_cases)) {
		body.append('archive_id', c.id);
		body.append('archive_file', c.filename);
		body.append('protocol', c.protocol);
		body.append('accession', c.accession);
		body.append('taskid', c.taskid);
		body.append('patient_name', c.patient_name);
	}
	
	$toggle('progress-outer', "expanded");
	response = await fetch('/submit_tasks_batch', {
	    method: "POST",
	    body: body
	})
	$toggle(progress, "bg-info");

	if (!response.ok) {
		r = await response.json()
		alert("Error: "+r.description);
		throw Error(r.description);
	}
	$toggle('progress-outer', "expanded");
	window.location.reload()
}

async function submit_form(){
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
	$toggle(progress,'bg-info');
	console.log(body);
	response = await fetch(form.action, {
	    method: form.method,
	    body: body
	})
	$toggle(progress,'bg-info');
	if (!response.ok) {
		r = await response.json()
		alert("Error: "+r.description);
		throw Error(r);
	} else {
		new Notification("task submitted");
		window.location.reload()
	}
  }

  $id('accession_file').addEventListener("change", async function() {
	$id('batch_box').value = await this.files[0].text();
  });
  
  $id('files').addEventListener("change", async function () {
  		if (this.files.length == 0 ) {
			$disable('extra_files');
			$id('protocol').value = '';
			return;
  		}
		$id('taskId').value = this.files[0].name.split('.').slice(0, -1).join('.')
		header = await readHeader(this.files[0])
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
		$enable('extra_files');
		$enable('submit_btn');

	}, false);

  async function readHeader(file) {
    var reader = new FileReader();
	arr = await file.slice(0, 11244).arrayBuffer()
	var data = new Uint32Array(arr) // Interpret as a bunch of 32bit uints
	// var preamble = new Uint8Array(arr) // Interpret as a bunch of bytes
	var num_scans,meas_id,file_id,header_start
	var file_format
	if (data[0] < 10000 && data[1] <= 64) { // Looks like a VD format
		file_format = 'VD'
		var num_scans = data[1]; // The number of measurements in this file
		// if (num_scans > 1) { // Only supporting simple files for now
		// 	alert("Only supports dat files with a single scan.");
		// 	return;
		// }
		meas_id = data[2];  // Unused, but this is where they are
		file_id = data[3];
		header_start = data[4]; // Where the header of the first measurement starts 

		// % header_start: points to beginning of header, usually at 10240 bytes
		console.log(num_scans,meas_id,file_id,header_start)
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

	headerBuffer = await file.slice(header_start+19,header_start+header_size).arrayBuffer(); // skip the binary part
	return new Uint8Array(headerBuffer)
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



