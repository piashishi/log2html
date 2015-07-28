#!/usr/bin/python 

import os
import genMSC

def writeHTMLhead(fileObject):
    head = "<html><head><script src=\"./mscgen-inpage.js\" defer></script> \
    <script type=\"text/javascript\" src=\"jquery-1.11.3.min.js\"></script> \
    <script type=\"text/javascript\" src=\"./genFilter.js\"></script> \
    <link type=\"text/css\" href=\"show.css\" rel=\"stylesheet\"></script> \
    </head><body>"
    fileObject.write(head)
    
def writeBody(fileObject):
    body = '''
<div class="main_div">
    <div class="filter">
        <div class="filterclass" id="filter_div">
            <p>Process One</p>
            <select class="srcNode" onchange="addProcessOptions(this.value, this)">
            </select>
            <select class="srcProcess" onchange="addInstanceOptions(this.value, this)">
            </select>
            <select class="srcInstance" >
            </select>
            <p>Process Two</p>
            <select class="dstNode" onchange="addProcessOptions(this.value, this)">
            </select>
            <select class="dstProcess" onchange="addInstanceOptions(this.value, this)">
            </select>
            <select class="dstInstance">
            </select>
            <div class="msgType_div">
                <ul class="listID"></ul>
            </div>
            <div class="button_div">
                <button type="button" class="apply">Apply Filter</button>
                <button type="button" class="del"> Del</button>
                <button type="button" class="add">Add</button>
            </div>
        </div>
    </div>
    <div class="show_div">'''
    fileObject.write(body)
    

    
def writeMSC(fileObject, MSC):
    fileObject.write(MSC)
    
    bodyEnd = '''        </div>
    </div>'''
    fileObject.write(bodyEnd)
    
    
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
    
    