import serial
import matplotlib.pyplot as plt
from time import time

arduinoSerialData = serial.Serial('/dev/cu.usbmodem101',9600) #Create Serial port object called arduinoSerialData

numbers = []
count = 0
size = 2**10

while (count < size):
    if (arduinoSerialData.inWaiting()>0):
        data = arduinoSerialData.readline()
        numbers.append(data)
        count += 1
print(numbers[:5])


# startTime = time()
# numbers.append(arduinoSerialData.read(size))
# elapsedTime = time() - startTime


plt.bar(numbers)
with open("timer_random_numbers.csv", w) as f:
    for x in numbers:
        f.write(x)
        f.write("\n")
