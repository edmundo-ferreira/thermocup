# Robust programm to detect and read arduino rfid connections
# It enables auto connections and detects non-presence
import time 
import serial
import csv

f=open('/home/pi/Desktop/thermocup/tag_lookup.txt','r')
f2=open('/home/pi/Desktop/thermocup/tag_lookup2.txt','w')
my_dic={}
csv_writer=csv.writer(f2)
csv_reader=csv.reader(f)


w_flag=False


for row in csv_reader:
	try:
		my_dic[row[0]]=row[1]
	except:
		print "fodeu"

print my_dic



if w_flag==True:
	card_number=87
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
				print "------------------------------------"
				print "Pass card: %d"%card_number
				tag_in=ser.readline().split('#')[1].strip('\r\n')
				my_dic[tag_in]=card_number
				card_number=card_number+1
			except serial.SerialException:
				print "disconnected"
				ser.close()	
				con_flag=False	
	except KeyboardInterrupt:
		if con_flag==True:
			ser.close()
		
	print "\nClosing Serial Port"
	
	
for item in my_dic:
	csv_writer.writerow([item, my_dic[item]])
	

f.close()
