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
    elif node == 2:    #2 mean CLA NODE
        return private_data.cla_map[num]
    elif node == 4:      #4 SAB
        return private_data.sab_map[num]
    else:
        return "UNKNOWN"
    
#the server name actually is RG's name, so did not know which active node will be send
#so set the server name as unknown, it will be assign after analysis IPC_IN message.  
def getServerName(server, num):
    return "CLA-Unknown"

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
    
def FindMessageItem(srcNode, src, srcInstance, dstNode, dst, dstInstance, senderPid):
    for tmp in ALLProcessPairMessagesArray:
        if tmp.srcNode == srcNode and tmp.src ==src and tmp.dst == dst and tmp.srcInstance == srcInstance \
        and tmp.dstNode == dstNode and tmp.dstInstance ==dstInstance and tmp.srcPid == senderPid:
            return tmp
    return None


def appendFragmentMsg(line):
    return

def isNeedTrace(src, dst):
    for pair in process_pair:
        if (pair[0] == src and pair[1] == dst) or (pair[0] == dst and pair[1] == src):
            return True
    return False

def checkPlatform(filename):
    matchObj = re.search(r"CLA", logFile)
    if matchObj:
        return "LittleEndian"
    matchObj = re.search(r"AS", logFile);
    if matchObj:
        return "BigEndian"
    return "BigEndian"
    
          
def collectMsg(fileName, direction):            
    platform = checkPlatform(fileName)
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

                if msgDirection == "IPC_OUT":
                    if platform == "LittleEndian":
                        srcPid = int(msgData[36] + msgData[35], 16) 
                    else:
                        srcPid = int(msgData[35] + msgData[36], 16)
                else:
                    if platform == "LittleEndian" and srcNode != dstNode:   #CLA node and message from different node.
                        srcPid = int(msgData[35] + msgData[36], 16)
            
                if not isNeedTrace(srcProcess, dstProcess):
                    continue;
                item = FindMessageItem(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
                if msgDirection == direction and direction == "IPC_OUT":
                    if not item:
                        item = processPairMessageList(srcNode, srcProcess, srcInstance, \
                                        dstNode, dstProcess, dstInstance, srcPid)
                        ALLProcessPairMessagesArray.append(item)
                    message = messageItem("12345555", "TRACE_TYPE_INFO_LOG", msgData)
                    item.appendOutMsg(message)
                elif msgDirection == direction and direction == "IPC_IN":
                    if item and item.dstNode == "CLA-Unknown":
                        realDestNode = tmpArr[4]
                        item.dstNode = realDestNode
                        
                
    fp.close()

for root,dirs,files in os.walk(r'log'):
    for logFile in files:
        matchObj = re.search(r"log$", logFile)    
        if matchObj:
            collectMsg('log/'+ logFile, "IPC_OUT")

#parse IPC_IN message used to set DST node name   
for root,dirs,files in os.walk(r'log'):
    for logFile in files:
        matchObj = re.search(r"log$", logFile)    
        if matchObj:
            collectMsg('log/'+ logFile, "IPC_IN")

             
for tmp in ALLProcessPairMessagesArray:
    print tmp.srcNode+"/"+tmp.src+"_"+str(tmp.srcInstance)+"["+str(tmp.srcPid)+"]"+"------->"+tmp.dstNode+ \
    "/"+tmp.dst+"_"+str(tmp.dstInstance) + "(" + str(len(tmp.outMsg)) +")"
#     for tmp2 in tmp.outMsg:
#             print tmp2.msgData

            
