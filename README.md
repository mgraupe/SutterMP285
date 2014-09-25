Sutter Instrument MP-285
========================

A python class for communicating with the Sutter Instrument MP-285 Motorized Micromanipulator. 

`sutterMP285` implements a class for communicating with a Sutter MP-285 to control the manipulators. The MP-285   must be connected with a 9-pin serial port cable. 

This class uses the python `serial` package which allows for communication with serial devices through `write` and `read`. The communication properties (BaudRate, Terminator, etc.) are set when invoking the serial object with `serial.Serial(...)`. For the MP-285: baud rate to 9600, 8 data bits, no parity, 1 stop bit (see 'COMPUTER INTERFAC1.pdf' manual). 

##Requires
The following python packages are required by the class. 

* serial
* struct
* numpy
* sys
* time

##Methods
  Create the object. The object is opened with `serial.Serial(...)`.

    * sutter = sutterMP285()

  Various functions from the manual are implemented :

    * getPosition()
		Reads out the current postion of the three axes. 
    * gotoPosition(position)
		Moves the three axes to specified location.
		position ... is the absolute target position
    * setVelocity(velocity,vScaleFactor)
		This function changes the velocity of the sutter motions
		velocity ... move velocity
		vScaleFactor ... resolution, 0=10, 1=50 uSteps/step
    * updatePanel()
		Causes the Sutter to display the XYZ info on the front panel.
    * setOrigin()
		Sets the origin of the coordinate system to the current position.
    * sendReset()
		Reset controller. 
    * getStatus()
		Queries the status of the controller. 

Futher functions can be implemented from the manual following the structure of the existing class functions. 

##Properties

* `verbose` - The level of messages displayed (0 or 1). 
* `timeOut` - The amount of time within which a move has to be accomplished, otherwise interruption with error. 

##Example session:

```python
>> from sutterMP285_1 import *
>> sutter = sutterMP285()
   Serial<id=0x4548370, open=True>(port='COM1', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=30, xonxoff=False, rtscts=False, dsrdtr=False)
   sutterMP285: get status info
   (64, 0, 2, 4, 7, 0, 99, 0, 99, 0, 20, 0, 136, 19, 1, 120, 112, 23, 16, 39, 80, 0, 0, 0, 25, 0, 4, 0, 200, 0, 84, 1)
   step_mul (usteps/um): 25
   xspeed" [velocity] (usteps/sec): 200
   velocity scale factor (usteps/step): 10
   sutterMP285 ready
>> pos = sutter.getPosition()
   sutterMP285 : Stage position
   X: 3258.64 um
   Y: 5561.32 um
   Z: 12482.5 um
>> posnew = (pos[0]+10.,pos[1]+10.,pos[2]+10.)
>> sutter.gotoPosition(posnew)
   sutterMP285: Sutter move completed in (0.24 sec)
>> status = sutter.getStatus()
   sutterMP285: get status info
   (64, 0, 2, 4, 7, 0, 99, 0, 99, 0, 20, 0, 136, 19, 1, 120, 112, 23, 16, 39, 80, 0, 0, 0, 25, 0, 4, 0, 200, 0, 84, 1)
   step_mul (usteps/um): 25
   xspeed" [velocity] (usteps/sec): 200
   velocity scale factor (usteps/step): 10
>> del sutter
```


