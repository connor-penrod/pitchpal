import threading
from tkinter import font
import tkinter, sys, getopt, os, textwrap
from math import floor, ceil
from time import sleep
from PIL import Image, ImageTk
from fuzzywuzzy import fuzz
from configparser import SafeConfigParser
import subprocess


def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


child_pid = None
try:
    p = subprocess.Popen(["python3", sys.argv[1] + "/ibmstt2.py", str(sys.argv[1]), str(os.getpid())])
    child_pid = p.pid
except Exception as e:
    print("ERROR: " + str(e))

try:
    parser = SafeConfigParser()
    parser.read(sys.argv[1] + "/../settings.conf")
    FONT_SIZE = int(parser.get('font_settings', 'font_size'))
    FONT_COLOR = parser.get('font_settings', 'font_color')
    FONT_BACKGROUND_TRANSPARENCY = parser.get('font_settings', 'font_background_transparency')
    SLIDE_DETECTION_RANGE = int(parser.get('slide_settings', 'slide_detection_range'))
    SLIDE_DETECTION_THRESHOLD = int(parser.get('slide_settings', 'slide_detection_threshold'))
    NEXT_SLIDE_PHRASE = parser.get('slide_settings', 'next_slide_phrase')
    PREVIOUS_SLIDE_PHRASE = parser.get('slide_settings', 'previous_slide_phrase')
    FIRST_SLIDE_PHRASE = parser.get('slide_settings', 'first_slide_phrase')
    LAST_SLIDE_PHRASE = parser.get('slide_settings', 'last_slide_phrase')
    CUSTOM_SLIDE_PHRASE = parser.get('slide_settings', 'custom_slide_phrase')
    SHOW_TEXT_PHRASE = parser.get('slide_settings', 'show_subtitle_phrase')
    HIDE_TEXT_PHRASE = parser.get('slide_settings', 'hide_subtitle_phrase')
    INITIAL_TEXT_STATE = bool(int(parser.get('slide_settings', 'initial_text_state')))
    print("settings.conf successfully loaded...")
except Exception as e:
    print(str(e))
    print("There was an error reading settings.conf, using default settings...")
    FONT_SIZE = 35
    FONT_COLOR = 'white'
    FONT_BACKGROUND_TRANSPARENCY = '75'
    SLIDE_DETECTION_RANGE = 2
    SLIDE_DETECTION_THRESHOLD = 60
    NEXT_SLIDE_PHRASE = "next slide please"
    PREVIOUS_SLIDE_PHRASE = "previous slide please"
    FIRST_SLIDE_PLEASE = "first slide please"
    LAST_SLIDE_PLEASE = "last slide please"
    CUSTOM_SLIDE_PHRASE = "slide x please"
    SHOW_TEXT_PHRASE = "show text please"
    HIDE_TEXT_PHRASE = "hide text please"

show_text = INITIAL_TEXT_STATE
current_slide = 0
current_text = ""
analysis_text = ""
analysis_cutoff = 90
accuracy_threshold = SLIDE_DETECTION_THRESHOLD
font_size = FONT_SIZE
font_color = FONT_COLOR
font_outline_color = "black"
font_background_transparency = FONT_BACKGROUND_TRANSPARENCY

monitoring = True

# clear debug file
try:
    open(sys.argv[1] + "/log", "w").close()
except:
    print("Log file could not be opened.")

# clear overlay file
open(sys.argv[1] + "/overlay.txt", "w").close()


def log(string):
    try:
        f = open(sys.argv[1] + "/log", "a")
        f.write("\n" + string)
        f.close()
    except:
        print("Log file could not be written to.")

def sttMonitor():
    global p
    global child_pid
    print("STT Monitor active...")
    while(p.poll() == None and monitoring):
        pass
    if(monitoring):
        #canvas.itemconfigure(wifiIndicator, state="normal")
        sleep(2)
        print("STT process unexpected termination detected, restarting process...")
        try:
            p = subprocess.Popen(["python3", sys.argv[1] + "/ibmstt2.py", str(sys.argv[1]), str(os.getpid())])
            child_pid = p.id
        except Exception as e:
            print("STT process could not be recreated, error type " + type(e).__name__ + ": " + str(e))
            return
        print("STT process restarted.")
        #canvas.itemconfigure(wifiIndicator, state="hidden")
        sttMonitor()


def close(event):
    global monitoring
    global analysis_text
    global p
    print("Exitting PitchPal")
    analysis_text = ""
    monitoring = False
    try:
        p.kill() #os.kill(child_pid, signal.SIGTERM)
    except Exception as e:
        print("STT process could not be terminated. Error type " + type(e).__name__ + ": " + str(e))
    root.destroy()
    
