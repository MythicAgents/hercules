function(task, response){
	if(task.status === 'error'){
		return "<pre> Error: untoggle for error message(s) </pre>";
	}
  let rows = [];
  for(let i = 0; i < response.length; i++){
    try{
        let data = JSON.parse(response[i]['response']);
        let row_style = "";
  			let cell_style = {};
		    Object.keys(data).forEach(function(x){
		      let r = data[x];
		      let row_style = "";
		      if(r['name'].includes("powershell")){row_style="background-color:green;color:white"}
		      if(r['name'].includes("defender")){row_style="background-color:red;color:white"}
		      rows.push({"pid": escapeHTML(r['process_id']),
		                 "name": escapeHTML(r['name']),
                         "user": escapeHTML(r['user']),
		                 "arch": escapeHTML(r['architecture']),
		                 "bin_path": escapeHTML(r['bin_path']),
		                 "row-style": row_style,
		                 "cell-style": {"pid":"text-align:center"}
		                 });
		    });
    }
    catch(error){
        "<pre>Error: " + error.toString() + "\n" + JSON.stringify(response, null, 2) + "</pre>";
    }
  }
  return support_scripts['hercules_create_table']([{"name":"pid","size":"2em"},{"name":"arch","size":"2em"},{"name":"name", "size":"10em"},{"name":"user","size":"2em"},{"name":"bin_path","size":"20em"}], rows);
}