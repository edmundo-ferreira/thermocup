import RPIO
import time

#debounce time varaible (None -> XXX miliseconds typical between 10 and 200)
tb=None

#eliminating warnings
RPIO.setwarnings(False)


def call_P1(gpio,val):
	print "P1-4"
        RPIO.del_interrupt_callback(4)
	RPIO.add_interrupt_callback(25,call_C1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C1(gpio_id,val):
	print "C1-25"
	RPIO.del_interrupt_callback(25)
	RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_P2(gpio,val):
	print "P2-17"
        RPIO.del_interrupt_callback(17)
	RPIO.add_interrupt_callback(18,call_C2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C2(gpio_id,val):
	print "C2-18"
	RPIO.del_interrupt_callback(18)
	RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_P3(gpio,val):
	print "P3-21"
        RPIO.del_interrupt_callback(21)
	RPIO.add_interrupt_callback(22,call_C3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C3(gpio_id,val):
	print "C3-22"
	RPIO.del_interrupt_callback(22)
	RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)



def call_P4(gpio,val):
	print "P4-7"
        RPIO.del_interrupt_callback(7)
	RPIO.add_interrupt_callback(8,call_C4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)


def call_C4(gpio_id,val):
	print "C4-8"
	RPIO.del_interrupt_callback(8)
	RPIO.add_interrupt_callback(7,call_P4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)








RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)


RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)


RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)

RPIO.add_interrupt_callback(7,call_P4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=100)


RPIO.wait_for_interrupts(threaded=True)
print "Ready... Let's play the piano..."


try:
	while True:
		time.sleep(0.1)
except KeyboardInterrupt:
	RPIO.stop_waiting_for_interrupts()
	RPIO.cleanup()
	print "FUCKING ERROR ON EXIT..."

