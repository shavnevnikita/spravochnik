#!/bin/bash

if test -f "compiled"; then
    echo "Already compiled"
else
    touch compiled
    pip3 install virtualenv
    python3 -m venv venv
    source venv/bin/activate
    pip3 install pyqt6 sqlalchemy
    python3 db_scheme.py
fi