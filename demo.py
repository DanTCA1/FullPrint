from fullPrint import fullPrint
from fullPrint import repeatPattern
import time
# \r and repeat pattern showcase
repeatPattern("-", printPattern=True)

print("This is what happens when using print:")
print("Some text\nSome more text", end="\rThis should override the first text, but it doesn't")
print("\n\n")

fullPrint("This is what happens when using fullPrint:")
fullPrint("Some text\nSome more text", end="\rThis overrides the first text (Look in code to see what was overridden)")
fullPrint("\n\n", rmExtraChars=False)

time.sleep(5)

# Extra character removal showcase
repeatPattern("-+", printPattern=True)
print("This part is timed (to show off what is happening).")
print("This is what happens with print (or extra character removal off):")
time.sleep(3)
print("This is a long test sentence.", end="\r")
time.sleep(3)
print("This one is shorter.")
time.sleep(1)

fullPrint("\nThis is what happens with fullPrint:")
time.sleep(2)
fullPrint("This is a long test sentence.", end="\r")
time.sleep(3)
fullPrint("This one is shorter.")