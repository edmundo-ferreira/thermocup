# Robust programm to detect and read arduino rfid connections
# It enables auto connections and detects non-presence


import time 
import serial


con_flag=False
try:
	while True:
		while con_flag==False:
			try:
				ser=serial.Serial('/dev/ttyACM0',9600)
				print "connected"
				con_flag=True
			except serial.SerialException:
				#print "no connection"
				time.sleep(0.5)
		
		try:
			print ser.readline().strip('\n')
		except serial.SerialException:
			print "disconnected"
			ser.close()	
			con_flag=False	
except KeyboardInterrupt:
	if con_flag==True:
		ser.close()
		print "\nClosing Serial Port"
		print "Goodby"
	else:
		print "\nGoodby"
