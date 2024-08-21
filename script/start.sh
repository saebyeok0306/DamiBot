#!/bin/bash

SCREEN_SESSION="dami"

if screen -list | grep -q "\.dami"; then
  screen -S $SCREEN_SESSION -X quit
fi

source .venv/bin/activate
pip install -r requirements.txt
screen -dS $SCREEN_SESSION python app.py