# Robust programm to detect and read arduino rfid connections
# It enables auto connections and detects non-presence
import time 
import serial
import csv

f=open('tag_lookup.csv','wb')
my_dic={}


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
			print "Pass the RFID card:"
			tag_in=ser.readline().strip('\n').split('#')[1]
			print tag_in
			card_n=raw_input("Insert Team Number:")
			my_dic[tag_in]=card_n	
		except serial.SerialException:
			print "disconnected"
			ser.close()	
			con_flag=False	
except KeyboardInterrupt:
	if con_flag==True:
		ser.close()
	
	print "\nClosing Serial Port"



for tag in my_dic:
	print tag



