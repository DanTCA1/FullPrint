import os

# Older version, new one got deleted
def fullPrint(*args, end="\n"):
    text = ""
    tLen = 0
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
            if tLen >= termLen:
                print(nText)
                tLen = len(word)
                nText = word
                word = ""
            else:
                nText += word
                word = ""
    
    if tLen >= termLen:
        print(nText)
        print(word, end="")
    else:
        print(nText, end="")
    print(end, end="")