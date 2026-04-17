@echo off
echo Checking requirements...
py -m pip install Pillow

echo Starting GIF Generator...
py gui_generator.py
pause