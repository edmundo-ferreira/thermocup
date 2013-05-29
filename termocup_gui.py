from PyQt4 import QtCore, QtGui
import sys
import datetime
import random
import RPIO
import logging
import time
import serial
import csv

fdic=open('/home/pi/Desktop/thermocup/tag_lookup.txt','r')
my_dic={}
csv_reader=csv.reader(fdic)
for row in csv_reader:
	try:
		my_dic[row[0]]=row[1]
	except:
		print "Error reading dictionary"
fdic.close()

logging.basicConfig(filename='/home/pi/Desktop/thermocup/debug.log',filemode='w',format="%(levelname)s|%(asctime)-15s|%(message)s",level=logging.WARNING)

title='TermoCup 2013'
title_style='QLabel { font-size: 60pt; color:gray;}'
timer_style='QLabel {font-size:40pt; color:red;}'
rfid_style='QLabel {font-size:25pt; color:blue;}'
table_header_style='QHeaderView {font-size: 13pt;  background-color:gray;}'
table_item_style='QTreeWidget, QTreeView{font-size:12pt; color:black}'

RPIO.wait_for_interrupts(threaded=True)
RPIO.setwarnings(False)
	
gpio_b_list=[4,17,22,9]
gpio_e_list=[14,18,23,25]


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
		self.tree_widget. setHeaderLabels(['Ranking','Team Number','Time (s)','Del'])
		self.tree_widget.setFixedWidth(800)
		self.tree_widget.setFixedHeight(500)
		self.tree_widget.move(screen.width()/2-400,400)
		self.tree_widget.setColumnWidth(0,200)
		self.tree_widget.header().setResizeMode(0,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(1,200)
		self.tree_widget.header().setResizeMode(1,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(2,350)
		self.tree_widget.header().setResizeMode(2,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(3,10)
		self.tree_widget.header().setResizeMode(3,QtGui.QHeaderView.Fixed)
		
		self.tree_widget.header().setDefaultAlignment(QtCore.Qt.AlignCenter) #alingment of header tags
		self.tree_widget.header().setStyleSheet(table_header_style)
		self.tree_widget.setStyleSheet(table_item_style)
					
		#self.tree_widget.setSortingEnabled(True) 
		#self.tree_widget.sortItems(2,QtCore.Qt.AscendingOrder)

		self.tree_widget.setAlternatingRowColors(True);
		
		
		fdata=open('/home/pi/Desktop/thermocup/data/temp.txt','r')
     		for row in fdata:
			aux=row.strip('\n').split(',')
			if not aux[0]=='':	
				new_item=QtGui.QTreeWidgetItem(self.tree_widget)
				new_item.setData(0,QtCore.Qt.DisplayRole,int(aux[0]))
				new_item.setData(1,QtCore.Qt.DisplayRole,int(aux[1]))
				new_item.setData(2,QtCore.Qt.DisplayRole,float(aux[2]))
				new_item.setTextAlignment(0,4)
				new_item.setTextAlignment(1,4)
				new_item.setTextAlignment(2,4)
				new_item.setCheckState(3,QtCore.Qt.Unchecked)
			else:
				new_sub_item=QtGui.QTreeWidgetItem(new_item)
				new_sub_item.setData(1,QtCore.Qt.DisplayRole,int(aux[1]))
				new_sub_item.setData(2,QtCore.Qt.DisplayRole,float(aux[2]))
				new_sub_item.setTextAlignment(0,4)
				new_sub_item.setTextAlignment(1,4)
				new_sub_item.setTextAlignment(2,4)
				new_sub_item.setCheckState(3,QtCore.Qt.Unchecked)

		fdata.close()
		#self.tree_widget.itemDoubleClicked.connect(self.edit_tree_widget)      
	 	self.tree_widget.itemChanged.connect(self.clikedDel) 
            #self.setStyleSheet("QWidget { background-color:white }") #set background
		self.showFullScreen() #show fullscreen

	def clikedDel(self,item,column):
		reply = QtGui.QMessageBox.question(self,'Message',"Are you sure you want to delete?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			index=self.tree_widget.indexOfTopLevelItem(item)
			if index==-1:
				item.parent().removeChild(item)
		    	else:
				self.tree_widget.takeTopLevelItem(index)
	    	else:
			item.setCheckState(3,QtCore.Qt.Unchecked)
			return

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
			self.track_clk.start(10000)
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
			self.timer_enable=False
			self.track_clk.start(5000)			
		
	#get and set ellapsed time     
	def setTimerClk(self):
		self.t_lap= datetime.datetime.now()-self.t_0
		self.timer_label.setText("%d:%03d"%(self.t_lap.seconds,self.t_lap.microseconds/1000))

	def resetMaster(self):
		if self.timer_running==True:
			RPIO.del_interrupt_callback(self.gpio_e)
			self.timer_clk.stop()
		self.sortTree(reset=True)
		self.rfid_label.setText('')	
		self.timer_label.setText('0:000')	
		self.rfid_enable=True
		self.timer_enable=False
		self.timer_running=False

#disable track and if timer was running kill's interrupt
	def disableTrack(self):
		self.track_clk.stop()
		if self.timer_running==False and self.timer_enable==True:
			RPIO.del_interrupt_callback(self.gpio_b)
		else:
			self.sortTree(reset=False)	
		self.rfid_label.setText('')	
		self.timer_label.setText('0:000')	
		self.timer_running=False
		self.rfid_enable=True
################################################################################
	def sortTree(self,reset):
		if reset==False:
			self.float_timer=float("%d.%03d"%(self.t_lap.seconds,self.t_lap.microseconds/1000))
		else:
			self.float_timer=float("inf")

		match_item=self.gui_data.tree_widget.findItems(self.tag_id,QtCore.Qt.MatchExactly,1)
		self.gui_data.tree_widget.blockSignals(True)
		fdata=open('/home/pi/Desktop/thermocup/data/temp.txt','w')
		if len(match_item)==0:
			new_item=QtGui.QTreeWidgetItem(self.gui_data.tree_widget)
			new_item.setData(1,QtCore.Qt.DisplayRole,self.tag_id)
			new_item.setData(2,QtCore.Qt.DisplayRole,self.float_timer)
			new_item.setTextAlignment(0,4)
			new_item.setTextAlignment(1,4)
			new_item.setTextAlignment(2,4)
			new_item.setCheckState(3,QtCore.Qt.Unchecked)
		elif self.float_timer<=float(match_item[0].text(2)):
			new_sub_item=QtGui.QTreeWidgetItem(match_item[0])
			new_sub_item.setData(1,QtCore.Qt.DisplayRole,float(match_item[0].text(1)))
			new_sub_item.setData(2,QtCore.Qt.DisplayRole,float(match_item[0].text(2)))
			match_item[0].setData(2,QtCore.Qt.DisplayRole,self.float_timer)
			new_sub_item.setTextAlignment(0,4)
			new_sub_item.setTextAlignment(1,4)
			new_sub_item.setTextAlignment(2,4)
			new_sub_item.setCheckState(3,QtCore.Qt.Unchecked)
		elif self.float_timer>float(match_item[0].text(2)):
			new_sub_item=QtGui.QTreeWidgetItem(match_item[0])
			new_sub_item.setData(1,QtCore.Qt.DisplayRole,self.tag_id)
			new_sub_item.setData(2,QtCore.Qt.DisplayRole,self.float_timer)
			new_sub_item.setTextAlignment(0,4)
			new_sub_item.setTextAlignment(1,4)
			new_sub_item.setTextAlignment(2,4)
			new_sub_item.setCheckState(3,QtCore.Qt.Unchecked)
		
		self.gui_data.tree_widget.sortItems(2,0)
		print "saving to file"
		for i in range(0,self.gui_data.tree_widget.topLevelItemCount()):
			aux=self.gui_data.tree_widget.topLevelItem(i)		
			aux.setData(0,QtCore.Qt.DisplayRole,i+1)
			fdata.write("%d,%d,%.03f\n"%(int(aux.text(0)),int(aux.text(1)),float(aux.text(2))))
			for j in range(0,aux.childCount()):
				fdata.write(",%d,%.03f\n"%(int(aux.child(j).text(1)),float(aux.child(j).text(2))))

		fdata.close() 
		self.gui_data.tree_widget.blockSignals(False)


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
					if in_number=='MASTER':
						  self.gui_data.track_list[in_channel].resetMaster()					
					else:
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
