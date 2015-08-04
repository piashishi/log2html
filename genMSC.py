#!/usr/bin/python 

import filter
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
            
def get_msg_key(msg):
    return msg.timestamp
    
#the function will do:
#1: generate   MSCItem 
#2: generate    MSGLable
def genMSCLabel():
    index = 0
    for pair in filter.filterData:
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

def printMSCLabel():
    MSCContent = ""
    maxSize = len(MSGLable)
    index = 1
    for processLabel in filter.filterProcesses:
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
    return MSCContent

        
def printMSCContent():
    MSCContent = ""
    index = 0
    if len(ALLMSG) == 0:
        MSCContent += "No match data found"
        return
    print ALLMSG
    print len(ALLMSG)
    prevMsg = ALLMSG[0]
    for msg in ALLMSG:
        print msg.srcLabel, msg.dstLabel, msg.msgType
        if prevMsg.srcLabel == msg.srcLabel and prevMsg.dstLabel == msg.dstLabel and prevMsg.msgType == msg.msgType:
            if index != 0:
                #message is same as previous one, 
                prevMsg.sameMsgCounter += 1
        else:
            msgName, msgColor = parseLog.msgTypeToNameAndColor(prevMsg.msgType)
            if prevMsg.sameMsgCounter != 1:
                #avoid show too many same messages, the output will show how many times the messages was sent 
                content = "%s=>%s [ label = \"%s(%d)\", textcolor = \"%s\", linecolor = \"%s\"];\n" %  \
                    (prevMsg.srcLabel, prevMsg.dstLabel, msgName, prevMsg.sameMsgCounter, msgColor, msgColor)
            else:
                content = "%s=>%s [ label = \"%s\", textcolor = \"%s\", linecolor = \"%s\"];\n" % \
                    (prevMsg.srcLabel, prevMsg.dstLabel, msgName, msgColor, msgColor)
            MSCContent += content
            prevMsg = msg
        index += 1
    msgName, msgColor = parseLog.msgTypeToNameAndColor(prevMsg.msgType)
    lastContent ="%s=>%s [ label = \"%s(%d)\", textcolor = \"%s\", linecolor = \"%s\"];\n" %  \
                    (prevMsg.srcLabel, prevMsg.dstLabel, msgName, prevMsg.sameMsgCounter, msgColor, msgColor)
    MSCContent += lastContent
    return MSCContent
        
def printMSCHeader():
    MSCContent = ""
    MSCContent += "<mscgen>\n"
    MSCContent += "msc {\n"
#    MSCContent += "hscale = \"2\";"
    return MSCContent
    
def printMSCEnd():
    MSCContent = ""
    MSCContent += "}\n"
    MSCContent += "</mscgen>\n"
    return MSCContent

def clearMSC():
    global  ALLMSG, MSGLable
    ALLMSG = []
    MSGLable = {}
    
def createMSC():
    MSCContent  = ""
    clearMSC()
    genMSCLabel()
    MSCContent +=  printMSCHeader()
    MSCContent += printMSCLabel()
    MSCContent += printMSCContent()
    MSCContent += printMSCEnd()
    print MSCContent
    return MSCContent
