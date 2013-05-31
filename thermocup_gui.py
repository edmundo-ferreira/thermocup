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

title='ThermoCup 2013'
title_style='QLabel { font-size: 35pt; color:gray;}'
track_style='QLabel { font-size: 23pt; color:gray;}'
timer_style='QLabel {font-size:28pt; color:red;}'
timer_style_invalid='QLabel {font-size:28pt; color:gray;}'
rfid_style='QLabel {font-size:22pt; color:blue;}'
rfid_style_invalid='QLabel {font-size:22pt; color:gray;}'
table_header_style='QHeaderView {font-size: 16pt;}'
table_item_style='QTreeWidget, QTreeView{font-size:14pt; color:black}'

RPIO.wait_for_interrupts(threaded=True)
RPIO.setwarnings(False)
	
gpio_b_list=[4,17,22,9]
gpio_e_list=[14,18,23,25]


class MainGui(QtGui.QWidget):
	def __init__(self,parent=None):
		QtGui.QWidget.__init__(self,parent)
		screen = QtGui.QDesktopWidget().screenGeometry() #get screen siz		
		
		#self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

		#list of reader threads	
		self.reader_list=list()
		self.reader_list.append(SerialReader(self,'/dev/ttyACM%s'%0))
		self.reader_list.append(SerialReader(self,'/dev/ttyACM%s'%1))
		self.reader_list.append(SerialReader(self,'/dev/ttyACM%s'%2))
		self.reader_list.append(SerialReader(self,'/dev/ttyUSB%s'%0))

	
		#list of track classes
		self.track_list=list()
		for i in range(0,len(gpio_b_list)):
			self.track_list.append(Track(self,gpio_b_list[i],gpio_e_list[i],i+1,screen.width()/2-700+i*300))

		#title label
		self.title= QtGui.QLabel(title, self)
		self.title.setStyleSheet(title_style)
		self.title.setFixedWidth(600)
		self.title.move(screen.width()/2-300,10)
		self.title.setAlignment(QtCore.Qt.AlignCenter)

		#ist_logo
		ist_logo = QtGui.QLabel(self)
		ist_logo.setPixmap( QtGui.QPixmap("ist_logo.png").scaled(280*0.82,150*0.82, QtCore.Qt.KeepAspectRatio))
	 
 		#cienciaviva_logo
		cienciaviva_logo= QtGui.QLabel(self)
		cienciaviva_logo.setPixmap(QtGui.QPixmap("cienciaviva_logo.tif").scaled(200*0.85,160*0.85, QtCore.Qt.KeepAspectRatio))
		cienciaviva_logo.move(screen.width()-200*0.9,0)


		#ranking table
		self.tree_widget= QtGui.QTreeWidget(self)
		self.tree_widget.setHeaderLabels(['Ranking','Team Number','Time (s)','Del'])
		self.tree_widget.setFixedWidth(1000)
		self.tree_widget.setFixedHeight(650)
		self.tree_widget.move(screen.width()/2-500,260)
		self.tree_widget.setColumnWidth(0,250)
		self.tree_widget.header().setResizeMode(0,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(1,250)
		self.tree_widget.header().setResizeMode(1,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(2,450)
		self.tree_widget.header().setResizeMode(2,QtGui.QHeaderView.Fixed)
		self.tree_widget.setColumnWidth(3,10)
		self.tree_widget.header().setResizeMode(3,QtGui.QHeaderView.Fixed)
		self.tree_widget.header().setDefaultAlignment(QtCore.Qt.AlignCenter) #alingment of header tags
		self.tree_widget.header().setStyleSheet(table_header_style)
		self.tree_widget.setStyleSheet(table_item_style)
		self.tree_widget.setAlternatingRowColors(True);
		
		
		fdata=open('/home/pi/Desktop/thermocup/data/temp.txt','r')
     		for row in fdata:
			aux=row.strip('\n').split(',')
			if not aux[0]=='':	
				new_item=QtGui.QTreeWidgetItem(self.tree_widget)
				new_item.setData(0,QtCore.Qt.DisplayRole,int(aux[0]))
				new_item.setData(1,QtCore.Qt.DisplayRole,int(aux[1]))
				new_item.setData(2,QtCore.Qt.DisplayRole,float(aux[2]))
				new_item.setCheckState(3,QtCore.Qt.Unchecked)
				new_item.setTextAlignment(0,4)
				new_item.setTextAlignment(1,4)
				new_item.setTextAlignment(2,4)
			else:
				new_sub_item=QtGui.QTreeWidgetItem(new_item)
				new_sub_item.setData(1,QtCore.Qt.DisplayRole,int(aux[1]))
				new_sub_item.setData(2,QtCore.Qt.DisplayRole,float(aux[2]))
				new_sub_item.setCheckState(3,QtCore.Qt.Unchecked)
				new_sub_item.setTextAlignment(0,4)
				new_sub_item.setTextAlignment(1,4)
				new_sub_item.setTextAlignment(2,4)

		fdata.close()
		
		self.tree_widget.header().setClickable(True)
		self.tree_widget.header().sectionClicked.connect(self.deleteItemsSelection)	
		
		self.showFullScreen() #show fullscreen


	def foda(self,index):
		print "welcome to foda"
		print index

	def deleteItemsSelection(self,header_index):
		if header_index==3:
			reply = QtGui.QMessageBox.question(self,'Message',"Are you sure to quit?", QtGui.QMessageBox.Yes|QtGui.QMessageBox.No,QtGui.QMessageBox.No)
			if reply == QtGui.QMessageBox.Yes:
				i=0
				count_items=self.tree_widget.topLevelItemCount()
				while i<count_items:
					aux=self.tree_widget.topLevelItem(i)		

					count_childs=aux.childCount()
					j=0
					while j<count_childs:
						if aux.child(j).checkState(3)==QtCore.Qt.Checked:
							print "removing child %d of item %d from table"%(j,i)	
							aux.removeChild(aux.child(j))
							count_childs=aux.childCount()	
							j=j-1
						j=j+1			

					if aux.checkState(3)==QtCore.Qt.Checked:
						if aux.childCount()==0:
							print "item has no child"
							print "removing item %d from table"%i
							self.tree_widget.takeTopLevelItem(i)
							count_items=self.tree_widget.topLevelItemCount()
							i=i-1
						else:
							print "this item is a parent have mercy on his sole, kill a child instead"
							aux.setData(2,QtCore.Qt.DisplayRole,float(aux.child(0).text(2)))
							aux.setCheckState(3,QtCore.Qt.Unchecked)
							aux.removeChild(aux.child(0))

					i=i+1
	

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
	def __init__(self,gui_data,gpio_b,gpio_e,track_id,pos_x):
		self.gui_data=gui_data	
		self.gpio_b=gpio_b
		self.gpio_e=gpio_e
		self.track_id=int(track_id)
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
		
		#track title
		track_label=QtGui.QLabel("Pista %d"%(self.track_id),self.gui_data)
		track_label.setStyleSheet(track_style)
		track_label.setFixedWidth(200)
		track_label.setAlignment(QtCore.Qt.AlignRight)
		track_label.move(pos_x+100,120)

		#timer label		
		self.timer_label=QtGui.QLabel('0:000',self.gui_data)
		self.timer_label.setStyleSheet(timer_style)
		self.timer_label.setFixedWidth(300)
		self.timer_label.setAlignment(QtCore.Qt.AlignRight)
		self.timer_label.move(pos_x,150)
		#rfid label
		self.rfid_label=QtGui.QLabel('',self.gui_data)
		self.rfid_label.setStyleSheet(rfid_style)
		self.rfid_label.setFixedWidth(200)
		self.rfid_label.setAlignment(QtCore.Qt.AlignCenter)
		self.rfid_label.move(pos_x+150,200)
	
	def enableTrack(self,tag_id):
		if self.rfid_enable==True:
			print "tagid %s enabled track %s"%(tag_id,self.track_id)
			self.rfid_enable=False
			self.tag_id=tag_id	
			self.track_clk.start(20000)
			self.rfid_label.setText("%s"%tag_id)
			self.timer_enable=True
			RPIO.add_interrupt_callback(self.gpio_b,self.startClk,edge='rising',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=None)

	def startClk(self,gpio,val):
		if self.timer_enable==True:
			print "tagid %s started run on track %s"%(self.tag_id,self.track_id)
			self.timer_enable=False
			RPIO.del_interrupt_callback(self.gpio_b)
			self.t_0=datetime.datetime.now()
			self.timer_clk.start(5)
			self.track_clk.stop()
			self.timer_running=True
			self.gui_data.update()
			RPIO.add_interrupt_callback(self.gpio_e,self.stopClk,edge='rising',pull_up_down=RPIO.PUD_UP,debounce_timeout_ms=None)

	def stopClk(self,gpio,val):
		if self.timer_running==True: 
			print "tagid %s ended run on track %s"%(self.tag_id,self.track_id)
			self.timer_running=False
			RPIO.del_interrupt_callback(self.gpio_e)
			self.timer_clk.stop()
			self.track_clk.start(5)			
		
	#get and set ellapsed time     
	def setTimerClk(self):
		self.t_lap= datetime.datetime.now()-self.t_0
		self.timer_label.setText("%d:%03d"%(self.t_lap.seconds,self.t_lap.microseconds/1000))

			

	#disable track and if timer was running kill's interrupt
	def disableTrack(self,in_number=None):
		clean=False
		self.track_clk.stop() #closing it's self
		if in_number==None:
			if self.timer_running==False and self.timer_enable==True:
				print "tagid %s made no run on track %s disabling it "%(self.tag_id,self.track_id)
				RPIO.del_interrupt_callback(self.gpio_b)
				clean=True
			if self.timer_running==False and self.timer_enable==False: 
				print "tagid %s completed successfull run on track %s disabling it"%(self.tag_id,self.track_id)
				self.gui_data.update()
				time.sleep(5)
				self.sortTree(reset=False)	
				clean=True
		if in_number=='MASTER' :
			if self.timer_running==False and self.timer_enable==False and self.rfid_enable==False:
				print "%s is canceling after run, tagid %s and disabling track %s"%(in_number,self.tag_id,self.track_id)
				self.rfid_label.setStyleSheet(rfid_style_invalid)
				self.timer_label.setStyleSheet(timer_style_invalid)	
				self.gui_data.update()
				time.sleep(5)	
				self.sortTree(reset=True)
				clean=True
			if self.timer_running==False and self.timer_enable==True:
				self.timer_enable=False
				print "%s is canceling before run, tagid %s and disabling track %s"%(in_number,self.tag_id,self.track_id)
				clean=True
			if self.timer_running==True and self.timer_enable==False:
				self.timer_running=False
				self.timer_clk.stop()
				RPIO.del_interrupt_callback(self.gpio_e)
				self.rfid_label.setStyleSheet(rfid_style_invalid)
				self.timer_label.setStyleSheet(timer_style_invalid)	
				print "%s is canceling during run, tagid %s and disabling track %s"%(in_number,self.tag_id,self.track_id)
				self.gui_data.update()
				time.sleep(5)	
				self.sortTree(reset=True)	
				clean=True

		if clean==True:
			self.rfid_label.setStyleSheet(rfid_style)
			self.timer_label.setStyleSheet(timer_style)	
			self.rfid_label.setText('')	
			self.timer_label.setText('0:000')	
			self.rfid_enable=True

		self.gui_data.update()


	def sortTree(self,reset):
		if reset==False:
			self.float_timer=float("%d.%03d"%(self.t_lap.seconds,self.t_lap.microseconds/1000))
		else:
			self.float_timer=float("inf")



		match_item=self.gui_data.tree_widget.findItems(self.tag_id,QtCore.Qt.MatchExactly,1)
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
				print in_tag
				if not in_number==None and in_channel<len(self.gui_data.track_list):
					if in_number=='MASTER':
						  self.gui_data.track_list[in_channel].disableTrack(in_number)					
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
