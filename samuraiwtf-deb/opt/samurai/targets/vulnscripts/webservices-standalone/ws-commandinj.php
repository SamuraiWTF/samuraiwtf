<?php
// Pull in the NuSOAP code
require_once('lib/nusoap.php');
// Create the server instance
$server = new soap_server();
// Initialize WSDL support
$server->configureWSDL('commandinjwsdl', 'urn:commandinjwsdl');
// Register the method to expose
$server->register('commandinj',                // method name
    array('command' => 'xsd:string'),        // input parameters
    array('return' => 'xsd:string'),      // output parameters
    'urn:commandinjwsdl',                      // namespace
    'urn:commandinjwsdl#commandinj',                // soapaction
    'rpc',                                // style
    'encoded',                            // use
    'Returns the results of a command'            // documentation
);
// Define the method as a PHP function
function commandinj($command) {
	exec($command, $output);
	$results = "";
	while (list($key, $val) = each($output)): 
		$results = $results . $val;
	endwhile;
        return $results;
}
// Use the request to (try to) invoke the service
$HTTP_RAW_POST_DATA = isset($HTTP_RAW_POST_DATA) ? $HTTP_RAW_POST_DATA : '';
$server->service($HTTP_RAW_POST_DATA);
?>
