import tkinter, sys, getopt, os, textwrap
from math import floor, ceil
from time import sleep
from PIL import Image, ImageTk
from fuzzywuzzy import fuzz
import subprocess
child_pid = None
try:
    p = subprocess.Popen(["python3", sys.argv[1] + "/ibmstt2.py", str(sys.argv[1])])
    child_pid = p.pid
except Exception as e:
    print("ERROR: " + str(e))

current_slide = 0
current_text = ""
analysis_text = ""
analysis_cutoff = 90
accuracy_threshold = 60
font_size = 35

# clear debug file
open(sys.argv[1] + "/log", "w").close()

# clear overlay file
open(sys.argv[1] + "/overlay.txt", "w").close()


def log(string):
    f = open(sys.argv[1] + "/log", "a")
    f.write("\n" + string)
    f.close()

def close(event):
    global analysis_text
    global p
    print("Exitting PitchPal")
    analysis_text = ""
    p.kill() #os.kill(child_pid, signal.SIGTERM)
    root.destroy()
    
def retrieveText():
    global current_text
    global analysis_text
    try:
        file = open(sys.argv[1] + "/overlay.txt", "r")
        current_text = file.read()
        file.close()
    except Exception as e:
        current_text = "[Blank]"
        log("Error: ", str(e.message))
    
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
    global current_text
    modified_text = new_text
    
    #while(len(current_text) > analysis_cutoff):
     #   modified_text = current_text
      #  wordLength = current_text.find(" ")
       # modified_text = current_text[wordLength+1:]
        #current_text = modified_text
    
    canvas.itemconfigure(subtitle, text = modified_text)
    
def checkSwitch():
    global current_slide
    
    if(checkSwitch.last_text != analysis_text):  
        maxIdx = current_slide
        maxRat = 0
        log("Change detected, checking slides " + str(current_slide) + "-" + str(current_slide+4))
        log("Phrase to match: " + analysis_text)
        for i in range(current_slide, current_slide+3):
            if(i >= 0):
                rat = fuzz.ratio(phrases[i], analysis_text)
            else:
                rat = -1
            log("Slide: " + str(i) + " -> Ratio (out of 100): " + str(rat) + " on phrase: '" + phrases[i] + "'")
            if(rat > maxRat and rat > accuracy_threshold):
                maxIdx = i
                maxRat = rat
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
fileList = sorted(os.listdir(sys.argv[1] + "/images"))
for filename in fileList:
    print(filename)
    photo = Image.open(sys.argv[1] + "/images/" + filename)
    photo = photo.resize((int(floor(screen_width)), int(floor(screen_height))))
    tkPhoto = ImageTk.PhotoImage(photo)
    slides.append(tkPhoto)
    
phrases = []
phrases.append("@@@@@@") # placeholder
with open(sys.argv[1] + "/manuscript.txt") as manu:
    for line in manu:
        line = line.lower()
        line = line.replace(".","").replace(",","").replace("\n","").replace("!","").replace("?","")
        phrases.append(line)
        
analysis_cutoff = len(phrases[1])

root.bind("<space>", lambda event, num=1: switch(event, num))
root.bind("<BackSpace>", lambda event, num=-1: switch(event, num))
    
canvas = tkinter.Canvas(root, width = screen_width, height = screen_height)
canvas.pack()

canvas.create_image(screen_width/2, screen_height/2, image = slides[0], tags="slide")

subtitle = canvas.create_text(screen_width/2,screen_height*5/6,text="test", fill="white",font=('Calibri',str(font_size)), justify="center")

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

retrieveText()
checkSwitch()

root.mainloop()
