<?php header('Access-Control-Allow-Origin: *'); ?>
<?php

$file = 'C:\Users\Conno\Documents\PitchPal\pitchpal\ahk_lib\overlay.txt';

if($transcribedText = $_POST['text'])
{
    file_put_contents($file, $transcribedText);
}
?>