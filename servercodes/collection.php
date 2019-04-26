<?php

$target_dir = "collection/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = pathinfo($target_file,PATHINFO_EXTENSION);
echo "qweqw";
//if (file_exists($target_file)) {

//    echo "Sorry, file already exists.";
//    $uploadOk = 0;
//}

if ($_FILES["fileToUpload"]["size"] > 50000000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}


if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
	echo "Data has been collected successfully";
	
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
