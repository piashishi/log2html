#!/usr/bin/python 

import os
import genMSC

def writeHTMLhead(fileObject):
    head = "<html><head><script src=\"./mscgen-inpage.js\" defer></script></head><body>"
    fileObject.write(head)
    
def writeMSC(fileObject, MSC):
    fileObject.write(MSC)
    
def writeHTMLEnd(fileObject):
    fileObject.write("</body></html>")
    
def createFile():
    fileName = "NGLOG.html"
    if os.path.exists(fileName):
        os.remove(fileName)
    fileObject = open(fileName, "w+")
    return fileObject

def genHTML():
    fileObject = createFile()
    writeHTMLhead(fileObject)
    writeMSC(fileObject, genMSC.genMSC())
    writeHTMLEnd(fileObject)
    fileObject.close()
    print "generate NGLOG.html successfully"
    
genHTML()
    
    