import os

# Older version, new one got deleted
def FullPrint(*args, end="\n"):
    text = ""
    for i in args:
        text += str(i) + " "
    SpaceNum = os.get_terminal_size().columns - 1
    print(" " * SpaceNum, end = "\r")
    print(text, end=end)