import os
import sys

if "linux" not in sys.platform and "win" not in sys.platform:
    print("mac sucks, change to windows at least, or to linux like real men!")
    print("install it manually, your fault for having mac")
    exit()

print("starting setup!")

ans = input("would you like to use the virtual environment provided by the developer\nor install the dependencies with pip: [y/n]: ")
while ans not in ["y", "n"]:
    ans = input("would you like to use the virtual environment provided by the developer\nor install the dependencies with pip: [y/n]: ")

if ans == "y":
    if "linux" in sys.platform:
        os.system("./linenv/Scripts/activate.sh")
    elif "win" in sys.platform:
        os.system("./winenv/Scripts/activate.bat")
    print("virtual environment activated!")
else:
    if "linux" in sys.platform:
        os.system("pip3 install -r requirements.txt")
    elif "win" in sys.platform:
        os.system("pip install -r requirements.txt")

print("setup finished successfully!")
