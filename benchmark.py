import fullPrint, time

testType = {
    "Empty":"",
    "Small":"this is a small sentence",
    "Large":"This is a sentence that should span multiple lines if I coded it correctly which I think I did, but I might not have, I don't know This is another sentence that should span multiple lines if I coded it correctly which I think I did, but I might not have, I don't know pt 2",
    "SpaceBar Spam":"h  i     t  h  e  r  e     h  o  w     a  r  e     y  o  u  ?",
    "\\n Spam":"h\ni\n \nt\nh\ne\nr\ne\n \nh\no\nw\n \na\nr\ne\n \ny\no\nu\n?",
}

printTime = 1
results = []
for text in testType.values():
    lines = fullPrint.fullPrint(text).y
    print(fullPrint.up() * lines, end="")
    up = fullPrint.up() * lines
    fullCount = 0
    startTime = time.time()
    while time.time() <= startTime + printTime:
        for _ in range(1000):
            fullPrint.fullPrint(text)
            print(up, end="")
        fullCount += 1
    
    printCount = 0
    startTime = time.time()
    while time.time() <= startTime + printTime:
        for _ in range(1000):
            print(text)
            print(up, end="")
        printCount += 1
    
    results.append((fullCount, printCount))

print("\n" * 20)
print("Test results (fullPrint vs print):")
i = 0
for test in testType.keys():
    print(f"{test}: {results[i][0]}k ops. VS {results[i][1]}k ops.")
    i+= 1