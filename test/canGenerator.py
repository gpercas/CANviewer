from ..usbTinLib import *
import time

usb1=USBTin('COM5','BAUD_125K','Normal')
usb1.canOpenChannel()

for i in range(100):
    usb1.canWrite('131',4,['12','65','77','AA'],0x0002)
    time.sleep(0.01)

usb1.canClose()
    

