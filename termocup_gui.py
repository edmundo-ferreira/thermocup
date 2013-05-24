from PyQt4 import QtCore, QtGui
import sys
import datetime
import random
import RPIO
import logging
import time
import serial
import csv

f=open('/home/pi/Desktop/thermocup/tag_lookup.txt','r')
my_dic={}
csv_reader=csv.reader(f)

for row in csv_reader:
	try:
		my_dic[row[0]]=row[1]
	except:
		print "Error reading dictionary"
f.close()

data={}

logging.basicConfig(filename='/home/pi/Desktop/thermocup/debug.log',filemode='w',format="%(levelname)s|%(asctime)-15s|%(message)s",level=logging.WARNING)


title='TermoCup 2013'
title_style='QLabel { font-size: 60pt; color:gray;}'
timer_style='QLabel {font-size:40pt; color:red;}'
rfid_style='QLabel {font-size:25pt; color:blue;}'
table_header_style='QHeaderView {font-size: 13pt;  background-color:gray;}'
table_item_style='QTreeWidget, QTreeView{font-size:12pt; color:black}'

RPIO.wait_for_interrupts(threaded=True)
RPIO.setwarnings(False)
	
gpio_b_list=[4,0,17,22]
gpio_e_list=[25,1,18,23]


class MainGui(QtGui.QWidget):
	def __init__(self,parent=None):
		QtGui.QWidget.__init__(self,parent)
		screen = QtGui.QDesktopWidget().screenGeometry() #get screen siz		
		
		#list of reader threads	
		self.reader_list=list()
		self.reader_list.append(SerialReader(self,'/dev/ttyACM%s'%0))
		self.reader_list.append(SerialReader(self,'/dev/ttyACM%s'%1))
		self.reader_list.append(SerialReader(self,'/dev/ttyUSB%s'%0))

	
		#list of track classes
		self.track_list=list()
		for i in range(0,len(gpio_b_list)):
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
		self.tree_widget= QtGui.QTreeWidget(self)
		self.tree_widget. setHeaderLabels(['Ranking','Team Number','Time (s)'])
		self.tree_widget.setFixedWidth(800)
		self.tree_widget.setFixedHeight(500)
		self.tree_widget.move(screen.width()/2-400,400)
		self.tree_widget.setColumnWidth(0,200)
		self.tree_widget.header().setResizeMode(0,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(1,200)
		self.tree_widget.header().setResizeMode(1,QtGui.QHeaderView.Fixed)
		#self.tree_widget.setColumnWidth(2,200)
		self.tree_widget.header().setResizeMode(2,QtGui.QHeaderView.Fixed)
		
		self.tree_widget.header().setDefaultAlignment(QtCore.Qt.AlignCenter) #alingment of header tags
		self.tree_widget.header().setStyleSheet(table_header_style)
		self.tree_widget.setStyleSheet(table_item_style)
		self.tree_widget.setSortingEnabled(True) 
		self.tree_widget.sortItems(2,QtCore.Qt.AscendingOrder)

		self.tree_widget.setAlternatingRowColors(True);
		#self.tree_widget.itemDoubleClicked.connect(self.edit_tree_widget)      
	  
            #self.setStyleSheet("QWidget { background-color:white }") #set background
		self.showFullScreen() #show fullscreen

	#edit the table
	#def edit_tree_widget(self,item, index):
		#print index
		#if not (index==0 or index==1):
			#item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)           
			#self.tree_widget.editItem(item, index)       
		    #  item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled) 

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
		#timer control flags 
		self.timer_running=False
		self.timer_enable=False
		self.rfid_enable=True
		#timer clock
		self.timer_clk= QtCore.QTimer()
		self.timer_clk.timeout.connect(self.setTimerClk)
	
		#track clock
		self.track_clk= QtCore.QTimer()
		self.track_clk.timeout.connect(self.disableTrack)

		#timer label		
		self.timer_label=QtGui.QLabel('0:000',self.gui_data)
		self.timer_label.setStyleSheet(timer_style)
		self.timer_label.setFixedWidth(300)
		self.timer_label.setAlignment(QtCore.Qt.AlignRight)
		self.timer_label.move(pos_x,220)
		#rfid label
		self.rfid_label=QtGui.QLabel('',self.gui_data)
		self.rfid_label.setStyleSheet(rfid_style)
		self.rfid_label.setFixedWidth(300)
		self.rfid_label.setAlignment(QtCore.Qt.AlignCenter)
		self.rfid_label.move(pos_x+60,300)
	
	
	def enableTrack(self,tag_id):
		print tag_id
		if self.rfid_enable==True:
			self.tag_id=tag_id	
			self.track_clk.start(30000)
			self.rfid_label.setText("%s"%tag_id)
			self.rfid_enable=False
			self.timer_enable=True
			RPIO.add_interrupt_callback(self.gpio_b,self.startClk,edge='rising',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=None)

	def startClk(self,gpio,val):
		print gpio	
		if self.timer_running==False and self.timer_enable==True:
			RPIO.del_interrupt_callback(self.gpio_b)
			self.t_0=datetime.datetime.now()
			self.timer_clk.start(5)
			self.track_clk.stop()
			self.timer_running=True
			self.rfid_enable=False
			self.gui_data.update()
			RPIO.add_interrupt_callback(self.gpio_e,self.stopClk,edge='rising',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=None)

	def stopClk(self,gpio,val):
		print gpio	
		if self.timer_running==True: 
			RPIO.del_interrupt_callback(self.gpio_e)
			self.timer_clk.stop()
			self.track_clk.start(8000)			
		
	#get and set ellapsed time     
	def setTimerClk(self):
		self.t_lap= datetime.datetime.now()-self.t_0
		self.timer_label.setText("%d:%03d"%(self.t_lap.seconds,self.t_lap.microseconds/1000))

	#disable track and if timer was running kill's interrupt
	def disableTrack(self):
		self.track_clk.stop()
		if self.timer_running==False:
			  RPIO.del_interrupt_callback(self.gpio_b)
		self.rfid_label.setText('')	
		self.timer_label.setText('0:000')	
		self.rfid_enable=True
		self.timer_enable=False
		self.timer_running=False
##################################################################################




     # def sortTree(self):
		##FUCKED UP SIMULTANEOUS DATA ACCESS
		#self.float_timer=float("%d.%04d"%(self.t_lap.seconds,self.t_lap.microseconds/100))
		#if data.get(self.tag_id)==None or self.float_timer<data.get(self.tag_id):
			#data[self.tag_id]=self.float_timer
		#self.gui_data.tree_widget.clear() 
		#for row in data:
			#aux=QtGui.QTreeWidgetItem(self.gui_data.tree_widget)
			#aux.setData(0,QtCore.Qt.DisplayRole,1)
			#aux.setData(1,QtCore.Qt.DisplayRole,row)
			#aux.setData(2,QtCore.Qt.DisplayRole,data[row])






############################  SERIAL THREAD  ####################################
class SerialReader(QtCore.QThread):
	def __init__(self,gui_data,in_dev):
		QtCore.QThread.__init__(self)
		self.gui_data=gui_data
		self.con_flag=False
		self.device_name=in_dev
		self.start()

	def run(self):
		while True:
			while self.con_flag==False:
				try:
					self.ser=serial.Serial(self.device_name,9600)
					print "%s connected\n"%self.device_name
					self.con_flag=True
				except serial.SerialException:
					time.sleep(1)
			try:
				in_channel, in_tag =self.ser.readline().strip('\r\n').strip(' ').split('#')
				in_number=my_dic.get(in_tag)
				in_channel=int(in_channel)-1	
				if not in_number==None and in_channel<len(self.gui_data.track_list):
					#print in_channel,in_tag, in_number 
				 	self.gui_data.track_list[in_channel].enableTrack(in_number)
			except serial.SerialException:
				print "disconnected"
				self.ser.close()	
				self.con_flag=False	
	
	def terminate(self):
		try:
			self.ser.close()
			QtCore.QThread.terminate(self)
			print "Stoping SerialRead Thread %s"%self.device_name    
		except:
			print "Unable to close SerialRead Thread %s"%self.device_name
##################################################################################


if __name__ == '__main__':
    	app = QtGui.QApplication(sys.argv)
    	MainGui()
    	app.exec_()
