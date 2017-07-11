# Running
To run, call the executable in 'bin' from the command line like so:
|path to executable|/pitchpal.exe keyword |path to file|/keywordfile.txt
For example:
```C:/Users/Connor/Documents/PitchPal/pitchpal/bin/pitchpal.exe keyword C:/manuscript.txt```
This activates keyword mode with the keywords given in ‘manuscript.txt’.
(If you don’t want to type out that entire path every time, add the <path to executable> to the system path variable, see: https://www.computerhope.com/issues/ch000549.htm)
# Modes
You need to specify a mode, either “keyword” or “dictation”.

“keyword” mode allows you to specify keywords and have slides change when they’re said. It takes an additional argument of the text file that has the keywords in them. Only changes slides in PowerPoint or Google Slides. See the bottom of this page to see how to format the keyword file. This works like so:

```pitchpal.exe keyword <path to manuscript>/manuscript.txt```

Once entered, wait until you receive a notification that Keyword Mode has finished loading. This can take awhile, as it is loading up the Microsoft Speech API.

“dictation” prints out anything that is said onto the Command Prompt (nowhere else). It doesn’t have any additional arguments.
Note: dictation mode is very significantly less accurate than keyword mode. Used like so:

```pitchpal.exe dictation```

# Formatting of Keywords File
The keywords file is just a simple text file, with each keyword on its own line. 

**Make sure to add a newline to the end of the file. This way the program detects the final keyword.** 

The keywords are case insensitive.

Example:
```
Artificial
Community
Not
Change
Speak
Self

```
