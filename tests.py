import numpy as np
from scipy.special import gammainc
from scipy.fft import *
import matplotlib.pyplot as plt
from math import *
from nist_tests import testsBatteryNIST

with open("timer_random_numbers_rotxor.csv","r") as f:
	data = f.read()

byteStrings = data.rstrip("\n").split("\n")
# Now numbers should have the random numbers in 8-bit strings
numbers = [int(x, 2) for x in byteStrings]
# print(byteStrings[:5])
# print(numbers[:5])

quantityBytes = len(byteStrings)
elementSize = len(byteStrings[0])
numBits = quantityBytes*elementSize


bits = []
for byte in byteStrings:
	for x in byte:
		bits.append(int(x))
bitsString = ''.join(byteStrings)

def vonNeumannAlgorithm(bitsArray):
	length = len(bitsArray)
	newArray = []
	for i in range(length//2):
		if (bitsArray[2*i] ^ bitsArray[2*i+1]):
			newArray.append(bitsArray[2*i])
	return newArray

def makeByteStringArray(bitsArray):
	newArray = []
	for i in range(len(bitsArray)//8):
		temp = ""
		for j in range(8):
			temp += str(bitsArray[8*i+j])
		newArray.append(temp)
	return newArray

def sanityChecks(bitsArray, intArray):
	numBits = len(bitsArray)
	numInts = len(intArray)
	propOnes = sum(bitsArray)/numBits 
	print("Number of bits :",numBits)
	print("Proportion of ones :",propOnes, "Expected proportion :",0.5,"±",2/sqrt(numBits))
	mean = sum(intArray)/numInts
	print("Integers' Mean :", mean,"Standard deviation :",np.std(intArray), "Expected STD :", 255/sqrt(12))
	entropyPerBit = -propOnes*log2(propOnes) - (1-propOnes)*log2(1-propOnes)
	minEntropyPerByte = -log2(max(np.histogram(intArray, bins=256)[0])/numInts)
	print("Shannon Entropy per bit :",entropyPerBit, "bits, Min-Entropy per byte :", minEntropyPerByte,"bits")


# Frequency monobit test
def freqMonobitTest(bitsArray):
	length = len(bitsArray)
	s = abs(2*bitsArray.count(1) - length)/np.sqrt(length) # The test statistic
	# erfc is the Complementary Error Function, imported from math
	p = erfc(s/np.sqrt(2)) # p-value

	print("Frequency monobit test : ", end="")
	if p>0.01:
		print("passed")
	else:
		print("failed")
	print("s = ",s," p-value = ",p)

def freqBlockTest(bitsArray, numBlocks):
	length = len(bitsArray)
	blockLength = length//numBlocks
	bitBlocks = [bitsArray[blockLength*i : blockLength*(i+1)] for i in range(numBlocks) ]
	propOnes = np.array([sum(x)/blockLength for x in bitBlocks])
	chiSquared = 4*blockLength*(sum( (propOnes - 1/2)**2 ))
	p = 1 - gammainc(numBlocks/2, chiSquared/2)

	print("Frequency block test : ", end="")
	if p>0.01:
		print("passed")
	else:
		print("failed")
	print("Chi Squared = ",chiSquared," p-value = ",p)

# Calculating Pi using random numbers and seeing accuracy
def valueOfPiTest(intArray, makePlot = True, label = ""):
	length = len(intArray)
	numCords = length//2
	xCords = intArray[:numCords]
	yCords = intArray[numCords: 2*numCords]
	pointsInCircle = 0
	
	for i in range(numCords):
		if (xCords[i]**2 + yCords[i]**2 <= 255**2):
			pointsInCircle += 1
	piValue = 4*(pointsInCircle/numCords)

	print("Calculated value of Pi : ", piValue)
	print("Actual Pi : ", pi)

	if makePlot:
		plt.figure()
		fig, ax = plt.subplots()
		ax.scatter(xCords, yCords, s=0.5)
		# fig = plt.gcf()
		# ax = fig.gca()
		arc = plt.Circle((0,0), 255, fill = False)
		ax.add_patch(arc)
		ax.set_xlim(0,255)
		ax.set_ylim(0,255)
		if label:
			ax.set_title("Random points in cartesian space to estimate Pi, " + label)
		else:
			ax.set_title("Random points in cartesian space to estimate Pi")

# Runs Test
def runsTest(bitsArray):
	length = len(bitsArray)

	propOnes = sum(bitsArray)/length 

	prereq = bool(abs(propOnes-0.5) < 2/np.sqrt(length))

	v = 1 #initializing the test statistic

	if prereq:
		for i in range(length-1):
			if bitsArray[i] != bitsArray[i+1]:
				v += 1
	
		p = erfc((abs(v - 2*length*propOnes*(1-propOnes)))/(2*np.sqrt(2*length)*propOnes*(1-propOnes))) #p-value
		# erfc is the Complementary Error Function, imported from math

		print("Runs Test : ", end="")
		if p>0.01:
			print("passed")
		else:
			print("failed")
		print("v = ",v," distance from expected v (scaled) = ",(abs(v - 2*length*propOnes*(1-propOnes)))/(2*np.sqrt(2*length)*propOnes*(1-propOnes))," p-value = ",p)
	else:
		print("Frequency test prerequisite was failed, so Runs test not run")

def longestRunsBlockTest(bitsArray):
	length = len(bitsArray)
	if length>=128:
		if length>=6272:
			if length>=75*10**4:
				blockLength = 10**4
			else:
				blockLength = 128
		else:
			blockLength = 8
	else:
		print("Insufficient number of bits for Runs Block Test")
		return
	
	numBlocks = length//blockLength
	bitBlocks = [bitsArray[blockLength*i : blockLength*(i+1)] for i in range(numBlocks) ]
	propOnes = np.zeros(numBlocks)
	freqArray = np.zeros(7)

	for i in range(numBlocks):
		bitBlock = bitBlocks[i]
		propOnes[i] = sum(bitBlock)/blockLength
		index = longestRunIndex(bitBlock, blockLength)
		if index == -1:
			print("Something went wrong, longestRunIndex returned -1")
			return
		freqArray[index] += 1
	
	probArray = []
	if blockLength == 8:
		probArray = [0.2148, 0.3672, 0.2305, 0.1875]
	elif blockLength == 128:
		probArray = [0.1174, 0.2430, 0.2493, 0.1752, 0.1027, 0.1124]
	elif blockLength == 10**4:
		probArray = [0.0882, 0.2092, 0.2483, 0.1933, 0.1208, 0.0675, 0.0727]

	chiSquared = 0
	K = len(probArray)-1
	N_values = {3 : 16, 5 : 49, 6 : 75}
	N = N_values[K]

	for i in range(K+1):
		chiSquared += (freqArray[i] - N*probArray[i])**2/(N*probArray[i])

	p = 1 - gammainc(K/2, chiSquared/2)

	print("Longest Runs Block test : ", end="")
	if p>0.01:
		print("passed")
	else:
		print("failed")
	print("Chi Squared = ", chiSquared, " p-value = ", p)
	print(blockLength, K, probArray, freqArray)

def longestRunIndex(bitsArray, blockLength):
	lengthOfCurrentRun = 0
	lengthOfLongestRun = 0
	for i in range(blockLength):
		if bitsArray[i]==1:
			lengthOfCurrentRun += 1
		else:
			if lengthOfCurrentRun>lengthOfLongestRun:
				lengthOfLongestRun = lengthOfCurrentRun
			lengthOfCurrentRun = 0
	if lengthOfCurrentRun>lengthOfLongestRun:
		lengthOfLongestRun = lengthOfCurrentRun
	
	
	if blockLength == 8:
		if 0<lengthOfLongestRun<4:
			return lengthOfLongestRun-1
		elif lengthOfLongestRun >= 4:
			return 3
	
	elif blockLength == 128:
		if 0<lengthOfLongestRun<=4:
			return 0
		elif 4<lengthOfLongestRun<9:
			return lengthOfLongestRun - 4
		elif lengthOfLongestRun >= 9:
			return 5

	elif blockLength == 10**4:
		if 0<lengthOfLongestRun<=10:
			return 0
		elif 10<lengthOfLongestRun<16:
			return lengthOfLongestRun - 10
		elif lengthOfLongestRun >= 16:
			return 6

	else:
		print("Invalid block length entered.")
		return -1

# Unecessary function
def runsInBlock(bitsArray, blockLength): # Returns the tabulated frequencies
	freqArray = np.zeros(7)
	lengthOfCurrentRun = 0
	bitsArray.append(0)

	if blockLength == 8:
		for i in range(blockLength+1):
			if bitsArray[i]==1:
				lengthOfCurrentRun += 1
			elif 0<lengthOfCurrentRun<4:
				freqArray[lengthOfCurrentRun-1] += 1
			elif lengthOfCurrentRun >= 4:
				freqArray[3] += 1
	
	if blockLength == 128:
		for i in range(blockLength+1):
			if bitsArray[i]==1:
				lengthOfCurrentRun += 1
			elif 0<lengthOfCurrentRun<=4:
				freqArray[0] += 1
			elif 4<lengthOfCurrentRun<9:
				freqArray[lengthOfCurrentRun-4] += 1
			elif lengthOfCurrentRun >= 9:
				freqArray[5] += 1
	
	if blockLength == 10**4:
		for i in range(blockLength+1):
			if bitsArray[i]==1:
				lengthOfCurrentRun += 1
			elif 0<lengthOfCurrentRun<=10:
				freqArray[0] += 1
			elif 10<lengthOfCurrentRun<16:
				freqArray[lengthOfCurrentRun-10] += 1
			elif lengthOfCurrentRun >= 16:
				freqArray[6] += 1

	return freqArray

def matrixRankTest(bitsArray):
	pass

def fourierTransformTest(bitsArray):
	length = len(bitsArray)
	M = abs(fft(2*np.array(bitsArray) - 1)[:length//2])
	T = sqrt(length*log(1/0.05))
	ExpectedNumPeaks = 0.95*length/2
	ActualNumPeaks = np.count_nonzero(M<T)
	d = 2*(ActualNumPeaks - ExpectedNumPeaks)/sqrt(length*0.95*0.05)
	p = erfc(abs(d)/sqrt(2))
	
	print("Fourier Transform test : ", end="")
	if p>0.01:
		print("passed")
	else:
		print("failed")
	print("d = ",d," p-value = ",p)

# All the tests in one function to allow importing them together.
def testsBattery(bitsArray, intArray, makePlots = True, label="", bitmapSize = 128):
	sanityChecks(bitsArray, intArray)
	freqMonobitTest(bitsArray)
	freqBlockTest(bitsArray, 128)
	runsTest(bitsArray)
	# longestRunsBlockTest(bitsArray) # Not workin yet
	fourierTransformTest(bitsArray)
	valueOfPiTest(intArray, makePlots, label)
	# matrixRankTest(bitsArray, 8) Yet to be encoded

	if makePlots:
		if len(bitsArray)>=(bitmapSize**2):
			plt.figure()
			plt.imshow(np.reshape(bitsArray[:bitmapSize**2], (bitmapSize,bitmapSize)))
			if label:
				plt.title("Bitmap, " + label)
			else:
				plt.title("Bitmap")
		else:
			print("Not enough numbers for Bitmap - decrease bitmap size")
		plt.figure()
		plt.plot([*[0],*abs(rfft(bitsArray, norm = "ortho")[1:])])
		# Get rid of the 0th term because it is essentially the sum of the array
		# And so is very high, but does not represent a frequency
		# Note that these frequencies are not in Hz
		if label:
			plt.title("Discrete Fourier Transform of the bitstream, " + label)
		else:
			plt.title("Discrete Fourier Transform of the bitstream")
		plt.figure()
		plt.plot([*[0],*abs(rfft(intArray, norm = "ortho")[1:])])
		if label:
			plt.title("Discrete Fourier Transform of the 8-bit integers, " + label)
		else:
			plt.title("Discrete Fourier Transform of the 8-bit integers")
		plt.figure()
		plt.plot(numbers[:])
		plt.grid(True)
		if label:
			plt.title("Time-series of 8-bit integers, " + label)
		else:
			plt.title("Time-series of 8-bit integers")
		plt.figure()
		plt.hist(intArray, bins = 256)
		if label:
			plt.title("Frequency histogram of the 8-bit integers, " + label)
		else:
			plt.title("Frequency histogram of the 8-bit integers")


# Running Tests

if __name__ == "__main__":
	makePlots = True
	applyVN = False

	if applyVN:
		vnBits = vonNeumannAlgorithm(bits)
		vnByteStrings = makeByteStringArray(vnBits)
		vnNumbers = [int(x, 2) for x in vnByteStrings]

		print("Before Von Neumann : ")
		testsBattery(bits, numbers, makePlots, "Before Von Neumann")
		
		print("\nAfter Von Neumann : ")
		testsBattery(vnBits, vnNumbers, makePlots, "After Von Neumann")
	
	else:
		testsBattery(bits, numbers, makePlots)
		testsBatteryNIST(bitsString)

	plt.show()
