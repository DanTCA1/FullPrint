import os

# Older version, new one got deleted
def FullPrint(*args, end="\n"):
    text = ""
    tLen = 0
    nText = ""
    word = ""
    termLen = os.get_terminal_size().columns # termLen => Terminal Length
    for i in args:
        text += str(i) + " "
    for i in text:
        word += i
        tLen += 1
        if i == " ":
            if tLen >= termLen:
                print(nText)
                tLen = len(word)
                nText = word
            else:
                nText += word
    print(" " * termLen - 1, end = "\r")
    print(text, end=end)