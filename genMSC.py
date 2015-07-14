#!/usr/bin/python 

import parseLog
import datetime


# the msc format is like that:
# msc {
# 
#  a [label="Client"],b [label="Server"];
# 
#  a=>b [label="data1"];
#  a-xb [label="data2"];
#  a=>b [label="data3"];
#  a<=b [label="ack1, nack2"];
#  a=>b [label="data2", arcskip="1"];
#  |||;
#  a<=b [label="ack3"];
#  |||;
# }

ALLMSG = []
#MSGLable is a dictionary, key is label name, like "AS10-0/SC_1[1111]" ,value is a alias of key.
#because MSC can't support the label name, so need use alias.
MSGLable = {}
MSCContent = ""

class MSCItem:
    def __init__(self, msgPair, msgItem):
        if msgPair.srcInstance != 0:
            self.src = msgPair.srcNode+"\n"+msgPair.src+"_"+str(msgPair.srcInstance)+"["+str(msgPair.srcPid)+"]"
        else:
            self.src = msgPair.srcNode+"\n"+msgPair.src+"["+str(msgPair.srcPid)+"]"
        if msgPair.dstInstance != 0:
            self.dst = msgPair.dstNode+"\n"+msgPair.dst+"_"+str(msgPair.dstInstance)+"["+str(msgPair.dstPid)+"]"
        else:
            self.dst = msgPair.dstNode+"\n"+msgPair.dst+ "["+ str(msgPair.dstPid)+"]"
        self.msgType = msgItem.msgType
        self.timestamp = msgItem.timestamp
        self.srcLabel = ""
        self.dstLabel = ""
        self.sameMsgCounter = 1

sortedProcessLabel  = []  
 
#sort label by process pair.
def sortProcessLabel():
    for process in parseLog.processPairNeedProcess:
        if not process[0] in sortedProcessLabel: 
            sortedProcessLabel.append(process[0])
        if not process[1] in sortedProcessLabel:
            sortedProcessLabel.append(process[1])
            
def get_msg_key(msg):
    return msg.timestamp
    
#the function will do:
#1: generate   MSCItem 
#2: generate    MSGLable
def genMSCLabel():
    index = 0
    for pair in parseLog.processPairArray:
        for data in pair.msgDataList:
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
    ALLMSG.sort(key = get_msg_key)
    sortProcessLabel()

def printMSCLabel():
    global MSCContent
    maxSize = len(MSGLable)
    index = 1
    for processLabel in sortedProcessLabel:
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
                #message is same as previous one, 
                prevMsg.sameMsgCounter += 1
        else:
            if prevMsg.sameMsgCounter != 1:
                #avoid show too many same messages, the output will show how many times the messages was sent 
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
#    MSCContent += "hscale = \"2\";"
    
def printMSCEnd():
    global MSCContent
    MSCContent += "}\n"
    MSCContent += "</mscgen>\n"
    

def genMSC():
    parseLog.parseNGLog("log")
    genMSCLabel()
    printMSCHeader()
    printMSCLabel()
    printMSCContent()
    printMSCEnd()
    return MSCContent
