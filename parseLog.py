#!/usr/bin/python 

import re
import os

import private_data

processPairArray=[]  #collect all out message, each node is messageItem

processPairNeedProcess = [["TRACE_CTRL", "TRACE_PROXY"], ["TRACE_PROXY", "SC"]]
   
class messageItem:
    def __init__(self, timestamp, msgType, msgData):
        self.timestamp = timestamp
        self.msgType = msgType
        self.msgData = msgData
    
#processPairMessage, store IPC_OUT messages for one process pair(srcProcess->dstProcess)
class processPair:
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
    
    #In IPC_OUT message, the dst could be RG, so need replace it with Node name
    def setDstNode(self, realNode):
        self.dstNode = realNode
        
    def setDstPid(self,pid):
        self.dstPid = pid
    
def findProcessPair(srcNode, src, srcInstance, dstNode, dst, dstInstance, senderPid):
    for tmp in processPairArray:
        if tmp.srcNode == srcNode and tmp.src ==src and tmp.dst == dst and tmp.srcInstance == srcInstance \
        and tmp.dstNode == dstNode and tmp.dstInstance ==dstInstance and tmp.srcPid == senderPid:
            return tmp
    return None


def appendFragmentMsg(line):
    return

def isNeedTrace(src, dst):
    for pair in processPairNeedProcess:
        if (pair[0] == src and pair[1] == dst) or (pair[0] == dst and pair[1] == src):
            return True
    return False

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
    
def getPid(platform, lowByte, highByte):
    pid = 0
    if platform == "LittleEndian":
        pid = int(highByte + lowByte, 16) 
    else:
        pid = int(lowByte + highByte, 16)
    return pid

def getProcessInstance(value):
    return int(value, 16)


def checkPlatform(nodeName):
    if "CLA" in nodeName:
        return "LittleEndian"
    else:
        return "BigEndian"
    

#testline = "Jun 18 08:24:53.469097 debug AS7-0 trace_proxy[4618]: [0]: LIBMSG: MMON;28078;1/1;IPC_IN;2D00_000A_FFFF_120A<0800_0201_0400_1724;290979;0; 00 03 00 00 00 00 27 0f 00 00 27 0f 00 00 27 0f 00 00 27 0f 0b 09 08 00 02 01 04 00 2d 00 00 0a ff ff 00 17 24 27 00 00 00 00 81 42 00 08 00 00 00 00 f1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 (libmsg_msgmon.c:306) //146136"        

def parseLine(line, direction):
    msgLine = re.search("LIBMSG: MMON", line)
    if msgLine:     
        tmpArr = re.split(r' +', line);
        msgInfo = re.split(r";", tmpArr[8])  # tmpArr[8] is LIB MSG information
        fragmentFlag = msgInfo[2]  # get fragment flag, 1/1 mean no fragment, 1/3 mean the first one of 3 fragment
        msgDirection = msgInfo[3]  # get MSG direction IPC_OUT/IPC_IN
           
        matchObj = re.search(r'([0-9A-Fa-f]{2} ){2,}', line); #get MSG content
        if matchObj:
            msgData = re.split(r' ', matchObj.group())
                
            if fragmentFlag != "1/1":
                appendFragmentMsg(msgData)
                return
            
            srcProcess = private_data.process_map[int(msgData[22], 16)]
            dstProcess = private_data.process_map[int(msgData[28], 16)]
                             
            if not isNeedTrace(srcProcess, dstProcess):
                return
            
            srcInstance = getProcessInstance(msgData[23])
            dstInstance = getProcessInstance(msgData[29])
            srcNode = getNGName(int(msgData[24], 16), int(msgData[25], 16), int(msgData[26], 16), int(msgData[27], 16))
            dstNode = getNGName(int(msgData[30], 16), int(msgData[31], 16), int(msgData[32], 16), int(msgData[33], 16))
            srcPid = getPid(checkPlatform(srcNode), msgData[35], msgData[36])

            pairItem = findProcessPair(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
            if msgDirection == direction and direction == "IPC_OUT":
                if not pairItem:    #new OUT message
                    pairItem = processPair(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
                    processPairArray.append(pairItem)
                message = messageItem("12345555", "TRACE_TYPE_INFO_LOG", msgData)
                pairItem.appendOutMsg(message)
            elif msgDirection == direction and direction == "IPC_IN" and pairItem:
                if pairItem.dstNode == "CLA-Unknown":
                    pairItem.setDstNode(tmpArr[4])
                if pairItem.dstPid == 0 :
                    pairItem.setDstPid(re.findall(r'\[(\d+)\]', tmpArr[5])[0])  # tmpArr[5] is such as "Session_Ctrl_1[1111]:

def parseFile(fileName, direction):            
    fp = open(fileName, "r");
    for line in fp.readlines():
        parseLine(line, direction)
    fp.close()

def parseFiles(directroy, direction):
    for root, dirs,files in os.walk(directroy):
        for logFile in files:
            matchObj = re.search(r"log$", logFile)    
            if matchObj:
                parseFile(root + "\\" + logFile, direction)

def parseNGLog(directroy):
    parseFiles(directroy, "IPC_OUT")
    parseFiles(directroy, "IPC_IN")
    
    
parseNGLog("log")



            
