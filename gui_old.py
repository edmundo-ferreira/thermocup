# Copyright (C) 2012 by Edmundo Ferreira
# fc.edmundo@gmail.com
#
# This program is free software; you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
# GNU General Public License for more details.


from PyQt4 import QtCore, QtGui
import sys
import datetime
import random
import serial
import glob
import subprocess
import time

title='TermoCup 2013'
title_style='QLabel { font-size: 70pt; color:gray;}'
rfid_tag_style='QLabel {font-size:20pt; color:black;}'
timer_style_ON='QLabel {font-size:40pt; color:red;}'
timer_style_HOLD='QLabel {font-size:40pt; color:yellow;}'
timer_style_OFF='QLabel {font-size:40pt; color:black;}'
table_header_style='QHeaderView { font-size: 13pt; font-weight: bold; background-color:gray;}'
table_item_style='QTreeWidget, QTreeView{font-size:12pt; color:black}'


class App(QtGui.QWidget):
    def __init__(self):
        super(App, self).__init__() 
        self.initUI()
        

    def initUI(self):
        screen = QtGui.QDesktopWidget().screenGeometry() #get screen size

        #serial thread  INIT RFID DEVICE 
        # self.ports=glob.glob("/dev/ttyUSB*")
        # self.ser=serial.Serial(self.ports[0],9600)
        self.reader_thd=SerialReader()
        self.reader_thd.start() #STARTING THREAD
        print "Connected and started"
        QtCore.QObject.connect(self.reader_thd,QtCore.SIGNAL("rfid_detect(QString)"), self.rfid_detect)       
        

                
        #clock thread
        self.clock = QtCore.QTimer()
        self.clock.timeout.connect(self.getElapTime)

        #rfid label
        self.rfid_tagid=QtGui.QLabel('',self)
        self.rfid_tagid.setStyleSheet(rfid_tag_style)
        self.rfid_tagid.setFixedWidth(300)
        self.rfid_tagid.setAlignment(QtCore.Qt.AlignRight)
        self.rfid_tagid.move(screen.width()/2-200,300)
        
        #timer label
        self.timer=QtGui.QLabel('0:000000',self)
        self.timer.setStyleSheet(timer_style_OFF)
        self.timer.setFixedWidth(300)
        self.timer.setAlignment(QtCore.Qt.AlignRight)
        self.timer.move(screen.width()/2-150,220)
        self.timer_running=False
        
        #title label
        self.title= QtGui.QLabel(title, self)
        self.title.setStyleSheet(title_style)
        self.title.setFixedWidth(800)
        self.title.setAlignment(QtCore.Qt.AlignRight)
        self.title.move(screen.width()/2-400,30)

        #ist_logo
        ist_logo = QtGui.QLabel(self)
        ist_logo.setPixmap( QtGui.QPixmap("ist_logo.png").scaled(280,150, QtCore.Qt.KeepAspectRatio))
        ist_logo.move(30,30)
        

        
        # #cienciaviva_logo
        # cienciaviva_logo= QtGui.QLabel(self)
        # cienciaviva_logo.setPixmap( QtGui.QPixmap("cienciaviva_logo.tif").scaled(200,160, QtCore.Qt.KeepAspectRatio))
        # cienciaviva_logo.move(screen.width()-250,30)

        #shortcut start
        self.shortcut_start = QtGui.QShortcut(self)
        self.shortcut_start.setKey("F2")
        self.shortcut_start.activated.connect(self.start_fcn)
        
        #shortcut reset
        self.shortcut_reset=QtGui.QShortcut(self)
        self.shortcut_reset.setKey("F3")
        self.shortcut_reset.activated.connect(self.reset_fcn)

      
        #shortcut stop
        self.shortcut_stop = QtGui.QShortcut(self)
        self.shortcut_stop.setKey("F4")
        self.shortcut_stop.activated.connect(self.stop_fcn)



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
        #self.showFullScreen() #show fullscreen
        self.show()
 
        
    # edit the table
    def edit_rank_tree(self,item, index):
        print index
        if not (index==0 or index==1):
            item.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsEditable)           
            self.rank_tree.editItem(item, index)       
            item.setFlags(QtCore.Qt.ItemIsSelectable |  QtCore.Qt.ItemIsEnabled)



    def rfid_detect(self, tag_id):
        self.reader_thd.terminate()
        self.rfid_tagid.setText("TagId=%s"%tag_id)
        self.timer.setStyleSheet(timer_style_HOLD)
        #time.sleep(1)
        self.reader_thd.start()


    # start function
    def start_fcn(self):
        if self.timer_running==False:
            #starting the clock
            self.clock.start(1)
            self.t0=datetime.datetime.now()
            self.timer_running=True    

            
                   

    #stop function
    def stop_fcn(self):
        if self.timer_running==True:
            self.clock.stop()
            self.timer_running=False
            

    #reset function
    def reset_fcn(self):
        self.clock.stop()
        self.timer.setStyleSheet(timer_style_OFF)
        self.timer.setText("0:000000")
        self.timer_running=False
        

    #get ellapsed time     
    def getElapTime(self):
        elap= datetime.datetime.now()-self.t0
        self.timer.setText("%d:%06d"%(elap.seconds,elap.microseconds))
        

    #request password NOT READY
    def req_password(self,event):
        print "mete a pass porco"
        #pop=QtGui.QMessageBox.alert(self,''



    #close safeguard NOT READY
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message', "Are you sure to quit?", QtGui.QMessageBox.Yes |  QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            self.reader_thd.terminate()
            event.accept()
        else:
            event.ignore()     



############################  SERIAL THREAD      ##########################
class SerialReader(QtCore.QThread):
    def start(self,priority=QtCore.QThread.InheritPriority):
        self.out=None
        QtCore.QThread.start(self, priority)

    def run(self):
        sp = subprocess.Popen(["./my_poll_x32"], stdout=subprocess.PIPE)
        self.out, err = sp.communicate()
        self.emit(QtCore.SIGNAL("rfid_detect(QString)"),self.out)
        print self.out
        

    
    def terminate(self):
        try:
            QtCore.QThread.terminate(self)
            print "Stoping SerialRead Thread"    
        except:
            print "Unable to close SerialRead Thread"







if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = App()
    app.exec_()




