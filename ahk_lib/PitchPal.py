import tkinter, win32api, win32con, pywintypes, sys, getopt, os
from math import floor
from time import sleep
from PIL import Image, ImageTk

current_slide = 0

def close(event):
    root.destroy()
    
def switch(event, offset=1):
    switchslide(offset)
    
def switchslide(offset=1):
    global current_slide
    current_slide += offset
    
    if(current_slide > (len(slides) - 1)):
        current_slide = 0
    elif(current_slide < 0):
        current_slide = len(slides) - 1
    
    canvas.delete("slide")
    canvas.create_image(screen_width/2, screen_height/2, image = slides[current_slide], tags="slide")
    canvas.lift(subtitle, "slide")
    
def updatetext():
    try:
        file = open(sys.argv[1] + "\overlay.txt", "r")
        overlayText = file.read()
        file.close()
    except Exception as e:
        overlayText = str(e)

    canvas.itemconfigure(subtitle, text=overlayText)
    canvas.after(10, updatetext)

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

root.bind("<space>", lambda event, num=1: switch(event, num))
root.bind("<BackSpace>", lambda event, num=-1: switch(event, num))
    
canvas = tkinter.Canvas(root, width = screen_width, height = screen_height)
canvas.pack()

canvas.create_image(screen_width/2, screen_height/2, image = slides[0], tags="slide")

subtitle = canvas.create_text(screen_width/2,screen_height*5/6,text="test",font=('Calibri','50'),width=screen_width, justify="center")

root.overrideredirect(True)
root.lift()
root.wm_attributes("-topmost", True)
#root.wm_attributes("-disabled", True)
#root.wm_attributes("-transparentcolor", "white")

#hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
#exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
#win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)


updatetext()

root.mainloop()