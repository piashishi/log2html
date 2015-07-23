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
        <div class="filter_div">
            <p>Process One</p>
            <select id="node_1" onchange="addProcessOptions(this.value, this.id)">
                <option value="0">Nodes...</option>
            </select>
            <select id="process_1" onchange="addInstanceOptions(this.value, this.id)">
                <option value="0">Processes...</option>
            </select>
            <select id="instance_1" >
                <option value="0">Instances...</option>
            </select>
            <p>Process Two</p>
            <select id="node_2" onchange="addProcessOptions(this.value, this.id)">
                <option value="0">Nodes...</option>
            </select>
            <select id="process_2" onchange="addInstanceOptions(this.value, this.id)">
                <option value="0">Processes...</option>
            </select>
            <select id="instance_2">
                <option value="0">Instances...</option>
            </select>
            <p>-------------------------------------</P>
            <div class="msgType_div">
                <ul id="listID"></ul>
            </div>
            <button type="button">Apply Filter</button>
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
    
    