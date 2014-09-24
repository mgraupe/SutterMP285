# sutterMP285 : A python class for using the Sutter MP-285 positioner
# 
# SUTTERMP285 implements a class for working with a Sutter MP-285
#   micro-positioner. The Sutter must be connected with a Serial
#   cable. 
#
# This class uses the python "serial" package which allows for 
#   with serial devices through 'write' and 'read'. 
#   The communication properties (BaudRate, Terminator, etc.) are 
#   set when invoking the serial object with serial.Serial(..) (l105, 
#   see Sutter Reference manual p23).
#
# Methods:
#   Create the object. The object is opened with serial.Serial and the connection
#     is tested to verify that the Sutter is responding.
#       obj = sutterMP285()
#
#   Update the position display on the instrument panel (VFD)
#       updatePanel()
#
#   Get the status information (step multiplier, velocity, resolution)
#       [stepMult, currentVelocity, vScaleFactor] = getStatus()
#
#   Get the current absolute position in um
#       xyz_um = getPosition()
#
#   Set the move velocity in steps/sec. vScaleFactor = 10|50 (default 10).
#       setVelocity(velocity, vScaleFactor)
#
#   Move to a specified position in um [x y z]. Returns the elapsed time
#     for the move (command sent and acknowledged) in seconds.
#       moveTime = gotoPosition(xyz)
#
#   Set the current position to be the new origin (0,0,0)
#       setOrigin()
#
#   Reset the instrument
#       sendReset()
#
#   Close the connetion 
#       __del__()
#
# Properties:
#   verbose - The level of messages displayed (0 or 1). Default 1.
#
#
# Example:
#
# >> import serial
# >> from sutterMP285_1 import *
# >> sutter = sutterMP285()
#   Serial<id=0x4548370, open=True>(port='COM1', baudrate=9600, bytesize=8, parity='N', stopbits=1, timeout=30, xonxoff=False, rtscts=False, dsrdtr=False)
#   sutterMP285: get status info
#   (64, 0, 2, 4, 7, 0, 99, 0, 99, 0, 20, 0, 136, 19, 1, 120, 112, 23, 16, 39, 80, 0, 0, 0, 25, 0, 4, 0, 200, 0, 84, 1)
#   step_mul (usteps/um): 25
#   xspeed" [velocity] (usteps/sec): 200
#   velocity scale factor (usteps/step): 10
#   sutterMP285 ready
# >> pos = sutter.getPosition()
#   sutterMP285 : Stage position
#   X: 3258.64 um
#   Y: 5561.32 um
#   Z: 12482.5 um
# >> posnew = (pos[0]+10.,pos[1]+10.,pos[2]+10.)
# >> sutter.gotoPosition(posnew)
#   sutterMP285: Sutter move completed in (0.24 sec)
# >> status = sutter.getStatus()
#   sutterMP285: get status info
#   (64, 0, 2, 4, 7, 0, 99, 0, 99, 0, 20, 0, 136, 19, 1, 120, 112, 23, 16, 39, 80, 0, 0, 0, 25, 0, 4, 0, 200, 0, 84, 1)
#   step_mul (usteps/um): 25
#   xspeed" [velocity] (usteps/sec): 200
#   velocity scale factor (usteps/step): 10
# >> del sutter
#
#

import serial
import struct
import time 
import sys
from numpy import * 



