
<?php
$file = 'C:\Users\Conno\Documents\PitchPal\pitchpal\ahk_lib\overlay.txt';

$transcribedText = $_POST['text'];
echo $transcribedText;
if($transcribedText != "")
{
    file_put_contents($file, $transcribedText);
}
?>