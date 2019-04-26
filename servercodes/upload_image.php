<?php

function getUserIpAddr(){
	if(!empty($_SERVER['HTTP_CLIENT_IP'])){
		$ip = $_SERVER['HTTP_CLIENT_IP'];
	}elseif(!empty($_SERVER['HTTP_X_FORWARDED_FOR'])){
		$ip = $_SERVER['HTTP_X_FORWARDED_FOR'];
	}else{
		$ip = $_SERVER['REMOTE_ADDR'];
	}
	return $ip;
}

$target_dir = "image/";
$name = basename($_FILES["fileToUpload"]["name"]);
$file_name = substr(strrchr($name,':'),1);
$target_file = $target_dir . "IMG".$file_name;
$uploadOk = 1;
$imageFileType = pathinfo($target_file,PATHINFO_EXTENSION);

if (file_exists($target_file)) {

    echo "Sorry, file already exists.";
    $uploadOk = 0;
}

if ($_FILES["fileToUpload"]["size"] > 50000000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}


if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
	$hostname = 'localhost';
	$username = 'root';
	$password = 'advbird123';
	$database = 'image_database';

	$con = mysqli_connect($hostname, $username, $password, $database);

	$lat = substr($name,0,strpos($name,':'));
	$sub = substr($name,strpos($name,':')+1); 
	$long = substr($sub,0,strpos($sub,':'));
	$date = date('d/m/Y');
	$time = date('H:i:s');
	$ipaddress = getUserIpAddr();

	$output = system('./con_image.sh newenv '."IMG".$file_name, $retval);

	$sql = "insert into info(ipaddress, longitude, latitude, date, time, image_source, classifier) values ('$ipaddress', '$long', '$lat', '$date', '$time', '$target_file', '$output')";
	mysqli_query($con, $sql);
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
