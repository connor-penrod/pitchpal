#include %A_ScriptDir%\SpeechRecognition.ahk

 ; Utility function for retrieving the index on a specified string element
ReturnIndex(key, list)
{
  Loop, % list.Length()
  {
    if (list[A_Index] = key)
    {
      return % A_Index
    }
  }
  return -1
}

paramCount = %0%
if (paramCount != 2)
{
  MsgBox, Invalid number of parameters.
  ExitApp
}

mode = %2%
fileName = %1%
SetTitleMatchMode 2

 ; Try to open keyword list
try
{
  file := FileOpen(fileName, "r")
  manuscript := file.Read()
  file.Close()
}
catch e
{
  MsgBox, The manuscript file '%fileName%' could not be opened.
  ExitApp
}

; split sentences, turn all words to lowercase

sentences := []
wordList := []
keywordList := []
repeatList := []

StringSplit, sentences, manuscript, `n
Loop % sentences0
{
  StringSplit, words, sentences%A_Index%, %A_Space%
  Loop % words0
  {
    StringLower, words%A_Index%, words%A_Index%
    StringGetPos, pos, words%A_Index%, `r
    StringReplace, words%A_Index%, words%A_Index%, `r

    If (pos != -1) 
    {
      keywordList.Push(words%A_Index%)
      repeatList.Push(1)
    }
    wordList.Push(words%A_Index%)
  }
}

keywordList.Push("next slide")
keywordList.Push("previous slide")
keywordList.Push("pitch pal stop")

 ; Set up speech recognizer object
Recognizer := new SpeechRecognizer
Recognizer.Listen(True)

Text := ""
;begin listening loop

if (mode = "keyword")
{
    Recognizer.Recognize(keywordList)
    TrayTip, Keyword Mode, Keyword mode is ready.

    while Text != "pitch pal stop"
    {
      Text := Recognizer.Prompt()
      
      WinGetTitle, Title, A
      if (!inStr(Title, "PowerPoint"))
      {
        continue
      }
      repeatIdx := ReturnIndex(Text, keywordList)
      repeatVal := repeatList[repeatIdx]
      IfEqual, Text, previous slide
      {
        Send, {Backspace}
      }
      IfEqual, Text, next slide
      {
        Send, {Space}
      }
      Else if (repeatVal = 1)
      {
        Send, {Space}
        repeatList[repeatIdx] := repeatVal - 1
      }
    }
    MsgBox, PitchPal has stopped.
    ExitApp
}

if (mode = "dictation")
{
    Recognizer.Recognize(1)
    TrayTip, Dictation Mode, Dictation mode is ready.
    while Text != "stop"
    {
      Text := Recognizer.Prompt()
      WinGetTitle, Title, A
      if (!inStr(Title, "Command Prompt"))
      {
        continue
      }
      SendInput, %Text%
    }
}

F10::
MsgBox, PitchPal has stopped.
ExitApp
return