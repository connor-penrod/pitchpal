from cx_Freeze import setup, Executable
import os

base = None

os.environ['TCL_LIBRARY'] = r'C:\Program Files (x86)\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Program Files (x86)\Python36\tcl\tk8.6'

executables = [Executable("PitchPal.py", base=base)]
packages = ["tkinter", "win32api", "win32con", "pywintypes", "sys", "getopt", "os", "textwrap", "math", "time", "PIL", "fuzzywuzzy", "subprocess", "websocket"]
options = {
    'build_exe': {

        'packages':packages,
        "include_files": ["C:\\Program Files (x86)\\Python36\\DLLs\\tcl86t.dll", "C:\\Program Files (x86)\\Python36\\DLLs\\tk86t.dll"]
    }
}

setup(
    name = "Overlay",
    options = options,
    version = "1",
    description = '',
    executables = executables
)