class sutterMP285 :
	'Class which allows interaction with the Sutter Manipulator 285'
	def __init__(self):
		self.verbose = 1. # level of messages
		self.timeOut = 30 # timeout in sec
		# initialize serial connection to controller
		try:
			self.ser = serial.Serial(port='COM1',baudrate=9600,bytesize=serial.EIGHTBITS,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,timeout=self.timeOut)
			self.connected = 1
			if self.verbose:
			  print self.ser
		except serial.SerialException:
			print 'No connection to Sutter MP-285 could be established!'
			sys.exit(1)
		
		# set move velocity to 200
		self.setVelocity(200,10)
		self.updatePanel() # update controller panel
		(stepM,currentV,vScaleF)= self.getStatus()
		if currentV == 200:
			print 'sutterMP285 ready'
		else:
			print 'sutterMP285: WARNING Sutter did not respond at startup.'
	# destructor
	def __del__(self):
		self.ser.close()
		if self.verbose : 
			print 'Connection to Sutter MP-285 closed'
		
		
	def getPosition(self):
		# send commend to get position
		self.ser.write('c\r')
		# read position from controller
		xyzb = self.ser.read(13)
		# convert bytes into 'signed long' numbers
		xyz_um = array(struct.unpack('lll', xyzb[:12]))/self.stepMult
		
		if self.verbose:
			print 'sutterMP285 : Stage position '
			print 'X: %g um \n Y: %g um\n Z: %g um' % (xyz_um[0],xyz_um[1],xyz_um[2])
		
		return xyz_um
	
	def gotoPosition(self,pos):
		if len(pos) != 3:
			print 'Length of position argument has to be three'
			sys.exit(1)
		xyzb = struct.pack('lll',int(pos[0]*self.stepMult),int(pos[1]*self.stepMult),int(pos[2]*self.stepMult)) # convert integer values into bytes
		startt = time.time() # start timer
		self.ser.write('m'+xyzb+'\r') # send position to controller; add the "m" and the CR to create the move command
		cr = []
		cr = self.ser.read(1) # read carriage return and ignore
		endt = time.time() # stop timer
		if len(cr)== 0:
			print 'Sutter did not finish moving before timeout (%d sec).' % self.timeOut
		else:
			print 'sutterMP285: Sutter move completed in (%.2f sec)' % (endt-startt)
	# this function changes the velocity of the sutter motions
	def setVelocity(self,Vel,vScalF=10):
		# Change velocity command 'V'xxCR where xx= unsigned short (16bit) int velocity
        	# set by bits 14 to 0, and bit 15 indicates ustep resolution  0=10, 1=50 uSteps/step
        	# V is ascii 86
        	# convert velocity into unsigned short - 2-byte - integeter
        	velb = struct.pack('H',int(Vel))
        	# change last bit of 2nd byte to 1 for ustep resolution = 50
        	if vScalF == 50:
			velb2 = double(struct.unpack('B',velb[1])) + 128
			velb = velb[0] + struct.pack('B',velb2)
		self.ser.write('V'+velb+'\r')
		self.ser.read(1)
	# Update Panel
	# causes the Sutter to display the XYZ info on the front panel
	def updatePanel(self):
		self.ser.write('n\r') #Sutter replies with a CR
		self.ser.read(1) # read and ignore the carriage return
	
	## Set Origin
	# sets the origin of the coordinate system to the current position
	def setOrigin(self):
		self.ser.write('o\r') # Sutter replies with a CR
		self.ser.read(1) # read and ignor the carrage return
	 # Reset controller
	def sendReset(self):
		 self.ser.write('r\r') # Sutter does not reply
	
	def getStatus(self):
		if self.verbose : 
			print 'sutterMP285: get status info'
		self.ser.write('s\r') # send status command
		rrr = self.ser.read(32) # read return of 32 bytes without carriage return
		self.ser.read(1) # read and ignore the carriage return
		rrr
		statusbytes = struct.unpack(32*'B',rrr)
		print statusbytes
		# the value of STEP_MUL ("Multiplier yields msteps/nm") is at bytes 25 & 26
		self.stepMult = double(statusbytes[25])*256 + double(statusbytes[24])

		# the value of "XSPEED"  and scale factor is at bytes 29 & 30
		if statusbytes[29] > 127:
			self.vScaleFactor = 50
		else:
			self.vScaleFactor = 10
		#print double(127 & statusbytes[29])*256
		#print double(statusbytes[28]), statusbytes[28]
		#print double(statusbytes[29]), statusbytes[29]
		self.currentVelocity = double(127 & statusbytes[29])*256+double(statusbytes[28])
		#vScaleFactor = struct.unpack('lll', rrr[30:31])
		if self.verbose:
			print 'step_mul (usteps/um): %g' % self.stepMult
			print 'xspeed" [velocity] (usteps/sec): %g' % self.currentVelocity
			print 'velocity scale factor (usteps/step): %g' % self.vScaleFactor
		#
		return (self.stepMult,self.currentVelocity,self.vScaleFactor)


	