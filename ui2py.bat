@echo OFF
cd D:\users\khaled\Work\lab_with_dr_moshe\PC_GUI_App
pyuic5 UI/QTUI.ui -o QTUI.py
move QTUI.py UIwPy/QTUI.py