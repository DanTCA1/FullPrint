import os, sys, re, ctypes
from ctypes import wintypes

def cursorPos():
    # Credits to https://stackoverflow.com/questions/35526014/ for the cursor detection script
    OldStdinMode = ctypes.wintypes.DWORD()
    OldStdoutMode = ctypes.wintypes.DWORD()
    kernel32 = ctypes.windll.kernel32
    kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), ctypes.byref(OldStdinMode))
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 0)
    kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(OldStdoutMode))
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    try:
        _ = ""
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        while not (_ := _ + sys.stdin.read(1)).endswith('R'):
            True
        res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
    finally:
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), OldStdinMode)
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), OldStdoutMode)
    if(res):
        return (int(res.group("x")), int(res.group("y")))
    return (-1, -1)

def fullPrint(*args, end="\n"):
    x, y = cursorPos()
    if x != -1: # First detection of where the cursor is
        tLen = x - 1
    else:
        tLen = 0
    text = ""
    nText = "" # nText => New Text
    word = ""
    termLen = os.get_terminal_size().columns # termLen => Terminal Length
    for i in args: # Compile all the print parameters into one string
        text += str(i) + " "
    text = text[:-1]
    for i in text:
        if i != " ":
            word += i
            if i == "\t": # Shorter chars are fine because the cursor script will deal with it
                tLen += 4
            else:
                tLen += 1
        else:
            # Triggered every word, if the word is too long, its put on the next line
            if tLen >= termLen:
                print(nText)
                tLen = len(word)
                nText = word
                word = ""
            else:
                tLen += 1
                nText += word + " "
                word = ""

    if nText.endswith(" ") and len(word) == 0: # If a space is between 2 lines, its ignored because it could be printed later
        nText = nText[:-1]
        tLen -= 1
    if tLen >= termLen:
        print(nText)
        print(word, end="")
    else:
        print(nText + word, end="")
    print(end, end="")