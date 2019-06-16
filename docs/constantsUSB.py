"""USBTin Constants"""
#USBTin Responses
CR='\x0D' 			#Carriage Return (\r)
LF='\x0A'			#Line Feed (\n)
usb_ERR='\x07'

bCR=b'\x0D'
bLF=b'\x0A'
busb_ERR=b'\x07'

#USBTinConstants

usb_READSTATUS='F'
usb_TIMESTAMPING='Z'
usb_VERSION_FW='v'
usb_VERSION_HW='V'
usb_MSG_RECEIVED='z'
can_CLOSE='C'
can_OPEN_LOOPBACK='l'
can_OPEN_LISTENONLY='L'
can_OPEN_NORMALMODE='O'
can_FILTER_MASK='m'
can_FILTER_CODE='M'
can_SETBITRATE='S'

can_NORMALMODE=1
can_LOOPBACK=2
can_LISTENONLY=3

STATE_INI=0
STATE_MSG=1
STATE_RPS=2

CHR_r='r'
CHR_cR='R'
CHR_t='t'
CHR_cT='T'

canERR_OK=0
canERR_KO=-1
canERR_NOMSG=-2
canERR_NORPS=-2
canERR_PARAM=-1

canMSG_RTR              =0x0001      # Message is a remote request
canMSG_STD              =0x0002      # Message has a standard ID
canMSG_EXT              =0x0004 


BAUD={"BAUD_10K":0, "BAUD_20K":1, "BAUD_50K":2, "BAUD_100K":3, "BAUD_125K":4, 
"BAUD_250K":5, "BAUD_500K":6, "BAUD_800K":7, "BAUD_1M":8}

canBITRATE={"canBITRATE_10K":0,"canBITRATE_20K":1,"canBITRATE_50K":2,"canBITRATE_100K":3,"canBITRATE_125K":4,
"canBITRATE_250K":5,"canBITRATE_500K":6,"canBITRATE_800K":7,"canBITRATE_1M":8}