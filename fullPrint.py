import os
import sys
import re
import types
import re
from typing import Literal
if(sys.platform == "win32"):
    import ctypes
    from ctypes import wintypes
else:
    import termios

relConsolePos = -1 # relConsolePos => relative console position
sepDefault = " "
endDefault = "\n"
rmExtraCharsDefault = True
cursorCheckDefault = False
maintainWordsDefault = True

# fullPrint constants
upANSI = "\033M"

def _cursorPos():
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

def ANSILength(
    text: str,
    invalidANSI: bool=False
) -> tuple[int, list[tuple[int, int]]]:
    """Returns the length of the string (compensating for ANSI sequences), and optionally returns the location of the ANSI sequences
    
    Args:
        text: Text to measure
        invalidANSI: Whether to include invalid ANSI sequences in the length calculation (regex is more inclusive, but may take longer)
    Returns:
        Tuple:
        - Length of the string
        - List of the locations of the ANSI sequences (tuple of start and end)

    ## Notes
        - Invalid ANSI sequences are sequences that don't follow the ANSI sequence format, however, they still absorb characters when printed to console
    """
    if invalidANSI:
        regex = re.compile(r"\x1b\s*(?:[\[\?](?:[0-9\s]*;\"[^\"]*\")?[^a-zA-Z]*)?(?:[a-zA-Z]|$)", re.DOTALL)
    else:
        regex = re.compile(r"\x1b(?:[\[][\?]?(?:[0-9]*;\"[^\"]*\")?[0-9;]*)?(?:[a-zA-Z])", re.DOTALL)

    sequences = []

    for match in regex.finditer(text):
        sequences.append((match.start(), match.end()))

    textLen = len(text)

    for sequence in sequences:
        textLen -= sequence[1] - sequence[0]

    return (textLen, sequences)
    
