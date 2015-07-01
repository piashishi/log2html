#!/usr/bin/python 
import re
import os

import private_data


msgDirection = ""    #IPC_IN for incoming messages, IPC_OUT for out messages
fragmentFlag = "" #  1/1 mean no fragment, 1/3 mean the first one of 3 fragments

ALLProcessPairMessagesArray=[]  #collect all out message, each node is messageItem

process_pair = [["TRACE_CTRL", "TRACE_PROXY"], ["TRACE_PROXY", "SC"]]

def getNodeName(node, num):
    if node == 0:    #0 mean AS_NODE
        return private_data.as_map[num]
    if node == 2:    #2 mean CLA NODE
        return private_data.cla_map[num]
    if node == 4:      #4 SAB
        return private_data.sab_map[num]
    
def getServerName(server, num):
    return "CLA?"

def getNGName(node, node_num, server, ser_num):
    if node == 0xff:
        return getServerName(server, ser_num)
    else:
        return getNodeName(node, node_num)
   
class messageItem:
    def __init__(self, timestamp, msgType, msgData):
        self.timestamp = timestamp
        self.msgType = msgType
        self.msgData = msgData
        self.isReceived = False
        
    def setMsgReceived(self):
        self.isReceived = True
    
#processMessageList, store out messages for one process pair
class processPairMessageList:
    def __init__(self, srcNode,src, srcInstance, dstNode, dst, dstInstance, srcPid):
        self.src = src
        self.srcInstance = srcInstance
        self.srcPid = srcPid
        self.dst = dst
        self.dstInstance = dstInstance
        self.srcNode = srcNode
        self.dstNode = dstNode
        self.outMsg = []
    def appendOutMsg(self, data):
        self.outMsg.append(data)
  
def FindMessageItem(src, srcInstance, dst, dstInstance, senderPid):
    for tmp in ALLProcessPairMessagesArray:
        if tmp.src ==src and tmp.dst == dst and tmp.srcInstance == srcInstance \
        and tmp.dstInstance ==dstInstance and tmp.srcPid == senderPid:
            return tmp
    return None


def appendFragmentMsg(line):
    return

def isNeedTrace(src, dst):
    for pair in process_pair:
        if (pair[0] == src and pair[1] == dst) or (pair[0] == dst and pair[1] == src):
            return True
    return False
            
def collectMsg(fileName, direction):            
    fp = open(fileName, "r");
    for line in fp.readlines():
        msgLine = re.search("LIBMSG: MMON", line)
        if msgLine:     
            tmpArr = re.split(r' +', line);
            msgInfo = re.split(r";", tmpArr[8])  # tmpArr[8] is LIB MSG information
            fragmentFlag = msgInfo[2]  # get fragment flag
            msgDirection = msgInfo[3]  # get msg direction
           
            matchObj = re.search(r'([0-9A-Fa-f]{2} ){2,}', line);
            if matchObj:
                msgData = re.split(r' ', matchObj.group())
                
                if fragmentFlag != "1/1":
                    appendFragmentMsg(msgData)
                    continue

                srcProcess = private_data.process_map[int(msgData[22], 16)]
                srcInstance = int(msgData[23], 16)
                srcNode = getNGName(int(msgData[24], 16), int(msgData[25], 16), int(msgData[26], 16), int(msgData[27], 16))
                dstProcess = private_data.process_map[int(msgData[28], 16)]
                dstInstance = int(msgData[29], 16)
                dstNode = getNGName(int(msgData[30], 16), int(msgData[31], 16), int(msgData[32], 16), int(msgData[33], 16))
                srcPid = int(msgData[36] + msgData[35], 16) 
            
                if not isNeedTrace(srcProcess, dstProcess):
                    continue;
         
                if msgDirection == direction and direction == "IPC_OUT":
                    item = FindMessageItem(srcProcess, srcInstance, dstProcess, dstInstance, srcPid)
                    if not item:
                        item = processPairMessageList(srcNode, srcProcess, srcInstance, \
                                        dstNode, dstProcess, dstInstance, srcPid)
                        ALLProcessPairMessagesArray.append(item)
                    item.appendOutMsg(msgData)
                if msgDirection == direction and direction == "IPC_IN":
                    print "IN"
                
    fp.close()

for root,dirs,files in os.walk(r'./'):
    for logFile in files:
        matchObj = re.search(r"log$", logFile)    
        if matchObj:
            collectMsg(logFile, "IPC_OUT")

for root,dirs,files in os.walk(r'./'):
    for logFile in files:
        matchObj = re.search(r"log$", logFile)    
        if matchObj:
            collectMsg(logFile, "IPC_IN")
         
for tmp in ALLProcessPairMessagesArray:
    print tmp.srcNode+"/"+tmp.src+"_"+str(tmp.srcInstance)+"["+str(tmp.srcPid)+"]"+"------->"+tmp.dstNode+ \
    "/"+tmp.dst+"_"+str(tmp.dstInstance)
    for tmp2 in tmp.outMsg:
        print tmp2
    

            
