import usbTinLib as usb
import time
import random

hexByte='0123456789ABCDEF'
dlcList=[0,1,2,3,4,5,6,7,8]


def randomMsg(instUSB):
	mode=random.choice([0,1])
	if mode==0:
		idMode=random.choice([2,4])
		if idMode==2:
			id=random.choice('01234567')
			for i in range(2):
				id=id+random.choice(hexByte)
			dlc=random.choice(dlcList)
			Msg=[]
			for i in range(dlc):
				byteData=''
				for i in range(2):
					byteData=byteData+random.choice(hexByte)
				Msg.append(byteData)	
			instUSB.canWrite(id,dlc,Msg,0x0002)
		else:
			id=random.choice('01')
			for i in range(7):
				id=id+random.choice(hexByte)
			dlc=random.choice(dlcList)
			Msg=[]
			for i in range(dlc):
				byteData=''
				for i in range(2):
					byteData=byteData+random.choice(hexByte)
				Msg.append(byteData)
			instUSB.canWrite(id,dlc,Msg,0x0004)
	
	else:
		idMode=random.choice([2,4])
		if idMode==2:
			id=random.choice('01234567')
			for i in range(2):
				id=id+random.choice(hexByte)
			instUSB.canWrite(id,random.choice(dlcList),[],0x0001,0x0002)
		else:
			id=random.choice('01')
			for i in range(7):
				id=id+random.choice(hexByte)
			instUSB.canWrite(id,random.choice(dlcList),[],0x0001,0x0004)

if __name__ == "__main__":
			
	usb1=usb.USBTin('COM5','BAUD_125K','Normal')
	usb1.canOpenChannel()

	for i in range(100):
		randomMsg(usb1)
		time.sleep(0.01)

	usb1.canClose()
	usb1.closeSerial()
	
