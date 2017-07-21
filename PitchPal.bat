UniServerZ/UniController.exe start_apache
python pythonlib/google_recog.py
pause
python pythonlib/pitchpal.py "%cd%\pythonlib"
UniServerZ/UniController.exe stop_apache
