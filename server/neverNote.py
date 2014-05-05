#! /usr/bin/env python
##
 # This file is under MIT Licence
 # Copyright (C) 2014 Skander Ben Mahmoud <skander.benmahmoud@esprit.tn> 
 #   
 # Permission is hereby granted, free of charge, to any person obtaining a copy of
 # this software and associated documentation files (the "Software"),
 # to deal in the Software without restriction, including without limitation
 # the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 # sell copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:
 #   
 # The above copyright notice and this permission notice shall be included in all copies
 # or substantial portions of the Software.
 #   
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 # INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE
 # AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
 # DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
 # ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.




def CaptureNote(aNotePageNumber):
  import cv2.cv as cv
  import time

  fname = "/tmp/nevernoteCap-{0}.jpg".format(aNotePageNumber)
  capture = cv.CaptureFromCAM(0)
  i = 10
  img = None
  while i > 0:
    print i
    img = cv.QueryFrame(capture)
#    cv.WaitKey(10)
    time.sleep(0.001)
    i = i - 1
  
  
  cv.SaveImage(fname, img)

  return fname


# aListOfCapturedNotes is the notes file names saved from CaptureNote
# aSize is the size of the original PDF, it's format is : (width, height)
def generatePDF(aListOfCapturedNotes, aSize):
  from reportlab.pdfgen import canvas
  from reportlab.platypus import Image

  fname = "/tmp/notes.pdf"
  c = canvas.Canvas(fname, pagesize=aSize)

  for note in aListOfCapturedNotes:
    c.drawImage(note, 0, 0, aSize[0], aSize[1])
    c.showPage() # Save and start new page
  c.save()

  return fname

def addNotesToSlides(aSlidesFname, aNotesFname, aPages):
  from pyPdf import PdfFileWriter, PdfFileReader

  notesSlides = PdfFileWriter()
  notes = PdfFileReader(file(aNotesFname, "rb"))
  slides = PdfFileReader(file(aSlidesFname, "rb"))

  finalNumPages = notes.getNumPages() + slides.getNumPages()

  notesIt = 0
  slidesIt = 0

  for pageNum in range(finalNumPages):
    if(notesIt < len(aPages) and pageNum == (aPages[notesIt] - 1)):
      notesSlides.addPage(notes.getPage(notesIt))
      notesIt = notesIt + 1
    else:
      notesSlides.addPage(slides.getPage(slidesIt))
      slidesIt = slidesIt + 1


  ostream = file("/tmp/slides+notes.pdf", "wb")
  notesSlides.write(ostream)
  ostream.close()

