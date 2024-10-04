#!/bin/bash

VENV_PATH="/path/to/your/venv"

MAIN_PY_PATH="main.py"

source "$VENV_PATH/bin/activate" && python "$MAIN_PY_PATH"

deactivate