import os, sys, re, ctypes
from ctypes import wintypes

def cursorPos():
    # Credits to https://stackoverflow.com/questions/35526014/
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
    if x != -1:
        tLen = x - 1
    else:
        tLen = 0
    text = ""
    nText = ""
    word = ""
    termLen = os.get_terminal_size().columns # termLen => Terminal Length
    for i in args:
        text += str(i) + " "
    text = text[:-1]
    for i in text:
        word += i
        if i == "\t":
            tLen += 4
        else:
            tLen += 1
        if i == " ":
            if tLen >= termLen + 1: # I think this works because the space adds a char
                print(nText)
                tLen = len(word)
                nText = word
                word = ""
            else:
                nText += word
                word = ""
    
    if tLen >= termLen + 1:
        print(nText)
        print(word, end="")
    else:
        print(nText + word, end="")
    print(end, end="")