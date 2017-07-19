import tkinter, win32api, win32con, pywintypes, sys, getopt, os
from math import floor
from time import sleep
from PIL import Image, ImageTk
from fuzzywuzzy import fuzz

current_slide = 0
current_text = ""
analysis_text = ""
analysis_cutoff = 90

# clear debug file
open(sys.argv[1] + "\log", "w").close()

def log(string):
    f = open(sys.argv[1] + "\log", "a")
    f.write("\n" + string)
    f.close()

def close(event):
    global analysis_text
    analysis_text = ""
    root.destroy()
    
def retrieveText():
    global current_text
    global analysis_text
    try:
        file = open(sys.argv[1] + "\overlay.txt", "r")
        current_text = file.read()
        file.close()
    except Exception as e:
        current_text = "[Blank]"
        log("Error: ", str(e.message))
    
    if(len(current_text)-analysis_cutoff < 0):
        analysis_text = current_text[0:]
    else:
        analysis_text = current_text[len(current_text)-analysis_cutoff:]
    
    if(analysis_text != retrieveText.last_text):
        log("Analysis text is now: '" + analysis_text + "'")
        retrieveText.last_text = analysis_text
    
    updatetext()
    
    canvas.after(10, retrieveText)
    
def switch(event, offset=1):
    switchslide(offset)
    
    
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
    
    log("Switching to *Slide " + str(current_slide) + "*")
    
    analysis_text = ""    
    
def updatetext():
    global current_text
    modified_text = current_text
    
    if(len(modified_text) > 130):
        removeChars = 20
        modified_text = current_text[removeChars:]
    
    
    canvas.itemconfigure(subtitle, text = modified_text)
    
def checkSwitch():
    global current_slide
    
    if(checkSwitch.last_text != analysis_text):  
        maxIdx = current_slide
        maxRat = 0
        log("Change detected, checking slides " + str(current_slide-2) + "-" + str(current_slide+2))
        log("Phrase to match: " + analysis_text)
        for i in range(current_slide-2, current_slide+3):
            if(i >= 0):
                rat = fuzz.ratio(phrases[i], analysis_text)
            else:
                rat = -1
            log("Slide: " + str(i) + " -> Ratio (out of 100): " + str(rat))
            if(rat > maxRat and rat > 70):
                maxIdx = i
                maxRat = rat
        if maxRat != 0:
            log("----\nHighest ratio found: " + str(maxRat) + "/100" + "\n----")
            switchslide(maxIdx)
        else:
            log("----\nNo ratio found over 70/100\n----")
        
    checkSwitch.last_text = analysis_text
    
    canvas.after(100, checkSwitch)
    

root = tkinter.Tk()

root.bind("<Escape>", close)

screen_width = float(root.winfo_screenwidth())
screen_height = float(root.winfo_screenheight())

slides = []
for filename in os.listdir(sys.argv[1] + "\\images"):
    photo = Image.open(sys.argv[1] + "\\images\\" + filename)
    photo = photo.resize((floor(screen_width), floor(screen_height)))
    tkPhoto = ImageTk.PhotoImage(photo)
    slides.append(tkPhoto)
    
phrases = []
phrases.append("@@@@@@") # placeholder
with open("manuscript.txt") as manu:
    for line in manu:
        line = line.lower()
        line = line.replace(".","").replace(",","").replace("\n","").replace("!","").replace("?","")
        phrases.append(line)

root.bind("<space>", lambda event, num=1: switch(event, num))
root.bind("<BackSpace>", lambda event, num=-1: switch(event, num))
    
canvas = tkinter.Canvas(root, width = screen_width, height = screen_height)
canvas.pack()

canvas.create_image(screen_width/2, screen_height/2, image = slides[0], tags="slide")

subtitle = canvas.create_text(screen_width/2,screen_height*5/6,text="test",font=('Calibri','50'),width=screen_width, justify="center")

root.overrideredirect(True)
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