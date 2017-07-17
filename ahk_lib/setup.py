from cx_Freeze import setup, Executable

base = None

includes      = []
include_files = [r"C:\Program Files (x86)\Python36\tcl\tcl86t.lib", \
                 r"C:\Program Files (x86)\Python36\tcl\tk86t.lib"]


executables = [Executable("overlay.py", base=base)]
packages = ["tkinter", "win32api", "win32con", "pywintypes", "sys", "getopt"]
options = {
    'build_exe': {

        'packages':packages,
        'includes':includes,
        'include_files':include_files
    }
}

setup(
    name = "Overlay",
    options = options,
    version = "1",
    description = '',
    executables = executables
)