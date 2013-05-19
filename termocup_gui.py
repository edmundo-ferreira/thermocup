from PyQt4 import QtCore, QtGui
import sys
import datetime
import random
import RPIO
import logging
import time
import serial


tb=None


RPIO.setwarnings(False)
logging.basicConfig(filename='/home/pi/Desktop/thermocup/debug.log',filemode='w',format="%(levelname)s| %(asctime)-15s | %(message)s",level=logging.WARNING)


title='TermoCup 2013'
title_style='QLabel { font-size: 60pt; color:gray;}'
timer_style='QLabel {font-size:40pt; color:red;}'
rfid_style='QLabel {font-size:16pt; color:blue;}'
table_header_style='QHeaderView {font-size: 13pt;  background-color:gray;}'
table_item_style='QTreeWidget, QTreeView{font-size:12pt; color:black}'


def call_P1(gpio,val):
       	ex.start_fcn1() 
	ex.update()

def call_C1(gpio_id,val):
       	ex.stop_fcn1() 
	ex.update()

def call_P2(gpio,val):
	ex.start_fcn2() 
	RPIO.del_interrupt_callback(17)
	RPIO.add_interrupt_callback(18,call_C2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C2(gpio_id,val):
	ex.stop_fcn2() 
	RPIO.del_interrupt_callback(18)
	RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_P3(gpio,val):
	ex.start_fcn3() 
	RPIO.del_interrupt_callback(21)
	RPIO.add_interrupt_callback(22,call_C3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C3(gpio_id,val):
	ex.stop_fcn3() 
	RPIO.del_interrupt_callback(22)
	RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()


def call_P4(gpio,val):
	ex.start_fcn4() 
	RPIO.del_interrupt_callback(7)
	RPIO.add_interrupt_callback(8,call_C4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C4(gpio_id,val):
	ex.stop_fcn4() 
	RPIO.del_interrupt_callback(8)
	RPIO.add_interrupt_callback(7,call_P4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()



RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
RPIO.add_interrupt_callback(7,call_P4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
RPIO.wait_for_interrupts(threaded=True)



class Example(QtGui.QWidget):
    def __init__(self,parent=None):
	QtGui.QWidget.__init__(self,parent)

        screen = QtGui.QDesktopWidget().screenGeometry() #get screen size

	self.reader_thd0=SerialReader('/dev/ttyACM0')
        self.reader_thd0.start() 

	self.reader_thd1=SerialReader('/dev/ttyACM1')
        self.reader_thd1.start() 

        QtCore.QObject.connect(self.reader_thd0,QtCore.SIGNAL("rfid_detect(QString)"), self.rfid_detect)       


        #clock1 thread
        self.clock1 = QtCore.QTimer()
        self.clock1.timeout.connect(self.getElapTime1)
        #clock1 thread
        self.clock2 = QtCore.QTimer()
        self.clock2.timeout.connect(self.getElapTime2)
	#clock1 thread
        self.clock3 = QtCore.QTimer()
        self.clock3.timeout.connect(self.getElapTime3)
	#clock1 thread
        self.clock4 = QtCore.QTimer()
        self.clock4.timeout.connect(self.getElapTime4)


	#rfid_clocks
	self.rfid1_clk= QtCore.QTimer()
        self.rfid1_clk.timeout.connect(self.clear_rfid1)
	


	self.timers=list()
	for i in range(0,1):
		self.timers.append(QtGui.QLabel('0:0000',self))
        	self.timers[i].setStyleSheet(timer_style)
        	self.timers[i].setFixedWidth(300)
        	self.timers[i].setAlignment(QtCore.Qt.AlignRight)
        	self.timers[i].move(screen.width()/2-700+i*300,220)



        self.timer1=QtGui.QLabel('0:0000',self)
        self.timer1.setStyleSheet(timer_style)
        self.timer1.setFixedWidth(300)
        self.timer1.setAlignment(QtCore.Qt.AlignRight)
        self.timer1.move(screen.width()/2-700,220)
       	#timer2 label
        self.timer2=QtGui.QLabel('0:0000',self)
        self.timer2.setStyleSheet(timer_style)
        self.timer2.setFixedWidth(300)
        self.timer2.setAlignment(QtCore.Qt.AlignRight)
        self.timer2.move(screen.width()/2-400,220)
       	#timer3 label
        self.timer3=QtGui.QLabel('0:0000',self)
        self.timer3.setStyleSheet(timer_style)
        self.timer3.setFixedWidth(300)
        self.timer3.setAlignment(QtCore.Qt.AlignRight)
        self.timer3.move(screen.width()/2-100,220)
        #timer4 label
        self.timer4=QtGui.QLabel('0:0000',self)
        self.timer4.setStyleSheet(timer_style)
        self.timer4.setFixedWidth(300)
        self.timer4.setAlignment(QtCore.Qt.AlignRight)
        self.timer4.move(screen.width()/2+200,220)
        
	#rfid1 label
        self.rfid1=QtGui.QLabel('',self)
        self.rfid1.setStyleSheet(rfid_style)
        self.rfid1.setFixedWidth(300)
        self.rfid1.setAlignment(QtCore.Qt.AlignRight)
        self.rfid1.move(screen.width()/2-700,300)
	#rfid1 label
        self.rfid2=QtGui.QLabel('',self)
        self.rfid2.setStyleSheet(rfid_style)
        self.rfid2.setFixedWidth(300)
        self.rfid2.setAlignment(QtCore.Qt.AlignRight)
        self.rfid2.move(screen.width()/2-400,300)


       	#timer control flags 
	self.timer1_running=False
        self.timer2_running=False
        self.timer3_running=False
        self.timer4_running=False

	self.timer1_enable=False
	self.timer2_enable=False

	self.rfid1_enable=True
	self.rfid2_enable=True


        #title label
        self.title= QtGui.QLabel(title, self)
        self.title.setStyleSheet(title_style)
        self.title.setFixedWidth(700)
        self.title.setAlignment(QtCore.Qt.AlignRight)
        self.title.move(screen.width()/2-350,30)

	#ist_log#o
	#ist_logo = QtGui.QLabel(self)
	#ist_logo.setPixmap( QtGui.QPixmap("ist_logo.png").scaled(280,150, QtCore.Qt.KeepAspectRatio))
	#ist_logo.move(30,30)
        
	 #cienciaviva_logo
	#cienciaviva_logo= QtGui.QLabel(self)
	#cienciaviva_logo.setPixmap( QtGui.QPixmap("cienciaviva_logo.tif").scaled(200,160, QtCore.Qt.KeepAspectRatio))
	#cienciaviva_logo.move(screen.width()-250,30)


        ##shortcut start
        #self.shortcut_start = QtGui.QShortcut(self)
        #self.shortcut_start.setKey("F9")
        #self.shortcut_start.activated.connect(self.start_fcn)
        
        ##shortcut stop
        #self.shortcut_stop = QtGui.QShortcut(self)
        #self.shortcut_stop.setKey("F10")
        #self.shortcut_stop.activated.connect(self.stop_fcn)

        #shortcut reset
#        self.shortcut_reset=QtGui.QShortcut(self)
        #self.shortcut_reset.setKey("F11")
        #self.shortcut_reset.activated.connect(self.reset_fcn)


        #ranking table
        self.rank_tree= QtGui.QTreeWidget(self)
        self.rank_tree. setHeaderLabels(['Ranking','Team Number','Time (s)','Classificacao (val)','Bonus (val)'])
        self.rank_tree.setFixedWidth(1000)
        self.rank_tree.setFixedHeight(600)
        self.rank_tree.move(screen.width()/2-500,400)
      
        self.rank_tree.setColumnWidth(0,200)
        self.rank_tree.header().setResizeMode(0,QtGui.QHeaderView.Fixed)
        self.rank_tree.setColumnWidth(1,200)
        self.rank_tree.header().setResizeMode(1,QtGui.QHeaderView.Fixed)
        self.rank_tree.setColumnWidth(2,200)
        self.rank_tree.header().setResizeMode(2,QtGui.QHeaderView.Fixed)
        self.rank_tree.setColumnWidth(3,200)
        self.rank_tree.header().setResizeMode(3,QtGui.QHeaderView.Fixed)
        #self.rank_tree.setColumnWidth(4,200)
        self.rank_tree.header().setResizeMode(4,QtGui.QHeaderView.Fixed)

        self.rank_tree.header().setDefaultAlignment(QtCore.Qt.AlignCenter) #alingment of header tags
        self.rank_tree.header().setStyleSheet(table_header_style)
        self.rank_tree.setStyleSheet(table_item_style)
        
        self.rank_tree.setSortingEnabled(True) 
        self.rank_tree.sortItems(0,QtCore.Qt.AscendingOrder)
        self.rank_tree.setAlternatingRowColors(True);
    
    
        nteam=range(1,151)
        random.shuffle(nteam)

        for i in range(1,151):
            aux=QtGui.QTreeWidgetItem(self.rank_tree)
            aux.setData(0,QtCore.Qt.DisplayRole, i)
            aux.setData(1,QtCore.Qt.DisplayRole, nteam[i-1])
            aux.setData(2,QtCore.Qt.DisplayRole, random.uniform(0,300))
            aux.setData(3,QtCore.Qt.DisplayRole, random.uniform(0,20))
            aux.setData(4,QtCore.Qt.DisplayRole, random.uniform(0,20))
            for j in range(5):
                aux.setTextAlignment(j,QtCore.Qt.AlignCenter)

  
        
        self.rank_tree.itemDoubleClicked.connect(self.edit_rank_tree)      
         
        #self.setStyleSheet("QWidget { background-color:white }") #set background
        self.showFullScreen() #show fullscreen
 
	
    def rfid_detect(self, tag_id):
	    if self.rfid1_enable==True:
		    self.rfid1_clk.start(8000) #give it 30 seconds
		    self.rfid1.setText("TagId=%s"%tag_id)
		    self.timer1_enable=True
		    self.rfid1_enable=False


    def clear_rfid1(self):
	self.rfid1_enable=True
	self.rfid1.setText('')
	self.rfid1_enable=True
	self.timer1_enable=False

	# edit the table
    def edit_rank_tree(self,item, index):
        print index
        if not (index==0 or index==1):
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)           
            self.rank_tree.editItem(item, index)       
            item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)


    def getElapTime(self,clock_id,t0):
	self.timer[clock_id].setText("%d:%04d"%(elap_1.seconds,t0.microseconds/100))


    #get ellapsed time     
    def getElapTime1(self):
        elap_1= datetime.datetime.now()-self.t1_0
        self.timer1.setText("%d:%04d"%(elap_1.seconds,elap_1.microseconds/100))
    # start function
    def start_fcn1(self):
        if self.timer1_running==False and self.timer1_enable==True:
            self.clock1.start(1)
	    self.t1_0=datetime.datetime.now()
            RPIO.del_interrupt_callback(4)
	    RPIO.add_interrupt_callback(25,call_C1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	    self.rfid1_clk.stop()
            self.timer1_running=True
	    self.rfid1_enable=False
    #stop function
    def stop_fcn1(self):
        if self.timer1_running==True:
            self.clock1.stop()
            RPIO.del_interrupt_callback(25)
	    RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	    self.rfid1_enable=True
	    self.timer1_enable=False
	    self.timer1_running=False
	    time.sleep(4)
	    self.rfid1.setText('')
	    self.timer1.setText('0:0000')


	#get ellapsed time     
    def getElapTime2(self):
        elap_2= datetime.datetime.now()-self.t2_0
        self.timer2.setText("%d:%04d"%(elap_2.seconds,elap_2.microseconds/100))
    # start function
    def start_fcn2(self):
        if self.timer2_running==False:
            self.clock2.start(1)
            self.t2_0=datetime.datetime.now()
            self.timer2_running=True
    #stop function
    def stop_fcn2(self):
        if self.timer2_running==True:
            self.clock2.stop()
            self.timer2_running=False
    #get ellapsed time     
    def getElapTime3(self):
        elap_3= datetime.datetime.now()-self.t3_0
        self.timer3.setText("%d:%04d"%(elap_3.seconds,elap_3.microseconds/100))
    # start function
    def start_fcn3(self):
        if self.timer3_running==False:
            self.clock3.start(1)
            self.t3_0=datetime.datetime.now()
            self.timer3_running=True
    #stop function
    def stop_fcn3(self):
        if self.timer3_running==True:
            self.clock3.stop()
            self.timer3_running=False
       

    #get ellapsed time     
    def getElapTime4(self):
        elap_4= datetime.datetime.now()-self.t4_0
        self.timer4.setText("%d:%04d"%(elap_4.seconds,elap_4.microseconds/100))
    # start function
    def start_fcn4(self):
        if self.timer4_running==False:
            self.clock4.start(1)
            self.t4_0=datetime.datetime.now()
            self.timer4_running=True
    #stop function
    def stop_fcn4(self):
        if self.timer4_running==True:
            self.clock4.stop()
            self.timer4_running=False
 



    #request password
    def req_password(self,event):
        print "mete a pass porco"
        #pop=QtGui.QMessageBox.alert(self,''


    #close safeguard
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes |  QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
	if reply == QtGui.QMessageBox.Yes:
		self.reader_thd0.terminate()
		self.reader_thd1.terminate()
		RPIO.stop_waiting_for_interrupts()
		RPIO.stop_waiting_for_interrupts()
		RPIO.cleanup()
		event.accept()
        else:
		event.ignore()     


############################  SERIAL THREAD  ##########################
class SerialReader(QtCore.QThread):
    def __init__(self,in_dev):
	QtCore.QThread.__init__(self)
        self.con_flag=False
	self.device_name=in_dev	

    def run(self):
	while True:
		while self.con_flag==False:
			try:
				self.ser=serial.Serial(self.device_name,9600)
				print "%s connected"%self.device_name
				self.con_flag=True
			except serial.SerialException:
				#print "no connection"
				time.sleep(0.5)
		try:
			merda=self.ser.readline().strip('\n')
			self.emit(QtCore.SIGNAL("rfid_detect(QString)"),merda)
			print merda
		except serial.SerialException:
			print "disconnected"
			self.ser.close()	
			self.con_flag=False	
	
    
    def terminate(self):
        try:
	    self.ser.close()
            QtCore.QThread.terminate(self)
            print "Stoping SerialRead Thread"    
        except:
            print "Unable to close SerialRead Thread"







if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    app.exec_()