def retrieveText():
    global current_text
    global analysis_text
    try:
        file = open(sys.argv[1] + "/overlay.txt", "r")
        current_text = file.read()
        file.close()
    except Exception as e:
        current_text = "[]"
        log("Error, 'overlay.txt' could not be opened: " + str(e))
    
    chars = ceil(-1.462*font_size + 109.6)
    format_text = textwrap.fill(current_text, chars)
    newlines = format_text.count("\n")
    if(newlines > 2):
        format_text = format_text.replace("\n", "|", newlines - 2)
        first_newline = format_text.rfind("|")
        format_text = textwrap.fill(format_text[first_newline+1:], chars)
    
    '''
    # format for wordwrap
    line_length = 50
    line_end = line_length
    last_space = 0
    last_newline = 0
    format_text = ""
    
    
    while(1):
   
        if (0 <= line_end) and (line_end < len(current_text)):
        
            last_space = current_text[last_newline:line_end].rfind(" ")
            
            log("Last space -> " + str(last_space))
            log("Last newline -> " + str(last_newline))
            log("Text snippet -> " + current_text[last_newline:last_space])
            
            format_text += current_text[last_newline:last_space] + "\n"
                              
                            
            line_end = last_space + line_length
            
            last_newline = last_space + 1
            
            
            
        else:
            format_text = current_text
            break
    '''   
        
  
    # get analysis text
    if(len(current_text)-analysis_cutoff < 0):
        analysis_text = current_text[0:]
    else:
        analysis_text = current_text[len(current_text)-analysis_cutoff:]
    
    if(analysis_text != retrieveText.last_text):
        log("Analysis text is now: '" + analysis_text + "'")
        retrieveText.last_text = analysis_text
    
    updatetext(format_text)
    
    canvas.after(10, retrieveText)
    
def switch(event, offset=1):
    global current_slide
    switchslide(current_slide+offset)
    
    
def switchslide(number=1):
    global analysis_text
    global current_slide
    global analysis_cutoff
    current_slide = number
    
    if(current_slide > (len(slides) - 1)):
        current_slide = (len(slides) - 1)
    elif(current_slide < 0):
        current_slide = 0
    
    canvas.delete("slide")
    canvas.create_image(screen_width/2, screen_height/2, image = slides[current_slide], tags="slide")
    canvas.lift(subtitle, "slide")
    
    try:
        analysis_cutoff = len(phrases[current_slide+1])
    except:
        log("Reached end of slideshow, analysis over.")
    log("Switching to *Slide " + str(current_slide) + "*")
    log("----\nAnalysis window is now " + str(analysis_cutoff) + "\n----")
        
def updatetext(new_text):
    global subtitleBBox
    global current_text
    modified_text = new_text
    
    #while(len(current_text) > analysis_cutoff):
     #   modified_text = current_text
      #  wordLength = current_text.find(" ")
       # modified_text = current_text[wordLength+1:]
        #current_text = modified_text
    
    #canvas.itemconfigure(subtitleOutline, text = modified_text)

    try:
        canvas.delete(subtitleBBox)
    except:
        pass

    if not show_text:
        try:
            canvas.itemconfigure(subtitleBBox, state="hidden")
        except:
            pass
        canvas.itemconfigure(subtitle, state="hidden")
    else:
        try:
            canvas.itemconfigure(subtitleBBox, state="normal")
        except:
            pass
        canvas.itemconfigure(subtitle, state="normal")
        canvas.itemconfigure(subtitle, text = modified_text)
        subCoords = canvas.bbox("subtitletext")
        subtitleBBox = canvas.create_rectangle(subCoords[0], subCoords[1], subCoords[2], subCoords[3], fill="black", stipple=font_background_transparency)
        canvas.lift(subtitle, subtitleBBox)

