#! /usr/bin/env python
'''
 This file is under MIT License
 Copyright (C) 2014 Skander Ben Mahmoud <skander.benmahmoud@esprit.tn>

 Permission is hereby granted, free of charge, to any person obtaining a copy of
 this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 sell copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in all copies
 or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import sys


from PyQt4 import QtGui, QtCore, Qt

import QtPoppler

from autobahn.twisted.websocket import WebSocketServerProtocol, WebSocketServerFactory
import threading

from pdfReader import PDFWindow
import neverNote

import subprocess
import serial
import time

'''
  Values signification : 
  light : 0 if the light is off, 1 if on.
  dataShow : 0 if Off, 1 if On.
  curtains : 0 of Closed, 1 if Opened.
  ambiantLight : 'S' if night, 'E' if day.
'''
classroom_states = {'lights':0, 'dataShow':0, 'curtains':0, 'ambiantLight':'S'}


arduino_commands = {'getLight':'A', 'offLight':'B', 'onLight':'C',
  'offDataShow':'D', 'onDataShow':'E', 'closeCurtains':'F', 'openCurtains':'G'}


class ServerHandlerProtocol(WebSocketServerProtocol):
  def __init__(self):
    self.isWaitingData = False
    self.fileName = "" # TODO : This should be changed as pdfData then we will read from the data instead of the file.
    self.pdfWindowIsOpened = False
    self.path = '/tmp/remoteslideServerd/'
    self.th = QtCore.QThread.currentThread()
    self.notesCap = []
    self.notePages = []
    self.serial = initSerial()

  def onConnect(self, request):
    pass
  def onOpen(self):
    pass

  def onMessage(self, message, isBinary):

    if isBinary and self.isWaitingData:
      # Regarding to the protocol, this should be our data (the pdf)
      f = open(self.path + self.fileName, 'w+')
      f.write(message)
      f.close()
      self.isWaitingData = False
      self.notesCap = []
      self.notePages = []

    else:
      cmd = message.split(':')[0]  # Please refer to the doc to see the frame format

      if cmd == 'SEND':
        self.isWaitingData = True
        self.fileName = message.split(':')[1]
      elif cmd == 'OPEN':
        if(self.pdfWindowIsOpened):
          self.closePdfWindow()
        self.openPdfWindow()
      elif cmd == 'NEXT' and self.pdfWindowIsOpened:
        self.th.emit(QtCore.SIGNAL('next()'))
      elif cmd == 'BACK' and self.pdfWindowIsOpened:
        self.th.emit(QtCore.SIGNAL('back()'))
      elif cmd == 'EXIT' and self.pdfWindowIsOpened:
        self.closePdfWindow()
      elif cmd == 'CAPT':
        self.notesCap.append(neverNote.CaptureNote(pdfWindow.currentPage))
        self.notePages.append(pdfWindow.currentPage)
      elif cmd == 'SAVENOTES':
        ps = pdfWindow.doc.page(0).pageSize()
        size = (ps.width(), ps.height()) 
        noteFname = neverNote.generatePDF(self.notesCap, size)
        neverNote.addNotesToSlides(self.path + self.fileName, noteFname, self.notePages)
      elif cmd == 'SENDMAIL':
        subprocess.Popen(['java', '-jar', '/opt/ClientMail.jar'])


  def onClose(self, wasClean, code, reason):
    pass


  def openPdfWindow(self):
    print "Creating doc"
    doc = QtPoppler.Poppler.Document.load(self.path + self.fileName)
    doc.setRenderHint(QtPoppler.Poppler.Document.Antialiasing and QtPoppler.Poppler.Document.TextAntialiasing)
    pdfWindow.doc = doc

    self.th.emit(QtCore.SIGNAL('display()'))
    self.pdfWindowIsOpened = True
    self.run_open_routine()

  def closePdfWindow(self):
    self.th.emit(QtCore.SIGNAL('close()'))
    self.pdfWindowIsOpened = False
    self.run_close_routine()

  def run_open_routine(self):
    print 'Open routine ...'
    print classroom_states

    # Turning the datashow on
    if(classroom_states['dataShow'] == 0):
      self.serial.write(arduino_commands['onDataShow'])
      classroom_states['dataShow'] = 1

    # We check if the lights are on, then we close them.
    if(classroom_states['lights'] == 1):
      self.serial.write(arduino_commands['offLight'])
      classroom_states['lights'] = 0

    # We close the curtains :
    if(classroom_states['curtains'] == 0):
      self.serial.write(arduino_commands['openCurtains'])
      classroom_states['curtains'] = 1

  def run_close_routine(self):

    print 'Close routine ...'
    print classroom_states

    # Is it necessary to turn the lights on ?
    # Ambiant light mesurement Request : 
    self.serial.write(arduino_commands['getLight'])
    # Reading mesurement :
    classroom_states['ambiantLight'] = self.serial.read()

    # We check if the lights are on, then we close them.
    if(classroom_states['lights'] == 0):
      self.serial.write(arduino_commands['onLight'])
      classroom_states['lights'] = 1

    # Turning the datashow off
    if(classroom_states['dataShow'] == 1):
      self.serial.write(arduino_commands['offDataShow'])
      classroom_states['dataShow'] = 0

    # We start opening the curtains :
    if(classroom_states['curtains'] == 1):
      self.serial.write(arduino_commands['closeCurtains'])
      classroom_states['curtains'] = 0



class Server(QtCore.QThread):
  def __init__(self):
    QtCore.QThread.__init__(self)

  def run(self):
    print "Running server ..."
    from twisted.internet import reactor

    factory = WebSocketServerFactory("ws://localhost:9000", debug = False)
    factory.protocol = ServerHandlerProtocol 

    reactor.listenTCP(9000, factory)
    reactor.run()

def initSerial():
  fp = open('/tmp/blue_dev', 'r')
  device = fp.readline()
  fp.close()
  s = serial.Serial(device, 9600, timeout=5)
  return s

if __name__ == '__main__':

  #Running bluetooth pairing and opening connection.
  subprocess.Popen(['python', '/opt/pairNconnect.py'])

  # We wait a little bit to make sure that the connection is okey
  time.sleep(3)

  app = QtGui.QApplication(sys.argv)
  serverd = Server()
  serverd.start()
  pdfWindow = PDFWindow()
  pdfWindow.connect(serverd, QtCore.SIGNAL('display()'), pdfWindow.display, QtCore.Qt.QueuedConnection)
  pdfWindow.connect(serverd, QtCore.SIGNAL('close()'), pdfWindow.hideWin, QtCore.Qt.QueuedConnection)
  pdfWindow.connect(serverd, QtCore.SIGNAL('next()'), pdfWindow.next, QtCore.Qt.QueuedConnection)
  pdfWindow.connect(serverd, QtCore.SIGNAL('back()'), pdfWindow.back, QtCore.Qt.QueuedConnection)
  sys.exit(app.exec_())
