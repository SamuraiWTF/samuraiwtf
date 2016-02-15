function get_content(f){
	 return (f.contentDocument) ? f.contentDocument : f.contentWindow.document;
}

function is_visited(l){
	var dummy = document.getElementById("HIDDEN_FRAME");

	if (!dummy){
		dummy = document.createElement("iframe");
		dummy.style.visibility = "hidden";
		dummy.id = "HIDDEN_FRAME";
		document.body.appendChild(dummy);	

		var dummycontent = get_content(dummy);
		var style  = "<style>a:visited{width:0px};</style>";
		dummycontent.open();
		dummycontent.write(style);
		dummycontent.close();
	} else {
		var dummycontent = get_content(dummy);	
	}

	var dummylink = dummycontent.createElement("a");
	dummylink.href = l;
	dummycontent.body.appendChild(dummylink);

	if (dummylink.currentStyle) {
		visited = dummylink.currentStyle["width"];
	}	else {
		visited = dummycontent.defaultView.getComputedStyle(dummylink, null).getPropertyValue("width");
	}

	return (visited == "0px");
}
	
function check_list(rawurls) {
	var result = "";
	var urllist = rawurls.split(/!/);
	for (var i=0; i < urllist.length; i++) {
		result += urllist[i] + ': ';
		if(is_visited(urllist[i])) {
			result += 'trueCR'; 
		} else {
			result += 'falseCR'; 			
		}
	}
	return result;
}
	
return_result(result_id, check_list('RAWURLS'));

