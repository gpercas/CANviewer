
1.3. Methods related to Bytes Processing
=========================================
The below methods are related with the procedural followed
when data arrives to the USBtin buffer. These data could come
either from the CAN bus or from itself - being an answer to a
user command.

These methods are transparent because the user does not need to
call them - they are always running through the FSM Thread.

The provided documentation could be used for future implementations
in other modules.


--------
Methods
--------

.. module:: usbTinLib
	:noindex:
	
.. automethod:: USBTin.FSM
	
.. automethod:: USBTin.processBytes

