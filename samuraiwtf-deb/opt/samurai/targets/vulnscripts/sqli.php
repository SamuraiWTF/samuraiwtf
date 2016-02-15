<?php

if (!isset($_GET["name"])) {
	echo('<form method="GET" action="sqli.php">
<input type="text" name="name">
<input type="submit">
</form>');
} else {
	mysql_connect("localhost", "root", "samurai") or die(mysql_error());
	mysql_select_db("dvwa");
	$result = mysql_query("SELECT * from users WHERE first_name = '".$_GET["name"]."';") or die(mysql_error());

while($row = mysql_fetch_array($result)) {
echo "Name: ".$row["first_name"]." ".$row['last_name'];
}
}
?>
