#!/usr/bin/python 

import re
import os
import json
import datetime

import private_data

#processInfo should be key: Node, value [(process , [process instance]), ...]
processesInfo = {}
#msgTypesInfo : key: msgType, value: (srcProcess, dstProcess)
msgTypesInfo = {}

processPairArray=[]  #collect all out message, each node is messageItem

def collectProcessesInfo(node, process, processInstance):

    if node in processesInfo.keys():
        processFound = False
        processInfoList = processesInfo[node]
        for processInfo in processInfoList:
            if process == processInfo[0]:
                processFound = True
                if not processInstance in processInfo[1]:
                    processInfo[1].append(processInstance)
                break
        if not processFound:
            newProcessInfo = (process, [])
            newProcessInfo[1].append(processInstance)
            processInfoList.append(newProcessInfo)
    else:
        newProcessInfo = (process, [])
        newProcessInfo[1].append(processInstance)
        processList = []
        processList.append(newProcessInfo)
        processesInfo[node] = processList
        

def collectMsgTypesInfo(msgType, srcProcess, dstProcess):        
    if not msgType in msgTypesInfo.keys():
        msgTypesInfo[msgType] = (srcProcess, dstProcess)
            
        
processPairNeedProcess = [["TRACE_CTRL", "TRACE_PROXY"], ["TRACE_PROXY", "SC"]]
#processPairNeedProcess = [["TRACE_CTRL", "TRACE_PROXY"]]
   
month2num = {   'Jan': 1,
                'Feb': 2,
                'Mar': 3,
                'Apr': 4,
                'May': 5,
                'Jun': 6,
                'Jul': 7,
                'Aug': 8,
                'Sep': 9,
                'Oct': 10,
                'Nov': 11,
                'Dec': 12,}


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
        self.dstPid = 0
        self.msgDataList = []

        
    def appendMsgDataList(self, msgItem):
        self.msgDataList.append(msgItem)
    
    #In IPC_OUT message, the dst could be RG, so need replace it with Node name
    def setDstNode(self, realNode):
        self.dstNode = realNode
        
    def setDstPid(self,pid):
        self.dstPid = pid

def get_msg_str(msg_str):
    tmp = msg_str.split(';')
    return tmp[-1].split('...')[0].split('(')[0]

class FragmentMsgProcessor(object):
    def __init__(self):
        self.msg_infos = {}

    def cache_msg(self, key, msg):
        tmpArr = re.split(r' +', msg);
        seq = tmpArr[8].split(";")[2] # seq = '1/2'

        if not self.msg_infos.has_key(key):
            self.msg_infos[key] = {'seq_num': 0 , 
                                   'msg'    : '', 
                                   'msg_direction': tmpArr[8].split(";")[3]} # IPC_OUT/IPC_IN

        seq_num, seq_total = int(seq.split('/')[0]), int(seq.split('/')[1])

        if seq_num == self.msg_infos[key]['seq_num'] + 1:
            self.msg_infos[key]['msg'] = self.msg_infos[key]['msg'] + get_msg_str(msg)
            self.msg_infos[key]['seq_num'] = seq_num

        if seq_num  == seq_total:
            ret_msg = self.msg_infos[key]['msg']
            ret_msg_dirction = self.msg_infos[key]['msg_direction']
            self.msg_infos.pop(key)
            return re.split(r' +', ret_msg)[1:], ret_msg_dirction
        else:
            return None, None

def findProcessPair(srcNode, src, srcInstance, dstNode, dst, dstInstance, senderPid):
    for tmp in processPairArray:
        if tmp.srcNode == srcNode and tmp.src ==src and tmp.dst == dst and tmp.srcInstance == srcInstance \
        and tmp.dstNode == dstNode and tmp.dstInstance ==dstInstance and tmp.srcPid == senderPid:
            return tmp
    return None

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
    
def hexToInt(platform, lowByte, highByte):
    pid = 0
    if platform == "LittleEndian":
        pid = int(highByte + lowByte, 16) 
    else:
        pid = int(lowByte + highByte, 16)
    return pid


def getProcessInstance(value):
    return int(value, 16)


def getSrcPlatform(srcNode):
    if "CLA" in srcNode:
        return "LittleEndian"
    else:
        return "BigEndian"
    

#ALL IPC_OUT message type will convert to big endian, and all IPC_IN message type will convert to according order
def getMsgTypePlatform(direction, nodeName):
    if direction == "IPC_OUT":
        return "BigEndian"
    else:
        return getSrcPlatform(nodeName)
        
        
