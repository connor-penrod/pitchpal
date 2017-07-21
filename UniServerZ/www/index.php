<?php header('Access-Control-Allow-Origin: *'); ?>
<?php

$directory = str_replace('\UniServerZ\www', '', dirname(__FILE__));

$file = $directory . '\pythonlib\overlay.txt';

if($transcribedText = $_POST['text'])
{
    echo $file . '||||' . dirname(__FILE__);
    file_put_contents($file, $transcribedText);
}
?>