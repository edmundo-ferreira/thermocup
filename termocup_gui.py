from PyQt4 import QtCore, QtGui
import sys
import datetime
import random
import RPIO
import logging
import time
import serial

logging.basicConfig(filename='/home/pi/Desktop/thermocup/debug.log',filemode='w',format="%(levelname)s|%(asctime)-15s|%(message)s",level=logging.WARNING)


title='TermoCup 2013'
title_style='QLabel { font-size: 60pt; color:gray;}'
timer_style='QLabel {font-size:40pt; color:red;}'
rfid_style='QLabel {font-size:16pt; color:blue;}'
table_header_style='QHeaderView {font-size: 13pt;  background-color:gray;}'
table_item_style='QTreeWidget, QTreeView{font-size:12pt; color:black}'

RPIO.wait_for_interrupts(threaded=True)
RPIO.setwarnings(False)
	


gpio_b_list=[4]
gpio_e_list=[25]
class MainGui(QtGui.QWidget):
	def __init__(self,parent=None):
		QtGui.QWidget.__init__(self,parent)
		screen = QtGui.QDesktopWidget().screenGeometry() #get screen siz		
		
		#list of reader threads	
		self.reader_list=list()
		for i in range(0,1):
			self.reader_list.append(SerialReader(self,'/dev/ttyACM%s'%i))

		#list of track classes
		self.track_list=list()
		for i in range(0,1):
			self.track_list.append(Track(self,gpio_b_list[i],gpio_e_list[i],screen.width()/2-700+i*300))
		
  
		#title label
		self.title= QtGui.QLabel(title, self)
		self.title.setStyleSheet(title_style)
		self.title.setFixedWidth(700)
		self.title.setAlignment(QtCore.Qt.AlignRight)
		self.title.move(screen.width()/2-350,30)

		##ist_logo
		#ist_logo = QtGui.QLabel(self)
		#ist_logo.setPixmap( QtGui.QPixmap("ist_logo.png").scaled(280,150, QtCore.Qt.KeepAspectRatio))
		#ist_logo.move(30,30)
	 
 		##cienciaviva_logo
		#cienciaviva_logo= QtGui.QLabel(self)
		#cienciaviva_logo.setPixmap( QtGui.QPixmap("cienciaviva_logo.tif").scaled(200,160, QtCore.Qt.KeepAspectRatio))
		#cienciaviva_logo.move(screen.width()-250,30)

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
	  
            ##self.setStyleSheet("QWidget { background-color:white }") #set background
		#self.showFullScreen() #show fullscreen
		self.show()

	#edit the table
	def edit_rank_tree(self,item, index):
		print index
		if not (index==0 or index==1):
			item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)           
			self.rank_tree.editItem(item, index)       
			item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) 

	#close safeguard
	def closeEvent(self, event):
		reply = QtGui.QMessageBox.question(self,'Message',"Are you sure to quit?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			#closing serial thread list	
			for thread in self.reader_list:	
				thread.terminate()
			RPIO.stop_waiting_for_interrupts()
			RPIO.cleanup()
			event.accept()
	    	else:
			event.ignore()     



############################  TRACK CLASS ####################################
class Track():
	def __init__(self,gui_data,gpio_b,gpio_e,pos_x):
		self.gui_data=gui_data	
		self.gpio_b=gpio_b
		self.gpio_e=gpio_e
		self.tb=None
		#timer control flags 
		self.timer_running=False
		self.timer_enable=False
		self.rfid_enable=True
		#timer clock
		self.timer_clk= QtCore.QTimer()
		self.timer_clk.timeout.connect(self.setTimerClk)
	
		#rfid_clocks
		self.rfid_clk= QtCore.QTimer()
		self.rfid_clk.timeout.connect(self.clearRFID)
	  
		#timer label		
		self.timer_label=QtGui.QLabel('0:0000',self.gui_data)
		self.timer_label.setStyleSheet(timer_style)
		self.timer_label.setFixedWidth(300)
		self.timer_label.setAlignment(QtCore.Qt.AlignRight)
		self.timer_label.move(pos_x,220)
		#rfid label
		self.rfid_label=QtGui.QLabel('',self.gui_data)
		self.rfid_label.setStyleSheet(rfid_style)
		self.rfid_label.setFixedWidth(300)
		self.rfid_label.setAlignment(QtCore.Qt.AlignRight)
		self.rfid_label.move(pos_x,300)
	
	#get ellapsed time     
	def setTimerClk(self):
		t_lap= datetime.datetime.now()-self.t_0
		self.timer_label.setText("%d:%04d"%(t_lap.seconds,t_lap.microseconds/100))


	def startClk(self,gpio,val):
		print gpio
		if self.timer_running==False and self.timer_enable==True:
			self.t_0=datetime.datetime.now()
			self.timer_clk.start(1)
			RPIO.del_interrupt_callback(self.gpio_b)
			RPIO.add_interrupt_callback(self.gpio_e,self.stopClk,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=self.tb)
			self.rfid_clk.stop()
			self.timer_running=True
			self.rfid_enable=False
			self.gui_data.update()

	def stopClk(self,gpio,val):
		print gpio
		if self.timer_running==True:
			self.timer_clk.stop()
			RPIO.del_interrupt_callback(self.gpio_e)
			self.gui_data.update()	
			self.rfid_enable=True
			self.timer_enable=False
			self.timer_running=False
			time.sleep(6)
			self.rfid_label.setText('')
			self.timer_label.setText('0:0000')
	

	def setRFID(self,tag_id):
		if self.rfid_enable==True:
			self.rfid_clk.start(8000)
			self.rfid_label.setText("TagId=%s"%tag_id)
			self.rfid_enable=False
			self.timer_enable=True
			RPIO.add_interrupt_callback(self.gpio_b,self.startClk,edge='falling',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=self.tb)


	def clearRFID(self):
		RPIO.del_interrupt_callback(self.gpio_b)
		self.rfid_label.setText('')	
		self.rfid_enable=True
		self.timer_enable=False
		self.timer_running=False
		self.rfid_clk.stop()
##################################################################################





############################  SERIAL THREAD  ####################################
class SerialReader(QtCore.QThread):
	def __init__(self,gui_data,in_dev):
		QtCore.QThread.__init__(self)
		self.con_flag=False
		self.device_name=in_dev
		self.start()
		self.gui_data=gui_data

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
				in_channel, in_tag =self.ser.readline().strip('\n').split('#')	
				print in_channel,in_tag	
				self.gui_data.track_list[int(in_channel)-1].setRFID(in_tag)
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
##################################################################################


if __name__ == '__main__':
    	app = QtGui.QApplication(sys.argv)
    	MainGui()
    	app.exec_()
