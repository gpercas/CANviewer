
1.2. Methods related with CAN bus
=====================================

The following methods are related with the CAN bus and its interaction 
with the USBtin - considerating each device as a node of the bus. The methods
comprise the communication User <---> USBtin <---> CAN bus.

Methods
-------

.. module:: usbTinLib
	:noindex:
	
.. automethod:: USBTin.canOpenChannel
	
.. automethod:: USBTin.canClose
	
.. automethod:: USBTin.canSetBitrate

	.. warning::
	
		If there were multiple nodes, bitrate must be the same in every one.
		Otherwise a CAN Error could be raised and collapse the bus CAN.
	
.. automethod:: USBTin.canWrite
	
	.. note::
	
		1) Be careful! If the msgId is not inside the interval Standard ID or Extended ID Message, the method will return an error.
		Moreover check that CAN channel communication is opened before sending any message.
		
		2) If RTR message mask is not defined explicitly, the message will be active (with data bytes).
		
		3) If the message is RTR, messageList should be an empty list. Otherwise it prints an error.
		
	.. warning::
		
		Be careful! The msgId should be inside the interval Standard ID or Extended ID Message. Method will not raise any error as the USBtin adapts
		to this situations assigning an arbitrary value to the problematic byte of the identifier. 
		
		
	
.. automethod:: USBTin.canReadMessage