import tkinter, win32api, win32con, pywintypes, sys, getopt
from math import floor
from time import sleep

def updatetext():
    try:
        file = open("overlay.txt", "r")
        overlayText = file.read()
        file.close()
    except:
        overlayText = ""
    label.update_idletasks()
    label_width = float(label.winfo_width())
    label_height = float(label.winfo_height())

    label.master.geometry("+" + str(floor(screen_width/2 - label_width/2)) + "+" + str(floor(screen_height - label_height)))

    
    label.config(text=overlayText)
    label.config(fg="white")
    label.after(10, updatetext)

root = tkinter.Tk()
screen_width = float(root.winfo_screenwidth())
screen_height = float(root.winfo_screenheight())

label = tkinter.Label(text="", font=('Calibri','50'), fg='black', bg='black', wraplength=screen_width, justify="center")
label.master.overrideredirect(True)
label.master.lift()
label.master.wm_attributes("-topmost", True)
label.master.wm_attributes("-disabled", True)
label.master.wm_attributes("-transparentcolor", "black")

hWindow = pywintypes.HANDLE(int(label.master.frame(), 16))
# http://msdn.microsoft.com/en-us/library/windows/desktop/ff700543(v=vs.85).aspx
# The WS_EX_TRANSPARENT flag makes events (like mouse clicks) fall through the window.
exStyle = win32con.WS_EX_COMPOSITED | win32con.WS_EX_LAYERED | win32con.WS_EX_NOACTIVATE | win32con.WS_EX_TOPMOST | win32con.WS_EX_TRANSPARENT
win32api.SetWindowLong(hWindow, win32con.GWL_EXSTYLE, exStyle)

updatetext()


label.pack()
label.mainloop()