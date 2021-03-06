#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__title__ = outputTxtplan
__author__ = zhangben 
__mtime__ = 2021/3/17 : 18:07
__description__: 

THEOREM: A good programmer should wipe the butts of his predecessors in an amicable way,
    instead of reinventing a new butt.
        As long as this , code is far away from bugs, and with the god animal protecting
            I love animals. They taste delicious.
"""

import sys
import re,os,sys
from PySide.QtGui import *
from PySide.QtCore import *
from PySide import QtXml
from PySide.QtUiTools import QUiLoader
import pysideuic as uic
# from PySide2.QtWidgets import *
# from PySide2.QtGui import *
# from PySide2.QtCore import *
# from PySide2.QtUiTools import QUiLoader
# import pyside2uic as uic
#  ============= ===live template require variables =====================
#  o  utputTxtplan O OutputTxtplan || OutputTxtplan  utputtxtplan
# class Stream(QObject):
#     newText = Signal(str)
#     # def __init__(self):
#     #     super(Stream,self).__init__()
#     def write(self, text):
#         self.newText.emit(str(text).decode('gb2312'))
import logging
# logger = logging.getLogger(__name__)
#
# class QtHandler(logging.Handler):
#
#     def __init__(self):
#         logging.Handler.__init__(self)
#
#     def emit(self, record):
#         record = self.format(record)
#         Stream.stdout().write("{}\n".format(record))
#
# handler = QtHandler()
# handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
# logger.addHandler(handler)
# logger.setLevel(logging.DEBUG)

# class Stream(QObject):
#     _stdout = None
#     _stderr = None
#     messageWritten = Signal(str)
#     def flush( self ):
#         pass
#     def fileno( self ):
#         return -1
#     def write( self, msg ):
#         if ( not self.signalsBlocked() ):
#             self.messageWritten.emit(unicode(msg))
#
#     @staticmethod
#     def stdout():
#         if ( not Stream._stdout ):
#             Stream._stdout = Stream()
#             sys.stdout = Stream._stdout
#         return Stream._stdout
#
#     @staticmethod
#     def stderr():
#         if ( not Stream._stderr ):
#             Stream._stderr = Stream()
#             sys.stderr = Stream._stderr
#         return Stream._stderr
class QtHandler(logging.Handler):

    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        XStream.stdout().write("{}\n".format(record))

class XStream(QObject):
    _stdout = None
    _stderr = None
    messageWritten = Signal(str)
    def flush( self ):
        pass
    def fileno( self ):
        return -1
    def write( self, msg ):
        if ( not self.signalsBlocked() ):
            self.messageWritten.emit(unicode(msg))

    @staticmethod
    def stdout():
        if ( not XStream._stdout ):
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if ( not XStream._stderr ):
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr


logger = logging.getLogger(__name__)
handler = QtHandler()
handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)



class OptTxEdt(QWidget):
    executeObject = Signal(str)
    def __init__(self,*args,**kwargs):
        super(OptTxEdt, self).__init__(*args,**kwargs)
        self.output = QTextEdit(self)
        self.layout = QVBoxLayout()
        # self.frame = QFrame(self)
        self.hlayout = QHBoxLayout()
        self.bt_clr = QPushButton(self)
        self.bt_clr.setText("clear...")
        self.bt_run = QPushButton(self)
        self.bt_run.setText("run bat")
        self.hlayout.addWidget(self.bt_clr)
        self.hlayout.addWidget(self.bt_run)
        # self.frame.setLayout(self.hlayout)
        self.layout.addWidget(self.output)
        self.layout.addLayout(self.hlayout)
        self.setLayout(self.layout)
        # self.initUI()
        self.executeBat = None
        self.bt_clr.clicked.connect(self.output.clear)
        self.bt_run.clicked.connect(self.internalCalling)
        self.setAcceptDrops(True)
        self.output.setAcceptDrops(False)
        # self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowTitle(">>>bat debug")

    def initUI_process(self):
        # Layout are better for placing widgets
        # QProcess object for external app
        self.process = QProcess(self)
        # QProcess emits `readyRead` when there is data to be read
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        self.process.readyRead.connect(self.dataReady)
        # Just to prevent accidentally running multiple times
        # Disable the button when process starts, and enable it when it finishes
        # self.process.started.connect(lambda: self.runButton.setEnabled(False))
        # self.process.finished.connect(lambda: self.runButton.setEnabled(True))
    
    @Slot()
    def dataReady(self):
        cursor = self.output.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(str(self.process.readAll(),'gbk'))
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    def callProgram(self,cmd,*args):
        # run the process
        # `start` takes the exec and a list of arguments
        self.process.start(cmd,args)
    def dragEnterEvent(self, event):
        print('drag-enter')
        if event.mimeData().hasUrls():
            print(event.mimeData().urls()[-1])
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, e):
        #        print("DragMove")
        e.accept()

    # def dropEvent(self, e):
    #     #        print("DropEvent")
    #     #        position = e.pos()
    #     #        print(position)
    #     self.output.setText("wtf...........")  # +++
    #     e.setDropAction(Qt.MoveAction)  # +++
    #     e.accept()
    def dropEvent(self, event):
        url = event.mimeData().urls()[-1]
        self.executeBat  = url.toLocalFile()
        if self.executeBat .endswith('.bat'):
            self.executeObject.emit(self.executeBat)
            self.output.setText(self.executeBat)
        # event.setDropAction(Qt.MoveAction)
        event.accept()
    def internalCalling(self):
        self.initUI_process()
        # print(self.executeBat)
        if self.executeBat:
            self.callProgram(self.executeBat)
            if self.process.waitForFinished():
                print("ok")
        else:
            print("......")
    def redirectOPT(self):
        # sys.stdout = Log(self.txtedit)
        # sys.stdout = XStream()
        # sys.stdout.newText.connect(self.opt2txt)
        XStream.stdout().messageWritten.connect(self.opt2txt)
        # sys.stdout.messageWritten.connect(self.opt2txt)
        # sys.stderr = XStream()
        XStream.stderr().messageWritten.connect(self.opt2txt)
    def opt2txt(self, text,color=None):
        # print("get Message ....{}".format(text))
        cursor = self.output.textCursor()
        cursor.movePosition(QTextCursor.End)
        if color or text.startswith('#'):
            text = self.richTxt(text)
            cursor.insertHtml(str(text,'utf-8'))
            # txt_ex = unicode(text.decode('utf-8').encode('gb2312') )
            # txt_ex = "llllllllllllll    {}".format(text.decode('gbk'))
            # cursor.insertHtml(txt_ex)

            # cursor.insertText(os.linesep)
        else:
            cursor.insertText(text)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()
#Function Main Start
def main():
    app = QApplication(sys.argv)
    ui=OptTxEdt()
    ui.redirectOPT()
    ui.show()
    # bat = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'exec', 'maya2016.bat')
    # print(bat)
    # ui.callProgram(bat)
    sys.exit(app.exec_())
    print(".....em....")
#Function Main END

if __name__ == '__main__':
    main()