def lineToDatetime(line):
    tmpArr = re.split(r' +', line);
    year  = 2015
    month =  month2num[tmpArr[0]]
    day   = int(tmpArr[1])

    hour        = int(tmpArr[2].split(':')[0])
    minute      = int(tmpArr[2].split(':')[1])
    second      = int(tmpArr[2].split(':')[2].split('.')[0])
    microsecond = int(tmpArr[2].split(':')[2].split('.')[1])

    return datetime.datetime(year, month, day, hour, minute, second, microsecond)

def msgTypeToNameAndColor(msgType):
    if msgType in private_data.msgTypeDict:
        return private_data.msgTypeDict[msgType]['name'], private_data.msgTypeDict[msgType]['color']

    return 'unknown_msg(%d)' % msgType, private_data.unknownMsgColor

#testline = "Jun 18 08:24:53.469097 debug AS7-0 trace_proxy[4618]: [0]: LIBMSG: MMON;28078;1/1;IPC_IN;2D00_000A_FFFF_120A<0800_0201_0400_1724;290979;0; 00 03 00 00 00 00 27 0f 00 00 27 0f 00 00 27 0f 00 00 27 0f 0b 09 08 00 02 01 04 00 2d 00 00 0a ff ff 00 17 24 27 00 00 00 00 81 42 00 08 00 00 00 00 f1 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 0f 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 (libmsg_msgmon.c:306) //146136"        

fragmentMsgProc = FragmentMsgProcessor() 

def parseLine(line, direction):
    msgLine = re.search("LIBMSG: MMON", line)
    if msgLine:     
        tmpArr = re.split(r' +', line);
        msgInfo = re.split(r";", tmpArr[8])  # tmpArr[8] is LIB MSG information
        msgKey = msgInfo[1] # msg ID
        fragmentFlag = msgInfo[2]  # get fragment flag, 1/1 mean no fragment, 1/3 mean the first one of 3 fragment
        msgDirection = msgInfo[3]  # get MSG direction IPC_OUT/IPC_IN
           
        matchObj = re.search(r'([0-9A-Fa-f]{2} ){2,}', line); #get MSG content
        if matchObj:
            msgData = re.split(r' ', matchObj.group())

            if fragmentFlag != "1/1":
                msgData, msgDirection = fragmentMsgProc.cache_msg(msgKey, line)
                if not msgData:
                    return
            
            srcProcess = private_data.process_map[int(msgData[22], 16)]
            dstProcess = private_data.process_map[int(msgData[28], 16)]
                             
            if not isNeedTrace(srcProcess, dstProcess): 
                return
            
            srcInstance = getProcessInstance(msgData[23])
            dstInstance = getProcessInstance(msgData[29])
            srcNode = getNGName(int(msgData[24], 16), int(msgData[25], 16), int(msgData[26], 16), int(msgData[27], 16))
            dstNode = getNGName(int(msgData[30], 16), int(msgData[31], 16), int(msgData[32], 16), int(msgData[33], 16))
            srcPid = hexToInt(getSrcPlatform(srcNode), msgData[35], msgData[36])
            
            realNode = tmpArr[4]   
            msgType = hexToInt(getMsgTypePlatform(msgDirection, realNode), msgData[20], msgData[21])
            msgTypeName, _ = msgTypeToNameAndColor(msgType)
            
            pairItem = findProcessPair(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
            if msgDirection == direction and direction == "IPC_OUT":
                if not pairItem:    #new OUT message
                    pairItem = processPair(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
                    processPairArray.append(pairItem)
                 
                message = messageItem(lineToDatetime(line), msgType, msgData)
                pairItem.appendMsgDataList(message)
                collectMsgTypesInfo(msgTypeName, srcProcess, dstProcess)  
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
    for root, _,files in os.walk(directroy):
        for logFile in files:
            matchObj = re.search(r"log$", logFile)    
            if matchObj:
                parseFile(root + "\\" + logFile, direction)
                
def getALLProcessesInfo():
    for item in processPairArray:
        collectProcessesInfo(item.srcNode, item.src, item.srcInstance)
        collectProcessesInfo(item.dstNode, item.dst, item.dstInstance)

def parseNGLog(directroy):
    parseFiles(directroy, "IPC_OUT")
    parseFiles(directroy, "IPC_IN")
    if len(processPairArray) != 0:
        getALLProcessesInfo()
    msgTypeJson = json.dumps(msgTypesInfo)
    processJson = json.dumps(processesInfo)
    return processJson, msgTypeJson
    