def repeatPattern(
    pattern: str,
    end: str="",
    fitPattern: bool=True,
    printPattern=False
) -> str | None:
    """Prints a pattern across the whole width of the console

    FitPattern options:

    True : repeat until pattern won't fit `|123,123, |`

    False : repeat until entire console is filled (Doesn't work with end) `|123,123,1|`

    Args:
        pattern: Pattern to repeat
        end: String appended after the pattern can no longer be repeated
        fitPattern: Described above
        printPattern: Prints the pattern, increases consistency if ANSI sequences are in the pattern
    Returns:
        String when printPattern = False, returns None when printPattern = True
    """
    fString = "" # fString => Final String
    termLen = os.get_terminal_size().columns # termLen => Terminal Length
    patternLen = 0
    endLen = 0

    if printPattern == False:
        patternLen = len(pattern)
        endLen = len(end)
    else:
        print("\r" + pattern, end="")
        x, _ = _cursorPos()
        patternLen = x - 1
        print("\r", end="")

        print("\r" + end, end="")
        x, _ = _cursorPos()
        endLen = x - 1
        print("\r", end="")

    fString = pattern * ((termLen - endLen) // patternLen)
    if end != "":
        fString += end
    elif fitPattern == False:
        fString += pattern[0 : (termLen - endLen) % patternLen - 1]
    
    if printPattern == False:
        return fString
    print(fString)
    return None

def padToLength(
    text: str,
    length: int,
    padChar: str=" ",
    end: str="",
    rmExtraChars: bool=True,
    printPattern=False
) -> tuple[str, int]:
    """Pads a string to a certain length, with a certain character

    Args:
        text: Text to pad
        length: Length to pad to
        padChar: Character to pad with. Defaults to " ".
        end: String appended after the padding.
        rmExtraChars: Controls whether extra character removal is on or off (remove text after the pad). Defaults to on.
    Returns:
        Tuple:
        - String return / printed string
        - Positive int if padding was added, negative int if text was longer than requested padding, 0 if no padding was added
    """

    if printPattern: # If the pattern is printed, the offset is calculated differently
        offset = fullPrint(text, rmExtraChars=rmExtraChars, end="").x
        if offset == None:
            patternCount = 0
        else:
            patternCount = (length - offset) // len(padChar)
    else:
        patternCount = (length - len(text)) // len(padChar)

    if printPattern:
        if patternCount > 0:
            print(padChar * patternCount, end="")
        print("", end=end)

    return (text + padChar * patternCount + end, patternCount * len(padChar))

def saveConsolePos() -> None:
    """Saves the console position to be used later. 

    Call loadConsolePos to go back to where this was called.
    """
    global relConsolePos
    relConsolePos = 0

def loadConsolePos() -> None:
    """Loads the console position previously saved.
    Calling this function keeps the old save intact, for use later

    Call saveConsolePos to save a position, and use this to go to it
    """
    global relConsolePos
    if relConsolePos >= 0:
        print("\r", end="")
        if relConsolePos > 0:
            for _ in range(relConsolePos):
                print("\033[F", end="")
        saveConsolePos()

def setDefaults(
    sep: str = " ",
    end: str = "\n",
    rmExtraChars: bool = True,
    cursorCheck: bool = False,
    maintainWords: bool = True
) -> None:
    """Sets the default values for the fullPrint function.
    
    Check fullPrint for more information on the parameters.
    """
    global sepDefault, endDefault, rmExtraCharsDefault, cursorCheckDefault, maintainWordsDefault
    sepDefault = sep
    endDefault = end
    rmExtraCharsDefault = rmExtraChars
    cursorCheckDefault = cursorCheck
    maintainWordsDefault = maintainWords

def fullPrint(
    *values: object,
    sep: str = sepDefault,
    end: str = endDefault,
    rmExtraChars: bool = rmExtraCharsDefault,
    cursorCheck: bool = cursorCheckDefault,
    maintainWords: bool = maintainWordsDefault
) -> object:
    """Acts like a normal print operator, with infinite args, and an end value, but supports multi-line operations and ANSI tools.

    Args:
        *values: Values to be printed.
        sep: String inserted between values, default is " ".
        end: String appended after the last value, default is "\\n".
        rmExtraChars: Controls whether extra character removal is on or off (Check examples.py or below for more details). Defaults to on.
        cursorCheck: Checks where the cursor is using \\x1b[6n (Check below for more details). This is only useful when ANSI sequences are present, or if characters disappear. Default is off.
        maintainWords: If a word is longer then the terminal, selects whether to split the word or not with \\n. Default is on.
    Returns:
        y: Line count printed (How many lines down it went, 0 is returned if the print finished on the same line)
        x: Offset of the last printed character (How many characters to the right the last printed character is from the start, None is returned if more than one line was printed)

    ## Notes
        - WARNING: Having cursorCheck set to true can have a detrimental effect to performance (3x-5x performance reduction)
        - WARNING: Having maintainWords set to false can ruin ANSI sequences if they span multiple lines
        - An end of "\\r" will return to the beginning of the string, even if it spanned multiple lines.
        - Extra character removal is useful when making status bars, or when \\r is commonly used to reprint over existing text.
        - CursorCheck is useful when sequences are printed that may disappear (like ANSI), or when characters are longer than 1 character (like \\t)
        - CursorCheck being active WILL NOT fix any issues that are caused with ANSI strings alongside a word longer then the length of the terminal
        - When maintainWords is true, words spanning multiple lines will wordwrap, and will expand when the terminal is resized
    """

    # Var init.
    global relConsolePos
    charLeft = 0 # charLeft => characters left (in string)
    currentIdx = 0
    lines = 0
    offset = 0
    text = ""
    termLen = os.get_terminal_size().columns + 1 # termLen => Terminal Length
    rmChar = "\033[0K" if rmExtraChars else ""


    for i in values: # Compile all the print parameters into one string
        text += str(i) + sep
    if len(sep) != 0: # Remove the last separator
        text = text[:0 - len(sep)]


    if len(text + end) == 0: # If nothing is printed, don't run the expensive cursor script
        return(types.SimpleNamespace(y=0, x=0))

    x = -1
    if cursorCheck:
        x, _ = _cursorPos()
    if x != -1: # First detection of where the cursor is
        charLeft = termLen - (x - 1)
        startPos = x - 1
    else:
        charLeft = termLen
        startPos = 0


    backTriggered = True
    backIdx = 999999 # Specifies the idx at which the print has to go back to the beginning (multi-span)
    if end.find("\r") + 1:
        backIdx = end.find("\r") + len(text)
        backTriggered = False
    text += end


    i = 0
    endWordCheck = False # Special case used with ANSI and long words, to make a newline if no more words could fit on the current line 
    while i <= len(text) + 1:
        i += 1
        if i > len(text) + 1:
            raise Exception(
                f"Woops! fullPrint has entered an infinite loop! Please contact us if you see this error. (Main process, {termLen})"
            )

        # region XXX \n & \r processing, Priority: High XXX
        qPrint = "" # qPrint => queue print
        downLoc = text.find("\n", currentIdx, min(currentIdx + charLeft, backIdx + 1)) # downLoc => down location
        backLoc = text.find("\r", currentIdx, min(currentIdx + charLeft, backIdx + 1)) # backLoc => back location
        j = 0

        while downLoc != -1 or backLoc != -1:
            # Gets the location of a \n or \r, takes a slice from the beginning, to the \n, and then starts from there onward
            j += 1
            if j > len(text):
                raise Exception(
                    f"Woops! fullPrint has entered an infinite loop! Please contact us if you see this error. (\\n & \\r process, {termLen})"
                )
            endWordCheck = False
            downLoc = downLoc if downLoc >= 0 else 999999
            backLoc = backLoc if backLoc >= 0 else 999999
            if downLoc < backLoc:
                qPrint += text[currentIdx : downLoc] + rmChar + "\n"
                lines += 1
            else:
                if backLoc == backIdx:
                    qPrint += text[currentIdx : backLoc]
                    currentIdx = backLoc
                    charLeft = termLen
                    break
                else:
                    qPrint += text[currentIdx : backLoc] + rmChar + "\r"
            currentIdx = min(downLoc, backLoc) + 1
            charLeft = termLen
            downLoc = text.find("\n", currentIdx, min(currentIdx + charLeft, backIdx + 1))
            backLoc = text.find("\r", currentIdx, min(currentIdx + charLeft, backIdx + 1))
        
        if len(qPrint) != 0:
            offset = None
            print(qPrint, end="") # Text is compiled and then printed afterwards because calling print is s l o w

        # endregion

        # region XXX \r (in end) processing, Priority: Highest XXX
        if currentIdx == backIdx:
            backTriggered = True
            backIdx = 999999
            if text[currentIdx] != "\r":
                # This can only be reached if backIdx was wrong
                raise Exception("fullPrint has reached a case it cannot handle when processing \\r. Please contact us if you see this error.")
            else:
                for _ in range(lines):
                    print("\033M", end="")
                print("\r", end="")
                charLeft = termLen
                lines = 0

        # endregion

        # region XXX Near finish / finish checking, Priority: Medium XXX/
        if currentIdx == len(text):
            break
        if charLeft > len(text) - currentIdx:
            print(text[currentIdx:] + rmChar, end="")
            if offset != None:
                if cursorCheck:
                    x, _ = _cursorPos()
                    offset = x - 1 - startPos
                else:
                    offset = len(text) - currentIdx
            break

        # endregion

        # region XXX Space processing, Priority: Low XXX
        spaceLoc = text.rfind(" ", currentIdx, min(currentIdx + charLeft, backIdx))
        if spaceLoc != -1:
            if spaceLoc == min(currentIdx + charLeft, backIdx) - 1:
                print(text[currentIdx : spaceLoc], end="")
            else:
                print(text[currentIdx : spaceLoc] + rmChar, end="")
            charLeft = charLeft - len(text[currentIdx : spaceLoc])
            currentIdx = spaceLoc + 1
            if cursorCheck:
                x, _ = _cursorPos()
                if x - 1 != termLen - charLeft:
                    endWordCheck = True
                    charLeft = termLen - x
                    print(sep, end="")
                    continue
            offset = None
            endWordCheck = False
            print("\n", end="")
            charLeft = termLen
            lines += 1
            # Gets the location of the last space on the line, and moves the word to the next one
        else:
            offset = None
            if endWordCheck:
                print("\n", end="")
                charLeft = termLen
                lines += 1
                endWordCheck = False
                continue
            spaceLoc = text.find(" ", currentIdx, min(len(text), backIdx))
            if spaceLoc == -1:
                # In case the word is longer then the terminal, and the word doesn't end until the \r or the end of the string
                downLoc = text.find("\n", currentIdx, len(text))
                backLoc = text.find("\r", currentIdx, len(text))

                downLoc = downLoc if downLoc >= 0 else 999999
                backLoc = backLoc if backLoc >= 0 else 999999

                spaceLoc = min(downLoc, backLoc, len(text), backIdx) - 1

            temp = text[currentIdx : spaceLoc + 1]
            if maintainWords:
                print(temp, end="")
            else: # TODO: Implement cursor checking before going down (keep ANSI in mind). Maybe just have a black box ~8 characters after a sequence?
                split = currentIdx + charLeft - 1
                print(text[currentIdx : split] + "\n" + text[split : spaceLoc + 1], end="")
            currentIdx = spaceLoc + 1
            if cursorCheck:
                x, _ = _cursorPos()
                charLeft = termLen - x
            else:
                charLeft = termLen - (len(temp) % termLen)
            lines += len(temp) // termLen
            endWordCheck = True
            # If the word is longer then the terminal, print the entire thing with no \n, in case the terminal ever gets bigger
    
    # endregion

    # Only triggers when the \r code isn't run
    if not backTriggered:
        raise Exception(
            "fullPrint hasn't handled \\r correctly. Please contact us if you see this error."
        )
    relConsolePos += lines
    return(types.SimpleNamespace(y=lines, x=offset))
