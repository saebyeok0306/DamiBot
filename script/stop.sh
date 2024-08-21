#!/bin/bash

SCREEN_SESSION="dami"

if screen -list | grep -q "\.dami"; then
  screen -S $SCREEN_SESSION -X quit
fi