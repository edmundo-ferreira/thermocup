from PyQt4 import QtCore, QtGui
import sys
import datetime
import random
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
logging.basicConfig(filename='example.log',filemode='w',
		format="%(levelname)s| %(asctime)-15s | %(message)s",
		level=logging.WARNING)



title='TermoCup 2013'
title_style='QLabel { font-size: 60pt; color:gray;}'
timer_style='QLabel {font-size:40pt; color:red;}'
table_header_style='QHeaderView { font-size: 13pt; font-weight: bold; background-color:gray;}'
table_item_style='QTreeWidget, QTreeView{font-size:12pt; color:black}'



def call_P1(gpio,val):
	logging.warning("P1-4")
       	ex.start_fcn1() 
	RPIO.del_interrupt_callback(4)
	RPIO.add_interrupt_callback(25,call_C1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C1(gpio_id,val):
	logging.warning("C1-25")
       	ex.stop_fcn1() 
	RPIO.del_interrupt_callback(25)
	RPIO.add_interrupt_callback(4,call_P1,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_P2(gpio,val):
	logging.warning("P2-17")
	ex.start_fcn2() 
	RPIO.del_interrupt_callback(17)
	RPIO.add_interrupt_callback(18,call_C2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C2(gpio_id,val):
	logging.warning("C2-18")
	ex.stop_fcn2() 
	RPIO.del_interrupt_callback(18)
	RPIO.add_interrupt_callback(17,call_P2,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_P3(gpio,val):
	logging.warning("P3-21")
	ex.start_fcn3() 
	RPIO.del_interrupt_callback(21)
	RPIO.add_interrupt_callback(22,call_C3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C3(gpio_id,val):
	logging.warning("C3-22")
	ex.stop_fcn3() 
	RPIO.del_interrupt_callback(22)
	RPIO.add_interrupt_callback(21,call_P3,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()


def call_P4(gpio,val):
	logging.warning("P4-7")
	ex.start_fcn4() 
	RPIO.del_interrupt_callback(7)
	RPIO.add_interrupt_callback(8,call_C4,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=tb)
	ex.update()

def call_C4(gpio_id,val):
	logging.warning("C4-8")
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
    
    def __init__(self):
        super(Example, self).__init__() 
        self.initUI()
        
    def initUI(self):
        screen = QtGui.QDesktopWidget().screenGeometry() #get screen size

        #clock1 thread
        self.clock1 = QtCore.QTimer()
        self.clock1.timeout.connect(self.getElapTime1)

       #clock2 thread
	self.clock2 = QtCore.QTimer()
	self.clock2.timeout.connect(self.getelaptime2)

       #clock3 thread
	self.clock3 = QtCore.QTimer()
	self.clock3.timeout.connect(self.getelaptime3)

       #clock4 thread
	self.clock4 = QtCore.QTimer()
	self.clock4.timeout.connect(self.getelaptime4)


	#timer1 label
        self.timer1=QtGui.QLabel('0:0000',self)
        self.timer1.setStyleSheet(timer_style)
        self.timer1.setFixedWidth(300)
        self.timer1.setAlignment(QtCore.Qt.AlignRight)
        self.timer1.move(screen.width()/2-600,220)
        	#timer1 label
        self.timer2=QtGui.QLabel('0:0000',self)
        self.timer2.setStyleSheet(timer_style)
        self.timer2.setFixedWidth(300)
        self.timer2.setAlignment(QtCore.Qt.AlignRight)
        self.timer2.move(screen.width()/2-300,220)
        	#timer1 label
        self.timer3=QtGui.QLabel('0:0000',self)
        self.timer3.setStyleSheet(timer_style)
        self.timer3.setFixedWidth(300)
        self.timer3.setAlignment(QtCore.Qt.AlignRight)
        self.timer3.move(screen.width()/2+000,220)
        	#timer1 label
        self.timer3=QtGui.QLabel('0:0000',self)
        self.timer3.setStyleSheet(timer_style)
        self.timer3.setFixedWidth(300)
        self.timer3.setAlignment(QtCore.Qt.AlignRight)
        self.timer3.move(screen.width()/2+300,220)
        
        #title label
        self.title= QtGui.QLabel(title, self)
        self.title.setStyleSheet(title_style)
        self.title.setFixedWidth(700)
        self.title.setAlignment(QtCore.Qt.AlignRight)
        self.title.move(screen.width()/2-350,30)

        #ist_logo
        ist_logo = QtGui.QLabel(self)
        ist_logo.setPixmap( QtGui.QPixmap("ist_logo.png").scaled(280,150, QtCore.Qt.KeepAspectRatio))
        ist_logo.move(30,30)
        

        self.timer1_running=False
        self.timer2_running=False
        self.timer3_running=False
        self.timer4_running=False
        # #cienciaviva_logo
        # cienciaviva_logo= QtGui.QLabel(self)
        # cienciaviva_logo.setPixmap( QtGui.QPixmap("cienciaviva_logo.tif").scaled(200,160, QtCore.Qt.KeepAspectRatio))
        # cienciaviva_logo.move(screen.width()-250,30)



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
 
 
        
    # edit the table
    def edit_rank_tree(self,item, index):
        print index
        if not (index==0 or index==1):
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)           
            self.rank_tree.editItem(item, index)       
            item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)


    #get ellapsed time     
    def getElapTime1(self):
        elap_1= datetime.datetime.now()-self.t1_0
        self.timer1.setText("%d:%04d"%(elap_1.seconds,elap_1.microseconds))
 
    # start function
    def start_fcn1(self):
        if self.timer1_running==False:
             #starting the clock
            self.clock1.start(1)
            self.t1_0=datetime.datetime.now()
            self.timer1_running=True
        
    #stop function
    def stop_fcn1(self):
        if self.timer1_running==True:
            self.clock1.stop()
            self.timer1_running=False

     #get ellapsed time     
    def getelaptime2(self):
        elap_2= datetime.datetime.now()-self.t2_0
        self.timer2.settext("%d:%04d"%(elap_2.seconds,elap_2.microseconds))
        
            
    # start function
    def start_fcn2(self):
        if self.timer2_running==False:
             #starting the clock
            self.clock2.start(1)
            self.t2_0=datetime.datetime.now()
            self.timer2_running=True

    #stop function
    def stop_fcn2(self):
        if self.timer2_running==True:
            self.clock2.stop()
            self.timer2_running=False
 

      #get ellapsed time     
    def getelaptime3(self):
        elap_3= datetime.datetime.now()-self.t3_0
        self.timer3.settext("%d:%04d"%(elap_3.seconds,elap_3.microseconds))
        
            
    # start function
    def start_fcn3(self):
        if self.timer3_running==False:
             #starting the clock
            self.clock3.start(1)
            self.t3_0=datetime.datetime.now()
            self.timer3_running=True

    #stop function
    def stop_fcn3(self):
        if self.timer3_running==True:
            self.clock3.stop()
            self.timer3_running=False
        
        
     #get ellapsed time     
    def getelaptime4(self):
        elap_4= datetime.datetime.now()-self.t4_0
        self.timer4.settext("%d:%04d"%(elap_4.seconds,elap_4.microseconds))
        
            
    # start function
    def start_fcn4(self):
        if self.timer4_running==False:
             #starting the clock
            self.clock4.start(1)
            self.t4_0=datetime.datetime.now()
            self.timer4_running=true

    #stop function
    def stop_fcn4(self):
        if self.timer4_running==True:
            self.clock4.stop()
            self.timer4_running=false
 
       


    #request password
    def req_password(self,event):
        print "mete a pass porco"
        #pop=QtGui.QMessageBox.alert(self,''


    #close safeguard
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes |  QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        RPIO.stop_waiting_for_interrupts()
	RPIO.cleanup()

	if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()     





	


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    app.exec_()
