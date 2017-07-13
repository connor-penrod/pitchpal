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


 ; Simulation of a Unix man(ual)page for Windows
manpage =
(

PITCHPAL.EXE(1)

NAME
    pitchpal.exe - starts a voice activated 
                   presentation helper

SYNOPSIS
    pitchpal.exe mode [-n] [file] [recovery_level] [--debug | -d]
    
DESCRIPTION
    pitchpal.exe starts a session with a 
    voice activated presentation helper. Given
    customized keywords, this program will
    switch slides when these keywords are said
    in order. Also, dictation mode can be activated
    to convert all speech to text in a command
    prompt.

OPTIONS
    mode - can be either "keyword" or "dictation"
           "keyword" starts keyword recognition mode
           and requires a specified txt file with each
           keyword on its own line.
           "dictation" starts speech to text conversion
           in the command prompt.
    
    [-n] - "dictation" mode only. Send converted speech-to-
           text as a Windows notification.
           
    [file] - "keyword" mode only. The keyword file to be used.
           
    [recovery_level] - "keyword" mode only. Specify how many 
           future keywords can be said to have pitchpal.exe 
           attempt to 'recover' the state of the
           presentation by going forward multiple slides.
           For example, if your keyword list is 
           ["start", "presentation", "community"],
           a [recover_level] of 1 would cause the program
           to activate on "start" but also on "presentation".
           And if "presentation" was said then the program
           will go forward two slides to resynchronize itself.
           Default is 0.

    [--debug | -d] - starts pitchpal.exe in debug mode. Debug
                     messages will be displayed in "debug.txt"
                     in the executable's folder
                     
AUTHOR
    Mycroft AI

Windows           Last Change: July 2017
)



 ; Open text document with manpage on incorrect usage
ReturnManual(text)
{
   FileDelete, %A_ScriptDir%\manual.txt
   Loop, Parse, text, `n
   {
       FileAppend, %A_LoopField%`n, %A_ScriptDir%\manual.txt
   }
   Run, notepad.exe %A_ScriptDir%\manual.txt
}

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

 ; Utility function for retrieving the index on a specified string element
ReturnIndexInStr(key, list)
{
  Loop, % list.Length()
  {
    if (InStr(list[A_Index], key))
    {
      return % A_Index
    }
  }
  return 0
}

 ; Utility function for checking an array for a string
CheckArray(string, array)
{
  x = 1
  Loop % array.Length()
  {
    if(string = array[x])
    {
      return % true
    }
    x := x + 1
  }
  return % false
}

 ; Logs to 'debug.txt' in the same directory
Log(string, debug=1)
{
  if(debug)
  {
    FileAppend, %string%`n, %A_ScriptDir%\debug.txt
  }
}


SetTitleMatchMode 2

paramCount = %0%
mode = %1%
paramTwo = %2%
paramThree = %3%
paramFour = %4%
debugMode := false
notifMode := false

recoveryLevel = 0

if (mode = "dictation")
{
  if(paramCount > 3)
  {
    ReturnManual(manpage)
    ExitApp
  }
  else if(paramTwo = "--debug" or paramTwo = "-d")
  {
    debugMode := true
    if(paramThree = "-n")
    {
      notifMode := true
    }
  }
  else if(paramTwo = "-n")
  {
    notifMode := true
    if(paramThree = "--debug" or paramThree = "-d")
    {
      debugMode := true
    }
  }
  else if(paramTwo)
  {
    ReturnManual(manpage)
    ExitApp
  }
}
else if (mode = "keyword")
{
  if(paramCount > 4 or paramCount < 2)
  {
    ReturnManual(manpage)
    ExitApp
  }
  else if(paramThree = "--debug" or paramThree = "-d")
  {
    debugMode := true
  }
  else if paramThree is integer
  {
    recoveryLevel := paramThree
    if(paramFour = "--debug" or paramFour = "-d")
    {
      debugMode := true
    }
    else if(paramFour)
    {
      ReturnManual(manpage)
      ExitApp
    }
  }
  else if(paramThree)
  {
      ReturnManual(manpage)
      ExitApp
  }
  fileName := paramTwo
}
else
{
  ReturnManual(manpage)
  ExitApp
}

if(debugMode)
{
  try
  {
    FileDelete, %A_ScriptDir%\debug.txt
  }
}

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
      errorMsg := "----`nERROR, FILE COULD NOT BE OPENED`n" . "File: " . e.file . "`n" . "Line: " . e.line . "`n" . "Message: " . e.message . "`n" . "Details: " . e.what . "`n" . "Extra: " . e.extra . "`n----`n"
      Log(errorMsg, 1)
      ExitApp
    }
    
    ; split sentences, turn all words to lowercase

    sentences := []
    keywordList := []
    keywordListClean := []
    repeatList := []
    slideList := []
    
    cnt = 1

    ; StringSplit, sentences, manuscript, `n
    Log("`n----`nAdding Keywords: `n", debugMode)
    Loop, Parse, manuscript,`n
    {
      keywordPhrase := A_LoopField
      keywordPhraseClean := A_LoopField
      
      StringReplace, keywordPhrase, keywordPhrase, `r
      StringLower, keywordPhrase, keywordPhrase
      
      StringReplace, keywordPhraseClean, keywordPhrase, `r
      StringLower, keywordPhraseClean, keywordPhrase
      Log("|" . keywordPhrase . "|", debugMode)
      Log("Sub-keywords of |" . keywordPhrase . "|: `n", debugMode)
      Loop, Parse, keywordPhraseClean, %A_Space%
      {
        Log("|" . A_LoopField . "|", 1)
        keywordListClean.Push(A_LoopField)
      }
      
      keywordPhrase := " " . keywordPhrase . " "
            
      keywordList.Push(keywordPhrase)
      
      repeatList.Push(1)
      slideList.Push(cnt)
      cnt := cnt + 1
    }
    Log("`n----`n", debugMode)
    keywordListClean.Push("next slide")
    keywordListClean.Push("previous slide")
    keywordListClean.Push("pitch pal stop")
}

 ; Set up speech recognizer object
