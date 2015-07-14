#!/usr/bin/python 

import re
import os
import datetime

import private_data

processPairArray=[]  #collect all out message, each node is messageItem

processPairNeedProcess = [["TRACE_CTRL", "TRACE_PROXY"], ["TRACE_PROXY", "SC"]]
   
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
        self.outMsg = []
        self.dstPid = 0
        
    def appendOutMsg(self, data):
        self.outMsg.append(data)
    
    #In IPC_OUT message, the dst could be RG, so need replace it with Node name
    def setDstNode(self, realNode):
        self.dstNode = realNode
        
    def setDstPid(self,pid):
        self.dstPid = pid

def get_msg_str(msg_str):
    tmp = msg_str.split(';')
    return tmp[-1].split('...')[0].split('(')[0]

class FragmentMsgProcessor(object):
    """ """
    def __init__(self):
        super(FragmentMsgProcessor, self).__init__()
        self.msgs = {}
        self.seq_nums = {}
        self.msg_directions = {}

    def cache_msg(self, key, msg):
        tmpArr = re.split(r' +', msg);
        seq = tmpArr[8].split(";")[2] # seq = '1/2'

        if not self.seq_nums.has_key(key):
            self.msgs[key] = ''
            self.seq_nums[key] = 0
            self.msg_directions[key] = tmpArr[8].split(";")[3] # IPC_OUT/IPC_IN

        seq_num, seq_total = int(seq.split('/')[0]), int(seq.split('/')[1])

        if seq_num == self.seq_nums[key] + 1:
            self.msgs[key] = self.msgs[key] + get_msg_str(msg)
            self.seq_nums[key] = seq_num

        if seq_num  == seq_total:
            ret_msg = self.msgs[key]
            ret_msg_dirction = self.msg_directions[key]
            self.msgs.pop(key)
            self.seq_nums.pop(key)
            self.msg_directions.pop(key)
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

def msg_type_to_name(process_type, msg_type):
    msg_name = 'unknown_message'
    if process_type in private_data.msg_dic:
        if msg_type in private_data.msg_dic[process_type]:
            msg_name = private_data.msg_dic[process_type][msg_type] 

    return msg_name +'(' + str(msg_type) + ')'

def line_to_process_type(line):
    tmp = re.split(r' +', line);
    process_type = tmp[5].split('[')[0]
    return process_type

def is_little_endian(msgData):
    assert(msgData[0] == '00' or msgData[0] == '03')
    return msgData[0] == '03'

def msg_data_to_msg_type(msgData):
    msg_type_hex = ''
    if is_little_endian(msgData):
        msg_type_hex = msgData[21] + msgData[20]
    else:
        msg_type_hex = msgData[20] + msgData[21]
    msg_type = int(msg_type_hex, 16)
    return msg_type

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
            srcPid = getPid(checkPlatform(srcNode), msgData[35], msgData[36])

            pairItem = findProcessPair(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
            if msgDirection == direction and direction == "IPC_OUT":
                if not pairItem:    #new OUT message
                    pairItem = processPair(srcNode, srcProcess, srcInstance, dstNode, dstProcess, dstInstance, srcPid)
                    processPairArray.append(pairItem)

                process_type = line_to_process_type(line)
                msg_type = msg_data_to_msg_type(msgData)
                msg_type_name = msg_type_to_name(process_type, msg_type)
                message = messageItem(lineToDatetime(line), msg_type_name, msgData)
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



            
