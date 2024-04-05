import os, sys, re
if(sys.platform == "win32"):
    import ctypes
    from ctypes import wintypes
else:
    import termios

mode = 3
relConsolePos = -1 # relConsolePos => relative console position

def cursorPos():
    # Credits to https://stackoverflow.com/questions/35526014/ for the cursor detection script
    if(sys.platform == "win32"):
        OldStdinMode = ctypes.wintypes.DWORD()
        OldStdoutMode = ctypes.wintypes.DWORD()
        kernel32 = ctypes.windll.kernel32
        kernel32.GetConsoleMode(kernel32.GetStdHandle(-10), ctypes.byref(OldStdinMode))
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 0)
        kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(OldStdoutMode))
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    else:
        OldStdinMode = termios.tcgetattr(sys.stdin)
        _ = termios.tcgetattr(sys.stdin)
        _[3] = _[3] & ~(termios.ECHO | termios.ICANON)
        termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, _)
    try:
        _ = ""
        sys.stdout.write("\x1b[6n")
        sys.stdout.flush()
        while not (_ := _ + sys.stdin.read(1)).endswith('R'):
            True
        res = re.match(r".*\[(?P<y>\d*);(?P<x>\d*)R", _)
    finally:
        if(sys.platform == "win32"):
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), OldStdinMode)
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), OldStdoutMode)
        else:
            termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, OldStdinMode)
    if(res):
        return (int(res.group("x")), int(res.group("y")))
    return (-1, -1)

def up():
    """
    Returns an ANSI sequence for going one line up in console
    """
    return "\033[F"

