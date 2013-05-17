import RPi.GPIO as GPIO
import time
import serial
try:
	ser=serial.Serial('/dev/ttyACM0',9600)
except:
	print "No Arduino Connected"


tb=300


#setting mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#setting up channels
GPIO.setup(4,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(17,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(18,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(21,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(22,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(25,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(7,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(8,GPIO.IN,pull_up_down=GPIO.PUD_UP)



def call_P1(channel):
	print "P1-4"
	GPIO.remove_event_detect(4)
	GPIO.add_event_detect(25,GPIO.FALLING,callback=call_C1,bouncetime=tb)

def call_C1(channel):
	print "C1-25"
	GPIO.remove_event_detect(25)
	GPIO.add_event_detect(4,GPIO.FALLING,callback=call_P1,bouncetime=tb)

def call_P2(channel):
	print "P2-17"
	GPIO.remove_event_detect(17)	
	GPIO.add_event_detect(18,GPIO.FALLING,callback=call_C2,bouncetime=tb)

def call_C2(channel):
	print "C2-18"
	GPIO.remove_event_detect(18)
	GPIO.add_event_detect(17,GPIO.FALLING,callback=call_P2,bouncetime=tb)

def call_P3(channel):
	print "P3-21"
	GPIO.remove_event_detect(21)
	GPIO.add_event_detect(22,GPIO.FALLING,callback=call_C3,bouncetime=tb)

def call_C3(channel):
	print "C3-22"
	GPIO.remove_event_detect(22)
	GPIO.add_event_detect(21,GPIO.FALLING,callback=call_P3,bouncetime=tb)

def call_P4(channel):
	print "P4-7"
	GPIO.remove_event_detect(7)
	GPIO.add_event_detect(8,GPIO.FALLING,callback=call_C4,bouncetime=tb)

def call_C4(channel):
	print "C4-8"
	GPIO.remove_event_detect(8)
	GPIO.add_event_detect(7,GPIO.FALLING,callback=call_P4,bouncetime=tb)




#apenas as partidas
GPIO.add_event_detect(4,GPIO.FALLING,callback=call_P1,bouncetime=tb) 
GPIO.add_event_detect(17,GPIO.FALLING,callback=call_P2,bouncetime=tb)
GPIO.add_event_detect(21,GPIO.FALLING,callback=call_P3,bouncetime=tb)
GPIO.add_event_detect(7,GPIO.FALLING,callback=call_P4,bouncetime=tb)


try:
	while True:
		time.sleep(1)
		print "."	
		try:
			aux=ser.readline()
			print aux
		except:
			continue 
except:
	print "Execption Exiting..."


GPIO.cleanup()
print "GPIO clean"

