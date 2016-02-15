<?php
// Pull in the NuSOAP code
require_once('lib/nusoap.php');
// Create the server instance
$server = new soap_server();
// Initialize WSDL support
$server->configureWSDL('sqliwsdl', 'urn:sqliwsdl');
// Register the method to expose
$server->register('sqli',                // method name
    array('name' => 'xsd:string'),        // input parameters
    array('return' => 'xsd:string'),      // output parameters
    'urn:sqliwsdl',                      // namespace
    'urn:sqliwsdl#sqli',                // soapaction
    'rpc',                                // style
    'encoded',                            // use
    'Queries the database of contacts'            // documentation
);
// Define the method as a PHP function
function sqli($name) {
	// Make a MySQL Connection
	mysql_connect("localhost", "root", "samurai") or die(mysql_error());
	mysql_select_db("sqli") or die(mysql_error());

	// Retrieve all the data from the "example" table
	$result = mysql_query("SELECT * FROM Customers WHERE fname = '".$name."';") or die(mysql_error());
	
	while($row = mysql_fetch_array( $result )) {
	// Print out the contents of the entry 

	$results = "Name: ".$row['fName']." ".$row['lName'];
	$results = $results . " Phone: ".$row['phone'];

	}
        return $results;
}
// Use the request to (try to) invoke the service
$HTTP_RAW_POST_DATA = isset($HTTP_RAW_POST_DATA) ? $HTTP_RAW_POST_DATA : '';
$server->service($HTTP_RAW_POST_DATA);
?>
