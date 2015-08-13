#!/usr/bin/python 

import re
import os
import json
import datetime

import private_data

# processInfo should be key: Node, value [(process , [process instance]), ...]
processesInfo = {}
# msgTypesInfo : key: msgType, value: (srcProcess, dstProcess)
msgTypesInfo = {}
# availableDates : key: date_string(eg. 2015-8-13), value: True
availableDates = {}
# availableTimes : key: time_string(eg. 01:02:03), value: True
availableTimes = {}


processPairArray = []  # collect all out message, each node is messageItem

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
                'Dec': 12, }


class messageItem:
    def __init__(self, timestamp, msgType, msgData, msgString, line):
        self.timestamp = timestamp
        self.msgType = msgType
        self.msgString = msgString
        self.msgData = msgData
        self.line = line

    
# processPairMessage, store IPC_OUT messages for one process pair(srcProcess->dstProcess)
class processPair:
    def __init__(self, srcNode, src, srcInstance, srcPid, dstNode, dst, dstInstance, dstPid):
        self.src = src
        self.srcInstance = srcInstance
        self.srcPid = srcPid
        self.dst = dst
        self.dstInstance = dstInstance
        self.srcNode = srcNode
        self.dstNode = dstNode
        self.dstPid = dstPid
        self.msgDataList = []

    def appendMsgDataList(self, msgItem):
        self.msgDataList.append(msgItem)
    

def findProcessPair(srcNode, src, srcInstance, srcPid, dstNode, dst, dstInstance, dstPid):
    for tmp in processPairArray:
        if tmp.srcNode == srcNode and tmp.src == src and tmp.dst == dst and tmp.srcInstance == srcInstance \
        and tmp.dstNode == dstNode and tmp.dstInstance == dstInstance and tmp.srcPid == srcPid and tmp.dstPid == dstPid:
            return tmp
    return None

def getNodeName(node, num):
    if node == 0:  # 0 mean AS_NODE
        return private_data.as_map[num]
    elif node == 1:
        return private_data.se_map[num]
    elif node == 2:  # 2 mean CLA NODE
        return private_data.cla_map[num]
    elif node == 3:
        return private_data.ib_map[num]
    elif node == 4:  # 4 SAB
        return private_data.sab_map[num]
    else:
        return "UNKNOWN"
    
# the server name actually is RG's name, so did not know which active node will be send
# so set the server name as unknown, it will be assign after analysis IPC_IN message.  
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
    

# ALL IPC_OUT message type will convert to big endian, and all IPC_IN message type will convert to according order
def getMsgTypePlatform(direction, nodeName):
    if direction == "IPC_OUT":
        return "BigEndian"
    else:
        return getSrcPlatform(nodeName)
        
        
def lineToDatetime(line):
    tmpArr = re.split(r' +', line);
    year = 2015
    month = month2num[tmpArr[0]]
    day = int(tmpArr[1])

    hour = int(tmpArr[2].split(':')[0])
    minute = int(tmpArr[2].split(':')[1])
    second = int(tmpArr[2].split(':')[2].split('.')[0])
    microsecond = int(tmpArr[2].split(':')[2].split('.')[1])

    return datetime.datetime(year, month, day, hour, minute, second, microsecond)

def getMsgTypeColor(msgType):
    if msgType in private_data.msgTypeDict:
        return private_data.msgTypeDict[msgType]['color']
    return private_data.unknownMsgColor

def getMsgString(msgType):
    if msgType in private_data.msgTypeDict:
        return private_data.msgTypeDict[msgType]['name']
    return 'unknown_msg(%d)' % msgType
   
def parseLine(line):
    global in_line, out_line
    msgLine = re.search("LIBMSG: MMON", line)
    if msgLine:     
        tmpArr = re.split(r' +', line);
        msgInfo = re.split(r";", tmpArr[8])  # tmpArr[8] is LIB MSG information
        fragmentFlag = msgInfo[2]  # get fragment flag, 1/1 mean no fragment, 1/3 mean the first one of 3 fragment
        msgDirection = msgInfo[3]  # get MSG direction IPC_OUT/IPC_IN
        msgInNode = tmpArr[4]   
           
        matchObj = re.search(r'([0-9A-Fa-f]{2} ){2,}', line);  # get MSG content
        if matchObj:
            msgData = re.split(r' ', matchObj.group())

            if  int(re.split(r'/', fragmentFlag)[0] ) != 1:
                #ignore others segments
                return
            
            srcProcess = private_data.process_map[int(msgData[22], 16)]
            dstProcess = private_data.process_map[int(msgData[28], 16)]
            srcInstance = getProcessInstance(msgData[23])
            dstInstance = getProcessInstance(msgData[29])
            srcNode = getNGName(int(msgData[24], 16), int(msgData[25], 16), int(msgData[26], 16), int(msgData[27], 16))
#             dstNode = getNGName(int(msgData[30], 16), int(msgData[31], 16), int(msgData[32], 16), int(msgData[33], 16))
            dstNode = msgInNode
            srcPid = hexToInt(getSrcPlatform(srcNode), msgData[35], msgData[36])
            dstPid = re.findall(r'\[(\d+)\]', tmpArr[5])[0]  # tmpArr[5] is such as "Session_Ctrl_1[1111]:
            msgType = hexToInt(getMsgTypePlatform(msgDirection, msgInNode), msgData[20], msgData[21])
            msgTypeString = getMsgString(msgType)
            msgDateTime = lineToDatetime(line)
            availableDates[msgDateTime.date().isoformat()] = True
            availableTimes[msgDateTime.time().strftime("%H:%M.%S")] = True
                        
            pairItem = findProcessPair(srcNode, srcProcess, srcInstance, srcPid, dstNode, dstProcess, dstInstance, dstPid)
            if msgDirection == "IPC_IN":
                if not pairItem:  # new IN message
                    pairItem = processPair(srcNode, srcProcess, srcInstance, srcPid, dstNode, dstProcess, dstInstance, dstPid)
                    processPairArray.append(pairItem)
                 
                message = messageItem(msgDateTime, msgType, msgData, msgTypeString, line)
                pairItem.appendMsgDataList(message)
                collectMsgTypesInfo(msgTypeString, srcProcess, dstProcess)  
                
def parseFile(fileName):            
    fp = open(fileName, "r");
    for line in fp.readlines():
        parseLine(line)
    fp.close()

def parseFiles(directroy):
    for root, _, files in os.walk(directroy):
        for logFile in files:
            matchObj = re.search(r"log$", logFile)    
            if matchObj:
                parseFile(root + "\\" + logFile)
                
def getALLProcessesInfo():
    for item in processPairArray:
        collectProcessesInfo(item.srcNode, item.src, item.srcInstance)
        collectProcessesInfo(item.dstNode, item.dst, item.dstInstance)
            

def parseNGLog(directroy):
    parseFiles(directroy)
    if len(processPairArray) != 0:
        getALLProcessesInfo()

    processJson = json.dumps(processesInfo)
    msgTypeJson = json.dumps(msgTypesInfo)
    datesJson = json.dumps(sorted(availableDates.keys()))
    timesJson = json.dumps(sorted(availableTimes.keys()))
    
    return processJson, msgTypeJson, datesJson, timesJson



