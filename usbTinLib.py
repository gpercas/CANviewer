#!/usr/bin/python
#-*- coding: utf-8 -*-

import serial
import constantsUSB as cntUSB
import modules/queue
import modules/PeriodicThread as thread
import time


class USBTin(object):
	#Region USBTin
	def __init__(self, port, CANbaud, mode):
		"""
		Initializing function for instance USBTin
		
		Parameters:
			- port (str) - COM Virtual port where the USBTin hardware is connected in the format "COMx". - Ex. "COM4"
			- CANbaud (str) - Baudrate for the CAN Channel. Defined by the keys in dictionaries BAUD or canBITRATE from constantsUSB. - Ex. "BAUD_125K" or "canBITRATE_125K"
			- mode (str) - Three possible modes  to open the CAN Channel. Standard mode("Normal"), receiving but not writing ("Listen-Only"), receive own sent messages("Loopback")
		
		Returns:
			None
		"""
		
		#Attributes SerialPort (baudrate - only supported)
		self.SerialPort=serial.Serial()
		self.SerialPort.port=port
		self.SerialPort.baudrate=115200
		self.SerialPort.timeout=0.01
		self.SerialPort.writeTimeout=0.01
		
		#CAN Attributes
		self.baudrate=CANbaud
		self.mode=mode
		self.CANOC="Closed"
		
		#Response and Messages Queues
		self.MSGqueue=queue.Queue()
		self.RPSqueue=queue.Queue()
		
		#FSM attributes
		self.inFrame=b''
		self.state=cntUSB.STATE_INI
		
		#Threads
		self.FSMThread=thread.PeriodicThread(self.processBytes, 0.0001)
		
		self.openSerial()
	
		
		
	def openSerial(self):
		""" 
		Performs a series of actions to establish a communication between the user (PC) and USBtin:
		
		1) Open the serial port.
		2) Initialize Periodic Thread for Finite State Machine function
			
		Parameters:
			None
			
		Returns:
			None
			(Print to the console if port is opened or it have raised an exception)
		"""
		try:
			self.SerialPort.open()
			self.SerialPort.write(bytes('\rC\r','ascii')) #Recommended
			time.sleep(0.05)						#Recommended
			self.SerialPort.write(bytes('C\r','ascii')) 	#Recommended
			self.SerialPort.read(100);			#Recommended
			self.FSMThread.start()
			time.sleep(0.1)
			print("Port is opened.")
			self.RPSqueue.queue.clear()
		except serial.SerialException:
			print("Device not found - The COM port cannot be opened.")
	
	def closeSerial(self):
		"""
		Performs a series of actions to end the communication between the user (PC) and USBtin:
		
		1) Stop Periodic Thread for Finite State Machine function
		2) Close the CAN channel (if it is opened
		3) Close the serial port
			
		Parameters:
			None
		
		Returns:
			None
			(Print to the console when the port is closed)
		"""
		self.FSMThread.cancel()
		self.FSMThread.join()
		if self.CANOC=="Open": self.canClose()
		self.SerialPort.close()
		print("Port is closed.")
		
	def askHWversion(self):
		"""
		Get hardware USBtin version.
		
		Parameters:
			None
		
		Returns:
			String indicating hardware version
		"""
		if self.CANOC=="Closed":
			self.RPSqueue.queue.clear()
			self.SerialPort.write(bytes(cntUSB.usb_VERSION_HW+cntUSB.CR,'ascii'))
			time.sleep(0.2)
			return self.ReadResponse()
		else:
			return cntUSB.canERR_KO
		
	def askFWversion(self):
		"""
		Get firmware USBtin version.
		
		Parameters:
			None
		
		Returns:
			String indicating hardware version
		"""
		if self.CANOC=="Closed":
			self.RPSqueue.queue.clear()
			self.SerialPort.write(bytes(cntUSB.usb_VERSION_FW+cntUSB.CR,'ascii'))
			time.sleep(0.2)
			return self.ReadResponse()
		else:
			return cntUSB.canERR_KO
		
	def askUSBstatus(self):
		"""
		Read status/error flag of can controller
		
		Parameters:
			None
			
		Returns: 
			Fxx[CR] with xx as hexadecimal byte with following error flags:
			
			Bit 0 - not used\n
			Bit 1 - not used\n
			Bit 2 - Error warning (Bit EWARN of MCP2515)\n
			Bit 3 - Data overrun (Bit RX1OVR or RX0OVR of MCP2515)\n
			Bit 4 - not used\n
			Bit 5 - Error-Passive (Bit TXEP or RXEP of MCP2515)\n
			Bit 6 - not used\n
			Bit 7 - Bus error (Bit TXBO of MCP2515)\n
		"""
		if self.CANOC=="Closed":
			self.RPSqueue.queue.clear()
			self.SerialPort.write(bytes(cntUSB.usb_READSTATUS+cntUSB.CR,'ascii'))
			time.sleep(0.1)
			return self.ReadResponse()
		else:
			return cntUSB.canERR_KO
		
	def SerialSetTimestamping(self, x):
		"""
		Set time stamping on/off
		
		Parameters:
			- x (bin): 
			
			0: off
			1: on
			
		Returns:
			None
			(Print to the console if the Time stamping is now on/off/or there is an input error)
			
		
		"""
		self.SerialPort.write(bytes(cntUSB.usb_TIMESTAMPING+str(x)+cntUSB.CR,'ascii'))
		if x==0:
			print("Timestamping Off")
			time.sleep(0.05)
			print(self.ReadResponse())
		elif x==1:
			print("Timestamping On")
			time.sleep(0.05)
			print(self.ReadResponse())
		else:
			print("Timestamping input error!")
			time.sleep(0.05)
			print(self.ReadResponse())
			
			
	#Region CAN
	
	def canOpenChannel(self):
		"""
		Opens the CAN channel in the mode specified on instance attributes.
		By default, the function is called inside openSerial function.
		
		Parameters:
			None
		
		Returns:
			None
			(Print to the console which CAN channel mode have been opened)
		"""
		try:
			self.canSetBitrate(self.baudrate)
		except ValueError:
			return cntUSB.canERR_PARAM
			
		if self.mode == "Normal":
			self.SerialPort.write(bytes(cntUSB.can_OPEN_NORMALMODE+cntUSB.CR,'ascii'))
			print("CAN Channel opened in normal mode")
			self.CANOC="Open"
		elif self.mode == "Listen-only":
			self.SerialPort.write(bytes(cntUSB.can_OPEN_LISTENONLY+cntUSB.CR,'ascii'))
			print("CAN Channel opened in listen-only mode")
			self.CANOC="Open"
		elif self.mode == "Loopback":
			self.SerialPort.write(bytes(cntUSB.can_OPEN_LOOPBACK+cntUSB.CR,'ascii'))
			print("CAN Channel opened in loopback mode")
			self.CANOC="Open"
		else:
			print("CAN channel cannot be opened. Only -Normal-, -Loopback- or -Listen-only- are taken as inputs")
			
		time.sleep(0.1)
		return self.ReadResponse()
			
	def canClose(self):
		"""
		Closes the CAN channel.
		By default, the function is called inside closeSerial function.
		
		Parameters:
			None
			
		Returns:
			- ReadResponse method (constant canERR_OK)
			
		"""
		self.SerialPort.write(bytes(cntUSB.can_CLOSE+cntUSB.CR,'ascii'))
		print("CAN Channel closed")
		time.sleep(0.1)
		self.CANOC="Closed"
		return self.ReadResponse()
		
		
	def canSetBitrate(self, baudrate):
		"""
		Sets baudrate for the CAN channel. It must be set before CAN channel is opened.
		By default, canSetBitrate is called inside openSerial function (with self.baudrate as parameter).
		
		Parameters:
			- baudrate: Defined by the keys in dictionaries BAUD or canBITRATE
		
		Returns:
			None
			(Print to the console if the baudrate is set successfully)
			
		Raises:
			ValueError - if the baudrate value is not standarized nor contained in baudrate dictionaries from constantsUSB
		"""
		if baudrate in cntUSB.BAUD:
			self.SerialPort.write(bytes(cntUSB.can_SETBITRATE+str(cntUSB.BAUD[baudrate])+cntUSB.CR,'ascii'))
			self.baudrate=baudrate
			time.sleep(0.1)
			if self.ReadResponse()==0:
				print("Baudrate is set successfully")
		elif baudrate in cntUSB.canBITRATE:
			self.SerialPort.write(bytes(cntUSB.can_SETBITRATE+str(cntUSB.canBITRATE[baudrate])+cntUSB.CR,'ascii'))
			self.baudrate=baudrate
			time.sleep(0.1)
			if self.ReadResponse()==0:
				print("Baudrate is set successfully")
		else:
			print('Wrong Bitrate Value. Please set a proper value calling USBTin.canSetBitrate() method or change attribute value USBTin.baudrate')
			raise ValueError
			
	def canSetFilter(self, filter):
		self.SerialPort.write(bytes(cntUSB.can_FILTER_CODE+filter+cntUSB.CR,'ascii'))
		time.sleep(0.1)
		print(self.ReadResponse())
		
	def canSetMask(self, mask):
		self.SerialPort.write(bytes(cntUSB.can_FILTER_MASK+mask+cntUSB.CR,'ascii'))
		time.sleep(0.1)
		print(self.ReadResponse())
		
	def canWrite(self,msgId, dlc, messageList, *mask):
		""" 
		Writes a message through the serial port to the CAN channel

		Parameters:
			- msgId (str) -  Message identifier
				- String in hexadecimal format between 000 to 7FF (Integer between 0 and 2047)for standard messages
				- String in hexadecimal format between 00000000 to 1FFFFFFF (Integer between 0  and 536870911) for extended messages.
				
				Zeros are autocompleted in case it is not given the complete expression.
			- dlc (int) - Data Length Code. Indicates the number of data bytes in the message.
				- Integer from 0 to 8. 
			- message (list of str - hex format) 
				- List of strings of data bytes in hexadecimal represntation. List length must be dlc.
			- mask (int) - Multiple parameters can be defined
				- 0x0001: Remote Request Message
				- 0x0002: Standard ID Message
				- 0x0004: Extended ID Message
				
		Returns:
			- ReadResponse method if the message was sent successfully (constant canERR_OK)
			- Error: Explanation Strings if there has been some problem
		"""
		if self.CANOC=="Open":	
			if cntUSB.canMSG_RTR in mask:
				if cntUSB.canMSG_STD in mask:
					msgId=msgId.zfill(3)
					frame_str="r"+msgId.upper()
					if messageList!=[]: return 'Remote Request Message cannot have Data Bytes'
				elif cntUSB.canMSG_EXT in mask:
					msgId=msgId.zfill(8)
					frame_str="R"+msgId.upper()
					if messageList!=[]: return 'Remote Request Message cannot have Data Bytes'
				elif cntUSB.canMSG_EXT in mask and cntUSB.canMSG_STD in mask:
					return "STD and EXT ID messages cannot be defined at the same time. Please choose only one"
				else:
					return "STD or EXT ID message is not defined. Please define it in mask" 
			else:
				if cntUSB.canMSG_STD in mask:
					msgId=msgId.zfill(3)
					frame_str="t"+msgId.upper()
				elif cntUSB.canMSG_EXT in mask:
					msgId=msgId.zfill(8)
					frame_str="T"+msgId.upper()
				elif cntUSB.canMSG_EXT in mask and cntUSB.canMSG_STD in mask:
					return "STD and EXT ID messages cannot be defined at the same time. Please choose only one"
				else:
					return "STD or EXT ID message is not defined. Please define it in mask" 
			frame_str=frame_str+str(dlc)
			for data_byte in messageList:
				frame_str=frame_str+data_byte.zfill(2)
			self.SerialPort.write(bytes(frame_str+cntUSB.CR,'ascii'))
			time.sleep(0.1)
			return self.ReadResponse()
		else: print('CAN Channel is Closed. Message cannot be sent.')
		
	def processBytes(self):
		"""
		If USBTin buffer is not empty, Finite State Machine function is executed.
		processBytes is the run function in the periodic thread "FSMThread"
		
		Parameters:
			None
			
		Returns:
			None
		"""
		while self.SerialPort.inWaiting() != 0:
			self.FSM(self.SerialPort.read())

	def FSM(self, data):
		"""
		Finite State Machine is in charge of classifying data received from USBTin.
		If state == STATE_INI, a new frame is started.
		If state == STATE_MSG or STATE_RPS, the data will be added to the previous started frame.
		When the carriage return is read as data, the frame will be added to the corresponding queue (RPSqueue or MSGqueue, depending on state)
		
		Paramaters:
			- data (byte): Byte of data read from USBTin buffer
			
		Returns:
			None
		"""
		if self.state == cntUSB.STATE_INI:
			data_str=data.decode('ascii')
			if data_str==cntUSB.CHR_cT or data_str==cntUSB.CHR_t or data_str==cntUSB.CHR_cR or data_str==cntUSB.CHR_r:
				self.inFrame=data
				self.state=cntUSB.STATE_MSG
			elif data == bytes(cntUSB.usb_ERR,'ascii'):
				self.RPSqueue.put(data)
				print("CAN Error")
				self.ReadResponse()
			elif data == bytes(cntUSB.CR,'ascii'):
				self.RPSqueue.put(data)
			else:
				self.inFrame=data
				self.state=cntUSB.STATE_RPS
		elif self.state == cntUSB.STATE_MSG:
			if data.decode('ascii') == cntUSB.CR:
				self.MSGqueue.put(self.inFrame)
				self.state = cntUSB.STATE_INI
				self.inFrame=b''
			else:
				self.inFrame=self.inFrame+data #inFrame es bytearray
			
		elif self.state == cntUSB.STATE_RPS:
			if data.decode('ascii')==cntUSB.CR:
				self.RPSqueue.put(self.inFrame)
				self.state=cntUSB.STATE_INI
				self.inFrame=b''
			else:
				self.inFrame=self.inFrame+data
		
		
		
	def ReadResponse(self):
		"""
		Reads and process elements (responses) from RPSqueue (instance attribute)
		
		Parameters:
			None
		
		Returns:
			- Different strings or constants depending on the response to previous messages (indicated on each method)
		"""
		if self.RPSqueue.empty():
			return cntUSB.canERR_NORPS
		else:
			evalRPS=self.RPSqueue.get()
			if evalRPS.decode('ascii') == 'z' or evalRPS.decode('ascii') == 'Z':
				print("Message received")
				return cntUSB.canERR_OK
			elif evalRPS.decode('ascii') == cntUSB.CR:
				return cntUSB.canERR_OK
			elif bytes(cntUSB.usb_READSTATUS, 'ascii') in evalRPS:
				byte_stat=evalRPS.decode()[1:3]
				bin_stat=str(bin(int(byte_stat,16)))[2:].zfill(8)
				return bin_stat
			elif bytes(cntUSB.usb_VERSION_HW, 'ascii') in evalRPS:
				return evalRPS.decode('ascii')
			elif bytes(cntUSB.usb_VERSION_FW, 'ascii') in evalRPS:
				return evalRPS.decode('ascii')
			elif evalRPS == cntUSB.usb_ERR:
				return cntUSB.canERR_KO
			else:
				return evalRPS.decode('ascii')
				
	def canReadMessage(self):
		"""
		Reads and process elements (messages) from MSGqueue (instance attribute)
		
		Parameters:
			None
		
		Returns:
			- List of strings with message in the following format: [msgId mode, msgId, dlc, msgData]
		"""
		frameList=[]
		if self.MSGqueue.empty():
			frameList.append(cntUSB.canERR_NOMSG)
			return frameList
		else:
			evalMSG=self.MSGqueue.get().decode('ascii')
			if cntUSB.CHR_cT in evalMSG:
				frameList.append("Extended")
				frameList.append(evalMSG[1:9])
				frameList.append(evalMSG[9])
				frameList.append(evalMSG[10:])
				return frameList
			elif cntUSB.CHR_t in evalMSG:
				frameList.append("Standard")
				frameList.append(evalMSG[1:4])
				frameList.append(evalMSG[4])
				frameList.append(evalMSG[5:])
				return frameList
			elif cntUSB.CHR_cR in evalMSG:
				frameList.append("Extended RTR")
				frameList.append(evalMSG[1:9])
				frameList.append(evalMSG[9])
				frameList.append(evalMSG[10:])
				return frameList
			elif cntUSB.CHR_r in evalMSG:
				frameList.append("Standard RTR")
				frameList.append(evalMSG[1:4])
				frameList.append(evalMSG[4])
				frameList.append(evalMSG[5:])
				return frameList
			else:
				frameList.append(cntUSB.canERR_PARAM)
				return frameList

