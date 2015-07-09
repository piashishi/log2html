#!/usr/bin/python 

import parseLog

ALLMSG = []
MSGLable = {}
MSCContent = ""

class MSCItem:
    def __init__(self, msgPair, msgItem):
        self.src = msgPair.srcNode+"/"+msgPair.src+"_"+str(msgPair.srcInstance)+"["+str(msgPair.srcPid)+"]"
        self.dst = msgPair.dstNode+"/"+msgPair.dst+"_"+str(msgPair.dstInstance)+"["+str(msgPair.dstPid)+"]"
        self.msgType = msgItem.msgType
        self.timestamp = msgItem.timestamp
        self.srcLabel = ""
        self.dstLabel = ""
        self.sameMsgCounter = 1

sortProcessLabel  = []  
 
def sortLabel():
    for process in parseLog.process_pair:
        if not process[0] in sortProcessLabel: 
            sortProcessLabel.append(process[0])
        if not process[1] in sortProcessLabel:
            sortProcessLabel.append(process[1])
                  
def genMSCLabel():
    index = 0
    for pair in parseLog.ALLProcessPairMessagesArray:
        for data in pair.outMsg:
            msg = MSCItem(pair, data)
            if not MSGLable.has_key(msg.src):
                MSGLable[msg.src] = str(index)
                index += 1
            if not MSGLable.has_key(msg.dst):
                MSGLable[msg.dst] = str(index)
                index += 1
            msg.srcLabel = MSGLable[msg.src]
            msg.dstLabel = MSGLable[msg.dst]
            ALLMSG.append(msg)
    sortLabel()

def printMSCLabel():
    global MSCContent
    maxSize = len(MSGLable)
    index = 1
    for processLabel in sortProcessLabel:
        tmpArr = []
        for key in MSGLable.keys():
            if processLabel in key:
                value = MSGLable[key]
                pair =(key, value)
                tmpArr.append(pair)
        tmpArr.sort()
        for pair in tmpArr:
            if index == maxSize:
                Label = pair[1] + " [ label = \"" + pair[0] + "\" ]" + ";" + "\n"
            else:
                Label = pair[1] + " [ label = \"" + pair[0] + "\" ]" + ","
            MSCContent += Label
            index += 1

        
def printMSCContent():
    global MSCContent
    index = 0
    prevMsg = ALLMSG[0]
    for msg in ALLMSG:
        if prevMsg.srcLabel == msg.srcLabel and prevMsg.dstLabel == msg.dstLabel and prevMsg.msgType == msg.msgType:
            if index != 0:
                prevMsg.sameMsgCounter += 1
        else:
            if prevMsg.sameMsgCounter != 1:
                content =  prevMsg.srcLabel +"=>"+prevMsg.dstLabel +" [ label = \""+ \
                    prevMsg.msgType +"("+str(prevMsg.sameMsgCounter)+")"+"\"];" + "\n"
            else:
                content =  prevMsg.srcLabel +"=>"+prevMsg.dstLabel +" [ label = \""+prevMsg.msgType + "\"];" + "\n"
            MSCContent += content
            prevMsg = msg
        index += 1
        
def printMSCHeader():
    global MSCContent
    MSCContent += "<mscgen>\n"
    MSCContent += "msc {\n"
    #print "hscale = \"2\";"
    
def printMSCEnd():
    global MSCContent
    MSCContent += "}\n"
    MSCContent += "</mscgen>\n"
    

def genMSC():
    genMSCLabel()
    printMSCHeader()
    printMSCLabel()
    printMSCContent()
    printMSCEnd()
    return MSCContent
    
print genMSC()