Recognizer := new SpeechRecognizer
Recognizer.Listen(True)
Log("`nRecognizer loaded.`n", debugMode)

Text := ""

if (mode = "keyword")
{
    Log("`nKeyword Mode activated, preparing recognizer`n", debugMode)
    Recognizer.Recognize(keywordListClean)
    TrayTip, Keyword Mode, Keyword mode is ready.
    currSlide = 1
    
    while true
    {
      if(recoveryLevel)
      {
        i = 1
        recoveryList := []
        Log("`nRecovery words for " . keywordList[currSlide] . ":`n", debugMode)
        Loop % recoveryLevel
        {
          recoveryWord := keywordList[currSlide+i]
          StringReplace, recoveryWord, recoveryWord, `r
          recoveryWord := " " . recoveryWord . " "
          recoveryList.Push(recoveryWord)
          Log(keywordList[currSlide+i], debugMode)
          i := i + 1
        }
      }
    
      Text := Recognizer.Prompt()
      
      Log("`nMicrosoft Speech API heard: " . Text . "`n")
      
      WinGetTitle, Title, A
      
      /* Would restrict the available programs
      if (!inStr(Title, "PowerPoint") and !inStr(Title, "Google Slides"))
      {
        continue
      }
      */

      IfEqual, Text, previous slide
      {
        Send, {Backspace}
        currSlide := currSlide - 1
        Log("`nWent back a slide to slide " . currSlide . "`n", debugMode)

      }
      IfEqual, Text, next slide
      {
        Send, {Space}
        currSlide := currSlide + 1
        Log("`nAdvanced to slide " . currSlide . "`n", debugMode)
      }
      Else if (InStr(keywordList[currSlide], " " . Text . " "))
      {
        Send, {Space}
        ; repeatList[repeatIdx] := repeatVal - 1
        currSlide := currSlide + 1
        Log("`nAdvanced to slide " . currSlide . "`n", debugMode)

      }
      Else if (recoveryLevel and ReturnIndexInStr(" " . Text . " ", recoveryList))
      {
        Log("`nAttempting to recover " . ReturnIndexInStr(" " . Text . " ",recoveryList)+1 . " slides`n", debugMode)
        Loop % ReturnIndexInStr(" " . Text . " ", recoveryList)+1
        {
          Send, {Space}
          Sleep 10
        }
        currSlide := currSlide + ReturnIndexInStr(" " . Text . " ", recoveryList)+1
        Log("`nRecovered on keyword '" . Text . "'. Now on slide " . currSlide . ".`n", debugMode)
      }
    }
    MsgBox, PitchPal has stopped.
    ExitApp
}

if (mode = "dictation")
{
    Log("`nDictation Mode activated, preparing recognizer`n", debugMode)
    Recognizer.Recognize(1)
    TrayTip, Dictation Mode, Dictation mode is ready.
    
    initReturns = 1
    
    while Text != "stop"
    {
      if(initReturns)
      {
        Send ^{C}
        initReturns = 0
      }      
    
      Text := Recognizer.Prompt()
      
      if(notifMode)
      {
        TrayTip, Dictation, %Text%
      }
      
      WinGetTitle, Title, A
      if (!inStr(Title, "Command Prompt") and !inStr(Title, "cmd"))
      {
        continue
      }
      SendInput, %Text%
      Send ^{C}
      Send ^{C}
      Send ^{C}
      Log("`nMicrosoft Speech API heard: " . Text . "`n", debugMode)
    }
}

F10::
MsgBox, PitchPal has stopped.
ExitApp
return