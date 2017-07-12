/*
Copyright 2017 Mycroft AI, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

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
mode = %1%
fileName = %2%

if (paramCount > 2 or paramCount < 1)
{
  MsgBox, Invalid option. `n`n  Options:`n`n   "keyword" transitions slides based on keywords provided in a text file`n   Usage: pitchpal.exe keyword <file name>`n`n   "dictation" records speech to text in the command prompt`n   Usage: pitchpal.exe dictation
  ExitApp
}
else if (mode = "dictation" and paramCount != 1)
{
  MsgBox, Invalid option. `n`n  Options:`n`n   "keyword" transitions slides based on keywords provided in a text file`n   Usage: pitchpal.exe keyword <file name>`n`n   "dictation" records speech to text in the command prompt`n   Usage: pitchpal.exe dictation
  ExitApp
}
else if (mode = "keyword" and paramCount != 2)
{
  MsgBox, Invalid option. `n`n  Options:`n`n   "keyword" transitions slides based on keywords provided in a text file`n   Usage: pitchpal.exe keyword <file name>`n`n   "dictation" records speech to text in the command prompt`n   Usage: pitchpal.exe dictation
  ExitApp
}
else if (mode != "keyword" and mode != "dictation")
{
  MsgBox, Invalid option. `n`n  Options:`n`n   "keyword" transitions slides based on keywords provided in a text file`n   Usage: pitchpal.exe keyword <file name>`n`n   "dictation" records speech to text in the command prompt`n   Usage: pitchpal.exe dictation
  ExitApp
}

SetTitleMatchMode 2

 ; Retrieve keywords
if (mode = "keyword")
{
    try
    {
      file := FileOpen(fileName, "r")
      manuscript := file.read()
      file.Close()
    }
    catch e
    {
      MsgBox, The manuscript file '%fileName%' could not be opened.
      ExitApp
    }
    ; split sentences, turn all words to lowercase

    sentences := []
    keywordList := []
    repeatList := []
    slideList := []
    
    cnt = 1

    ; StringSplit, sentences, manuscript, `n
    Loop, Parse, manuscript,`n
    {
      keywordPhrase := A_LoopField
      StringReplace, keywordPhrase, keywordPhrase, `r
      StringLower, keywordPhrase, keywordPhrase
      keywordList.Push(keywordPhrase)
      repeatList.Push(1)
      slideList.Push(cnt)
      cnt := cnt + 1
    }
    keywordList.Push("next slide")
    keywordList.Push("previous slide")
    keywordList.Push("pitch pal stop")
}

 ; Set up speech recognizer object
Recognizer := new SpeechRecognizer
Recognizer.Listen(True)

Text := ""

if (mode = "keyword")
{
    Recognizer.Recognize(keywordList)
    TrayTip, Keyword Mode, Keyword mode is ready.

    currSlide = 1
    while true
    {
      Text := Recognizer.Prompt()
      
      WinGetTitle, Title, A
      if (!inStr(Title, "PowerPoint"))
      {
        continue
      }
      ; repeatIdx := ReturnIndex(Text, keywordList)
      ; repeatVal := repeatList[repeatIdx]
      IfEqual, Text, previous slide
      {
        Send, {Backspace}
        currSlide := currSlide - 1
      }
      IfEqual, Text, next slide
      {
        Send, {Space}
        currSlide := currSlide + 1
      }
      Else if (Text = keywordList[currSlide])
      {
        Send, {Space}
        ; repeatList[repeatIdx] := repeatVal - 1
        currSlide := currSlide + 1
      }
      /*
      Else if (Text = keywordList[currSlide + 1])
      {
        Loop, 2
        {
          Send, {Space}
          Sleep 100
        }
        currSlide := currSlide + 2
      }
      */
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
      if (!inStr(Title, "Command Prompt") and !inStr(Title, "cmd"))
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