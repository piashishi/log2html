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
        self.dstPid = 0
        
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


def getPid(platform, lowByte, highByte):
    pid = 0
    if platform == "LittleEndian":
        pid = int(highByte + lowByte, 16) 
    else:
        pid = int(lowByte + highByte, 16)
    return pid

    

testline = "Jun 18 08:24:53.469097 debug AS7-0 trace_proxy[4618]: [0]: LIBMSG: MMON;28078;1/1;IPC_IN;2D00_000A_FFFF_120A<0800_0201_0400_1724;290979;0; 00 03 00 00 00 00 27 0f 00 00 27 0f 00 00 27 0f 00 00 27 0f 0b 09 08 00 02 01 04 00 2d 00 00 0a ff ff 00 17 24 27 00 00 00 00 81 42 00 08 00 00 00 00 f1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 (libmsg_msgmon.c:306) //146136"        

def parseLine(line, direction):
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
                return
            
            srcProcess = private_data.process_map[int(msgData[22], 16)]
            srcInstance = int(msgData[23], 16)
            srcNode = getNGName(int(msgData[24], 16), int(msgData[25], 16), int(msgData[26], 16), int(msgData[27], 16))
            dstProcess = private_data.process_map[int(msgData[28], 16)]
            dstInstance = int(msgData[29], 16)
            dstNode = getNGName(int(msgData[30], 16), int(msgData[31], 16), int(msgData[32], 16), int(msgData[33], 16))

            srcPid = 0
            if "CLA" in srcNode:
                platform = "LittleEndian"
            else:
                platform = "BigEndian"
            srcPid = getPid(platform, msgData[35], msgData[36])
            
            
            if not isNeedTrace(srcProcess, dstProcess):
                return

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
                if item and item.dstPid == 0 :
                    item.dstPid = re.findall(r'\[(\d+)\]', tmpArr[5])[0]  # tmpArr[5] is such as "Session_Ctrl_1[1111]:


def collectMsg(fileName, direction):            
    fp = open(fileName, "r");
    for line in fp.readlines():
        parseLine(line, direction)
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

            
