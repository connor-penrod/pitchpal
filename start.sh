#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd pythonlib
python3 PitchPal.py "$DIR/pythonlib"
