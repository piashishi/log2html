#!/usr/bin/python 

import test

ALLMSG = []
MSGLable = {}
class MSCItem:
    def __init__(self, msgPair, msgItem):
        self.src = msgPair.srcNode+"/"+msgPair.src+"_"+str(msgPair.srcInstance)+"["+str(msgPair.srcPid)+"]"
        self.dst = msgPair.dstNode+"/"+msgPair.dst+"_"+str(msgPair.dstInstance)+"["+str(msgPair.dstPid)+"]"
        self.msgType = msgItem.msgType
        self.timestamp = msgItem.timestamp
        self.srcLabel = ""
        self.dstLabel = ""
        self.sameMsgCounter = 1

# sortProcessLabel  = {}    
# 
# def sortLabel():
#     for process in test.process_pair:
#         if not process[0] in sortProcessLabel.keys():
#             sortProcessLabel
#         if not process[1] in sortProcessLabel.keys:
#             sortProcessLabel.append(process)
                  
def genMSCLabel():
    index = 0
    for pair in test.ALLProcessPairMessagesArray:
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

def printMSCLabel():
    index = 1
    maxSize = len(MSGLable)
    for key in MSGLable.keys():
        value = MSGLable[key]
        print value + " [ label = \"" + key + "\" ]",
        if index == maxSize:
            print ";"
        else:
            print ",",
        index += 1
        
def printMSCContent():
    index = 0
    prevMsg = ALLMSG[0]
    for msg in ALLMSG:
        if prevMsg.srcLabel == msg.srcLabel and prevMsg.dstLabel == msg.dstLabel and prevMsg.msgType == msg.msgType:
            if index != 0:
                prevMsg.sameMsgCounter += 1
        else:
            if prevMsg.sameMsgCounter != 1:
                print prevMsg.srcLabel +"=>"+prevMsg.dstLabel +" [ label = \""+prevMsg.msgType +"("+str(prevMsg.sameMsgCounter)+")"+"\"];"
            else:
                print prevMsg.srcLabel +"=>"+prevMsg.dstLabel +" [ label = \""+prevMsg.msgType + "\"];"
            prevMsg = msg
        index += 1
        
def printMSCHeader():
    print "msc {"
    #print "hscale = \"2\";"
    
def printMSCEnd():
    print "}"
    
genMSCLabel()
printMSCHeader()
printMSCLabel()
printMSCContent()
printMSCEnd()