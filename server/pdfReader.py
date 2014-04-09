#! /usr/bin/env python

'''
  This file is under MIT Licence
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


from PyQt4 import QtCore, QtGui, Qt
import QtPoppler


class PDFWindow(QtGui.QWidget):
  def __init__(self, doc = None):
    QtGui.QWidget.__init__(self, None)
    self.doc = doc
    self.pdfImage = None
    self.currentPage = 0
    self.windowOpened = False
    # Will contain 3 rendred pages : [Previous, Current, Next]
    # We use the buffer to avoid performance issues.
    # Render operation take too much time. Especially on the Pi
    # For more details see issue#1 on github.
    self.renderBuffer = [None, None, None]


  def render(self, page):
    page = self.doc.page(page)

    if not page:
      return None

    pageWidth = page.pageSize().width() * 1.0
    pageHeight = page.pageSize().height() * 1.0


    screenWidth = QtGui.QApplication.desktop().width() * 1.0
    screenHeight = QtGui.QApplication.desktop().height() * 1.0

    hDPI = vDPI = 72.0

    hDPI = (screenWidth / pageWidth) * hDPI  # Zoom
    vDPI = (screenHeight / pageHeight) * vDPI  # Zoom

    pdfImage = page.renderToImage(hDPI, vDPI)
    return pdfImage


  def initRenderBuffer(self):
    self.renderBuffer[0] = self.render(self.currentPage -1)
    self.renderBuffer[1] = self.render(self.currentPage)
    self.renderBuffer[2] = self.render(self.currentPage +1)

  def paintEvent(self, event):
    painter = QtGui.QPainter(self)
    if self.pdfImage is not None:
      painter.drawImage(0,0, self.pdfImage)

  def next(self):

    if (self.currentPage + 1 < self.doc.numPages()):
      print "Next"
      self.currentPage += 1
      self.renderBuffer[0] = self.renderBuffer[1]
      self.renderBuffer[1] = self.renderBuffer[2]
      self.display()
      self.renderBuffer[2] = self.render(self.currentPage + 1)

  def back(self):
     if (self.currentPage > 0):
      print "Back !"
      self.currentPage -= 1
      self.renderBuffer[2] = self.renderBuffer[1]
      self.renderBuffer[1] = self.renderBuffer[0]
      self.display()
      self.renderBuffer[0] = self.render(self.currentPage - 1)


  def display(self):
    print "Displaying stuff ..."
    if(not self.windowOpened):
      self.initRenderBuffer()
      self.showFullScreen()
      self.windowOpened = True

    self.pdfImage = self.renderBuffer[1] # We always display the current rendered.
    self.update()

  def hideWin(self):
    self.hide()
    self.currentPage = 0
    self.windowOpened = False


