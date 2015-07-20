#!/usr/bin/python 

import os
import genMSC

def writeHTMLhead(fileObject):
    head = "<html><head><script src=\"./mscgen-inpage.js\" defer></script> \
    <script type=\"text/javascript\" src=\"jquery-1.11.3.min.js\"></script> \
    <script type=\"text/javascript\" src=\"./genFilter.js\"></script> \
    </head><body>"
    fileObject.write(head)
    
def writeBody(fileObject):
    body = '''<div id="div1">
        <p>one</p>
    <select id="node_1" onchange="addProcessOptions(this.value, this.id)">
        <option value="0">Choose Node...</option>
    </select>
    <select id="process_1" onchange="addInstanceOptions(this.value, this.id)">
            <option value="0">Choose Process...</option>
    </select>
    <select id="instance_1" >
            <option value="0">Choose Instance...</option>
    </select>
    <p>two</p>
    <select id="node_2" onchange="addProcessOptions(this.value, this.id)">
        <option value="0">Choose Node...</option>
    </select>
    <select id="process_2" onchange="addInstanceOptions(this.value, this.id)">
            <option value="0">Choose Process...</option>
    </select>
    <select id="instance_2">
            <option value="0">Choose Instance...</option>
    </select>
    <ul id="listID"></ul>
</div>'''
    fileObject.write(body)
    

    
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
    writeBody(fileObject)
    writeMSC(fileObject, genMSC.genMSC())
    writeHTMLEnd(fileObject)
    fileObject.close()
    print "generate NGLOG.html successfully"
    
genHTML()
    
    