def checkSwitch():
    global current_slide
    global show_text
    if(checkSwitch.last_text != analysis_text):

        customPhrase = CUSTOM_SLIDE_PHRASE.split("x")
        customPhrase1 = customPhrase[0]
        customPhrase2 = customPhrase[1]

        if NEXT_SLIDE_PHRASE in analysis_text:
            switchslide(current_slide+1)
        elif PREVIOUS_SLIDE_PHRASE in analysis_text:
            switchslide(current_slide-1)
        elif FIRST_SLIDE_PHRASE in analysis_text:
            switchslide(0)
        elif LAST_SLIDE_PHRASE in analysis_text:
            switchslide(len(slides)-1)
        elif SHOW_TEXT_PHRASE in analysis_text:
            show_text = True
        elif HIDE_TEXT_PHRASE in analysis_text:
            show_text = False
        elif customPhrase1 in analysis_text and customPhrase2 in analysis_text:
            wordStart = analysis_text.index(customPhrase1) + CUSTOM_SLIDE_PHRASE.index("x")
            try:
                slideNumber = analysis_text[wordStart:(wordStart+analysis_text[wordStart:].replace(" ", "XXX", 1).find(" "))-2]
                if slideNumber == "":
                    try:
                        slideNumber = analysis_text[wordStart:wordStart+analysis_text[wordStart:].index(" ")]
                    except:
                        try:
                            slideNumber = analysis_text[wordStart:]
                        except:
                            pass
            except Exception as e:
                print("Retrieving slide number from text failed: " + str(e))
                slideNumber = None
            print(slideNumber)
            if "to" in slideNumber:
                slideNumber.replace("to", "two")
            if "for" in slideNumber:
                slideNumber.replace("for", "four")
            slideNumberList = slideNumber.split()
            print(slideNumber)
            try:
                convertednum = text2int(slideNumber)
                if convertednum > 0 and convertednum < len(slides)+1:
                    switchslide(convertednum-1)
            except:
                try:
                    switchslide(text2int(slideNumberList[0])-1)
                except:
                    pass
        maxIdx = current_slide
        maxRat = 0
        log("Change detected, checking slides " + str(current_slide) + "-" + str(current_slide+4))
        log("Phrase to match: " + analysis_text)
        for i in range(current_slide, current_slide+SLIDE_DETECTION_RANGE+1):
            if(i >= 0 and i <= len(phrases)-1):
                rat = fuzz.ratio(phrases[i], analysis_text)
                log("Slide: " + str(i) + " -> Ratio (out of 100): " + str(rat) + " on phrase: '" + phrases[i] + "'")
                if(rat > maxRat and rat > accuracy_threshold):
                    maxIdx = i
                    maxRat = rat
            else:
                rat = -1
        if maxRat != 0:
            log("----\nHighest ratio found: " + str(maxRat) + "/100" + "\n----")
            switchslide(maxIdx)
        else:
            log("----\nNo ratio found over " + str(accuracy_threshold) + "/100\n----")
        
    checkSwitch.last_text = analysis_text
    
    canvas.after(100, checkSwitch)
    

root = tkinter.Tk()

root.bind("<Escape>", close)

screen_width = float(root.winfo_screenwidth())
screen_height = float(root.winfo_screenheight())

slides = []
try:
    fileList = sorted(os.listdir(sys.argv[1] + "/images"))
except Exception as e:
    print("Image folder not found. Error type " + type(e).__name__ + ": " + str(e))
    print(" Exitting...")
    close()
for filename in fileList:
    print(filename)
    photo = Image.open(sys.argv[1] + "/images/" + filename)
    photo = photo.resize((int(floor(screen_width)), int(floor(screen_height))))
    tkPhoto = ImageTk.PhotoImage(photo)
    slides.append(tkPhoto)
    
phrases = []
phrases.append("@@@@@@") # placeholder
try:
    with open(sys.argv[1] + "/manuscript.txt") as manu:
        for line in manu:
            line = line.lower()
            line = line.replace(".","").replace(",","").replace("\n","").replace("!","").replace("?","")
            phrases.append(line)
except Exception as e:
    print("Pitch manuscript file not found, could not extract phrases. Error type " + type(e).__name__ + ": " + str(e))
    print("Exitting...")
    close()

analysis_cutoff = len(phrases[1])

root.bind("<space>", lambda event, num=1: switch(event, num))
root.bind("<BackSpace>", lambda event, num=-1: switch(event, num))


def toggleText(event, val):
    global show_text
    show_text = val
        
root.bind("<h>", lambda event: toggleText(event, 0))
root.bind("<s>", lambda event: toggleText(event, 1))

canvas = tkinter.Canvas(root, width = screen_width, height = screen_height)
canvas.pack()

canvas.create_image(screen_width/2, screen_height/2, image = slides[0], tags="slide")

#subtitleOutlineFont = font.Font(family="Helvatica", size=font_size+1)
subtitleFont = font.Font(family="Helvetica", size=font_size, weight="bold")

#subtitleOutline = canvas.create_text(screen_width/2,screen_height*5/6,text="test", fill=font_outline_color, font=subtitleOutlineFont, justify="center")
subtitle = canvas.create_text(screen_width/2,screen_height*5/6,text="test", fill=font_color, font=subtitleFont, justify="center", tags="subtitletext")
subtitleBBox = None

#wifiIndicator = canvas.create_rectangle(10, 10, floor(screen_width*0.03125)+500, floor(screen_height*0.06), fill='yellow')
#canvas.itemconfigure(wifiIndicator, state="hidden")
#subtitle = tkinter.Label(canvas, text="TEST", font=('Calibri','36'), width = 50, justify=tkinter.CENTER, wraplength = screen_width * 7/8, fg="black", bg="white")
#subtitle.attributes("-alpha", 0.5)

#canvas.create_window(screen_width/2,screen_height*5/6,window=subtitle)

root.attributes("-fullscreen", True)
#root.overrideredirect(True)
root.lift()
#root.wm_attributes("-topmost", True)
#root.wm_attributes("-disabled", True)
#root.wm_attributes("-transparentcolor", "white")

#hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
#exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
#win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

checkSwitch.last_text = ""
retrieveText.last_text = " "

monitor = threading.Thread(target=sttMonitor)
monitor.start()


retrieveText()
checkSwitch()

root.mainloop()
