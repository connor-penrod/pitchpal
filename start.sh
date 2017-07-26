#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd pythonlib
python PitchPal.py "$DIR/pythonlib"
