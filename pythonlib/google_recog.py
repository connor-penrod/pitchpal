import webbrowser, sys, os


webbrowser.open_new("file://" + os.path.dirname(os.path.realpath(sys.argv[0])) + "/voice_grab/voice_grab.html")