def repeatPattern(pattern, end="", fitPattern=True, printPattern=False):
    """
    Prints a pattern across the whole width of the console

    FitPattern options:
    True : repeat until pattern won't fit
    |-=-=-=-=-= |
    False : repeat until entire console is filled (Doesn't work with fitPattern)
    |-=-=-=-=-=-|

    printPattern=True will result in more consistent results if ANSI sequences are in the pattern
    Returns string when printPattern = False, returns 1 when printPattern = True
    """
    fString = "" # fString => Final String
    termLen = os.get_terminal_size().columns # termLen => Terminal Length
    patternLen = 0
    endLen = 0

    if pattern == "":
        return

    if printPattern == False:
        patternLen = len(pattern)
        endLen = len(end)
    else:
        print(pattern, end="")
        x, _ = cursorPos()
        patternLen = x - 1
        print("\r", end="")

        print(end, end="")
        x, _ = cursorPos()
        endLen = x - 1
        print("test\r", end="")

    fString = pattern * ((termLen - endLen) // patternLen)
    if end != "":
        fString += end
    elif fitPattern == False:
        fString += pattern[0 : (termLen - endLen) % patternLen - 1]
    
    if printPattern == False:
        return fString
    fullPrint(fString, modeOverride=0)
    return 1

def saveConsolePos():
    """
    Saves the console position to be used later. 
    Call loadConsolePos to go back to where this was called.
    """
    global relConsolePos
    relConsolePos = 0

def loadConsolePos():
    """
    Loads the console position previously saved.
    Call saveConsolePos to save a position, and use this to go to it

    Calling this function keeps the old save intact, for use later
    """
    global relConsolePos
    if relConsolePos >= 0:
        print("\r", end="")
        if relConsolePos > 0:
            for _ in range(relConsolePos):
                print("\033[F", end="")
        saveConsolePos()


def setPrintMode(newMode = -1):
    """
    Sets the mode of extra character removal for the fullPrint operator. Returns the current mode (new mode if it was just set).
    NOTE: Only mess with this if you are using ANSI or other methods to change the background color, this will not have any effect otherwise.

    Available modes:
    0 : Inactive (Turns extra character removal off)
    1 : Start of line reset (resets ANSI, clears line, user data)
    2 : End of line reset (prints user data, resets ANSI, clears end of line)
    3 : End of line inherit (prints user data, clears end of line)
    4 : Double print clear (prints ALL lines of user data, resets ANSI, prints spaces, prints user data again)

    Extra character removal is useful when printing on the same line multiple times, using \\r, as the previous text will not be erased automatically.
    """
    global mode
    if newMode in range(0,5):
        mode = newMode
    return mode

def fullPrint(*args, end="\n", modeOverride=None):
    """
    Acts like a normal print operator, with infinite args, and an end value, but supports multi-line operations.

    Params: *args, end="\\n", modeOverride
    Returns: Line count printed (How many lines down it went, if it only moved right, not down, 0 is returned)

    An end of "\\r" will return to the beginning of the string, even if it spanned multiple lines
    """

    if not modeOverride in range(0,5) and modeOverride != None:
        raise Exception("ModeOverride not in range 0-5")

    # Var init.
    global relConsolePos, mode
    charLeft = 0 # charLeft => characters left (in string)
    currentIdx = 0
    lines = 0
    text = ""
    termLen = os.get_terminal_size().columns + 1 # termLen => Terminal Length


    for i in args: # Compile all the print parameters into one string
        text += str(i) + " "
    text = text[:-1]


    if len(text + end) == 0: # If nothing is printed, don't run the expensive cursor script
        return 0


    x, _ = cursorPos()
    if x != -1: # First detection of where the cursor is
        charLeft = termLen - (x - 1)
    else:
        charLeft = termLen


    backTriggered = True
    backIdx = 999999 # Specifies the idx at which the print has to go back to the beginning (multi-span)
    if end.find("\r") + 1:
        backIdx = end.find("\r") + len(text)
        backTriggered = False
    text += end


    i = 0
    while i <= len(text) + 1:
        i += 1
        if i > len(text):
            raise Exception("Woops! fullPrint has entered an infinite loop! Please contact us if you see this error.")

        # XXX \n processing, Priority: Med. XXX
        nPrint = "" # nPrint => \n print
        while text.find("\n", currentIdx, min(currentIdx + charLeft, backIdx)) != -1:
            downLoc = text.find("\n", currentIdx, min(currentIdx + charLeft, backIdx)) # downLoc => down location
            nPrint += text[currentIdx : downLoc] + "\n"
            currentIdx = downLoc + 1
            charLeft = termLen
            lines += 1
            # Gets the location of a \n, takes a slice from the beginning, to the \n, and then starts from there onward
        print(nPrint, end="") # Text is compiled and then printed afterwards because calling print is s l o w

        # XXX Space processing, Priority: Low XXX
        spaceLoc = text.rfind(" ", currentIdx, min(currentIdx + charLeft, backIdx))
        if spaceLoc != -1:
            print(text[currentIdx : spaceLoc])
            currentIdx = spaceLoc + 1
            charLeft = termLen
            lines += 1
            # Gets the location of the last space on the line, and moves the word to the next one
        else:
            spaceLoc = text.find(" ", currentIdx, min(len(text), backIdx))
            if spaceLoc == -1:
                downLoc = text.find("\n", currentIdx, len(text))
                if downLoc == -1:
                    downLoc = 999999
                spaceLoc = min(downLoc, len(text), backIdx) - 1
                # In case the word is longer then the terminal, and the word doesn't end until the \r or the end of the string
            temp = text[currentIdx : spaceLoc + 1]
            print(temp, end="")
            currentIdx = spaceLoc + 1
            charLeft = termLen - (len(temp) % termLen)
            lines += len(temp) // termLen
            # If the word is longer then the terminal, print the entire thing with no \n, in case the terminal ever gets bigger


        # XXX \r processing, Priority: High XXX
        if currentIdx == backIdx:
            backTriggered = True
            backIdx = 999999
            if text[currentIdx] != "\r":
                # This can only be reached if backIdx was wrong
                raise Exception("fullPrint has reached a case it cannot handle when processing \\r. Please contact us if you see this error.")
            else:
                for _ in range(lines):
                    print("\033[F", end="")
                print("\r", end="")
                charLeft = termLen
                lines = 0
        

        # XXX Checks if it's done printing XXX
        if currentIdx == len(text):
            break

    # Only triggers when the snippet above wasn't run
    if not backTriggered:
        raise Exception("fullPrint hasn't handled \\r correctly. Please contact us if you see this error.")
    relConsolePos += lines
    return(lines)