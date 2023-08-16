import serial

class OpenAFE:
	
	def __init__(self, comPort):
		self.ser = serial.Serial(comPort, 115200)


	def getMessageFromOpenAFE(self):
		"""
		The function `getMessageFromOpenAFE` reads a message from a serial port, checks its checksum, and
		returns the message if the checksum is valid, otherwise it returns -1.
		:return: either the message received from OpenAFE if the checksum is valid, or -1 if the checksum is
		not valid.
		"""
		messageReceived=str(self.ser.readline())
		rawMessage = messageReceived[2:][:-5]
		
		# check the message's checksum ...
		calculatedChecksum = self.calculateChecksumOfString(messageReceived[3:][:-8])
		checksumInMessage = self.getChecksumIntegerFromString(rawMessage[-2:])

		if (calculatedChecksum - checksumInMessage) == 0:
			# checksum is valid
			message = messageReceived[3:][:-8] 
			return message
		else :
			# checksum is not valid
			return -1


	def calculateChecksumOfString(self, string):
		"""
		The function `calculateChecksumOfString` calculates the checksum of a given string by performing a
		bitwise XOR operation on the ASCII values of its characters.
		
		:param string: The parameter "string" is a string of characters for which we want to calculate the
		checksum, e.g.: "CVW,500,-500,250,2,1".
		:return: the checksum of the given string, e.g.: 119 (0x77).
		"""
		checksum = 0
		for char in string:
			checksum = (checksum ^ ord(char))
		return checksum


	def getChecksumIntegerFromString(self, checksumString):
		"""
		The function `getChecksumIntegerFromString` converts a string representation of a checksum into an
		integer value.
		
		:param checksumString: The `checksumString` parameter is a string that represents a checksum, e.g.: "32".
		:return: an integer checksum value e.g.: 50 (0x32).
		"""
		integerChecksum = 0
		index = 1

		for char in checksumString:
			if ord(char) < 0x41:
				integerChecksum |= (ord(char) - 0x30) << (index * 4)
			else:
				integerChecksum |= (ord(char) - 0x37) << (index * 4)
			index -= 1

		return integerChecksum


	def sendCommandToMCU(self, command):
		"""
		The function `sendCommandToMCU` sends a command to a microcontroller unit (MCU) by calculating a
		checksum, constructing a full command string, and writing it to a serial port.
		
		:param command: The `command` parameter is a string that represents the command to be sent to the
		MCU (Microcontroller Unit), e.g.: "CVW,500,-500,250,2,1".
		"""
		checksumString = hex(self.calculateChecksumOfString(command))
		checksumString = checksumString[2:] # removes the "0x"
		fullCommand = "$" + command + "*" + checksumString
		self.ser.write(fullCommand.encode("utf-8"))


	def makeCyclicVoltammetry(self, endingPotential, startingPotential, scanRate, stepSize, numberOfCycles, settlingTime):
		"""
		The function "makeCyclicVoltammetry" sends a command string to a microcontroller unit (MCU) to
		perform cyclic voltammetry with specified parameters.
		
		:param endingPotential: The ending potential is the final voltage value at which the cyclic
		voltammetry will stop. It is a floating-point number representing the voltage in volts, in millivolts (mV)
		:param startingPotential: The starting potential is the initial voltage at which the cyclic
		voltammetry experiment begins, in millivolts (mV)
		:param scanRate: The scan rate is the rate at which the potential is swept during the cyclic
		voltammetry experiment. It is usually expressed in millivolts per second (mV/s)
		:param stepSize: The step size is the increment or decrement in potential applied during each step
		of the cyclic voltammetry experiment. It determines the resolution of the measurement and can be
		positive or negative, in millivolts (mV)
		:param numberOfCycles: The numberOfCycles parameter specifies the number of cycles to perform in the
		cyclic voltammetry experiment
		:param settlingTime: The settlingTime parameter refers to the time in seconds that the system should
		wait before starting the cyclic voltammetry measurement. This allows the system to stabilize and
		reach a steady state before the measurement begins, in milliseconds (ms)
		"""
		CVCommandString = "CVW," + str(endingPotential) + "," + str(startingPotential) + \
		"," + str(scanRate) + "," + str(stepSize) + "," + str(numberOfCycles)
		self.sendCommandToMCU(CVCommandString) # send the CV command