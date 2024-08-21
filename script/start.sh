#!/bin/bash

SCREEN_SESSION="dami"

if screen -list | grep -q "\.dami"; then
  screen -S $SCREEN_SESSION -X quit
fi

. .venv/bin/activate
pip install -r requirements.txt
screen -dS $SCREEN_SESSION bash -c "source .venv/bin/activate && python app.py"