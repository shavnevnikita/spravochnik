#!/bin/bash

if test -f "compiled"; then
    source venv/bin/activate
    python3 main.py
else
    echo "U need to compile first. Run ./compile.sh"
fi