#include Speech Recognition.ahk

file := FileOpen("testmanuscript", "r")

manuscript := file.Read()
file.Close()
sentences := []
StringSplit, sentences, manuscript, `n
count = 0
threshold = 2

; split sentence, turn all words to lowercase
StringSplit, words, sentences1, %A_Space%
currentSentence := []
Loop % words0
{
  StringLower, words%A_Index%, words%A_Index%
  StringReplace, words%A_Index%, words%A_Index%, `r
  currentSentence.Push(words%A_Index%)
}

Recognizer := new SpeechRecognizer
;["years ago", "American", "shadow", "Emancipation Proclamation", "next slide", "previous slide", "pitch pal stop"]

currentSentence.Push("next slide")
currentSentence.Push("previous slide")
currentSentence.Push("pitch pal stop")

Recognizer.Recognize(currentSentence)
Recognizer.Listen(True)

if WinExist("PitchPal Demo - Google Slides")
{
  WinActivate
}
MsgBox, Microsoft Speech API has loaded, Pitchpal is ready.

Text := ""
count = 0
lastWord := currentSentence[currentSentence.MaxIndex() - 3]
;begin listening loop
while Text != "pitch pal stop"
{
  Text := Recognizer.Prompt()
  IfEqual, Text, previous slide
  {
    Send, {Backspace}
  }
  IfEqual, Text, next slide
  {
    Send, {Space}
  }
  If (Text = lastWord) and (count > threshold)
  {
    count = 0
    Send, {Space}
  }
  Else If Text != "next slide" and Text != "previous slide" and Text != "pitch pal stop"
  {
    count := count + 1
  }
}
MsgBox, %count%
MsgBox, Pitchpal has stopped.
ExitApp