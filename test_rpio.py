import RPIO
import logging
import time
import serial
try:
	ser=serial.Serial('/dev/ttyACM0',9600)
except:
	print "No Arduino Connected"


tb=None



RPIO.setwarnings(False)
logging.basicConfig(#filename='example.log',filemode='w',
		format="%(levelname)s| %(asctime)-15s | %(message)s",
		level=logging.WARNING)






def call_P1(gpio,val):
	logging.warning("P1-4")
        RPIO.del_interrupt_callback(4)
	RPIO.add_interrupt_callback(25,call_C1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C1(gpio_id,val):
	logging.warning("C1-25")
	RPIO.del_interrupt_callback(25)
	RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_P2(gpio,val):
	logging.warning("P2-17")
        RPIO.del_interrupt_callback(17)
	RPIO.add_interrupt_callback(18,call_C2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C2(gpio_id,val):
	logging.warning("C2-18")
	RPIO.del_interrupt_callback(18)
	RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_P3(gpio,val):
	logging.warning("P3-21")
        RPIO.del_interrupt_callback(21)
	RPIO.add_interrupt_callback(22,call_C3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C3(gpio_id,val):
	logging.warning("C3-22")
	RPIO.del_interrupt_callback(22)
	RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)



def call_P4(gpio,val):
	logging.warning("P4-7")
        RPIO.del_interrupt_callback(7)
	RPIO.add_interrupt_callback(8,call_C4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C4(gpio_id,val):
	logging.warning("C4-8")
	RPIO.del_interrupt_callback(8)
	RPIO.add_interrupt_callback(7,call_P4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)








RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)


RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)


RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)

RPIO.add_interrupt_callback(7,call_P4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)


RPIO.wait_for_interrupts(threaded=True)










try:
	while True:
		time.sleep(0.1)
		print "."	
		try:
			aux=ser.readline()
			print aux
		except:
			continue 
except:
	print "Execption Exiting..."



RPIO.stop_waiting_for_interrupts()
RPIO.cleanup()
print "RPIO clean"

