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
    """
    Acts like a normal print operator, with infinite args, and an end value, but supports multi-line operations.

    Params: *args, end="\\n"
    Returns: Line count printed (1 based index)

    An end of "\\r" will return to the beginning of the string, even if it spanned multiple lines
    """
    x, y = cursorPos()
    if x != -1: # First detection of where the cursor is
        tLen = x - 1
    else:
        tLen = 0
    text = ""
    nText = "" # nText => New Text
    word = ""
    lines = 1
    termLen = os.get_terminal_size().columns # termLen => Terminal Length

    for i in args: # Compile all the print parameters into one string
        text += str(i) + " "
    text = text[:-1]
    for i in text:
        if i == "\n": # Lines are added with \n
            if tLen >= termLen:
                print(nText)
                print(word)
                lines += (len(nText + word) // termLen) + 1
            else:
                print(nText + word)
                lines += 1
            nText = ""
            word = ""
            tLen = 0
        elif i != " ":
            word += i
            if i == "\t": # Shorter chars are fine because the cursor script will deal with it
                tLen += 4
            else:
                tLen += 1
        else:
            # Triggered every word, if the word is too long, its put on the next line
            if tLen >= termLen:
                lines += (len(nText) // termLen) # If a word is long enough, it could take up multiple lines. The entire word is still printed, without any \n incase the terminal becomes wider
                if len(nText) == 0: # Case where the one word is the only thing on the whole line
                    print(word + " ")
                    tLen = 0
                    nText = ""
                else:
                    print(nText)
                    tLen = len(word)
                    nText = word + " "
                word = ""
            else:
                tLen += 1
                nText += word + " "
                word = ""

    if tLen >= termLen:
        print(nText)
        print(word, end="")
    else:
        print(nText + word, end="")

    lines += (len(nText) // termLen)
    if end.find("\r") + 1:
        for _ in range(lines - 1):
            print("\033[F", end="")
    print(end, end="")
    return(lines)