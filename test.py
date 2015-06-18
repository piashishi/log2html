#!/usr/bin/python 
import re

import private_data

def getNodeName(node, num):
    if node == 0:
        return private_data.as_map[num]
    if node == 2:
        return private_data.cla_map[num]
    
def getServerName(server, num):
    return "CLA?"

def getNGName(node, node_num, server, ser_num):
    if node == 0xff:
        return getServerName(server, ser_num)
    else:
        return getNodeName(node, node_num)
   
    
process=[]
msg_direction = ""

process_pair = [["TRACE_CTRL", "TRACE_PROXY"], ["TRACE_PROXY", "SC"]]

src_process = ["TRACE_CTRL", "TRACE_PROXY"]
dst_process = ["TRACE_PROXY", "SC"]

#not finished
def isTrace(src, dst):
    for pair in process_pair:
        if pair[0] == src and pair[1] == dst:
            return True
    return False
            

fp = open("raw.log", "r");
for line in fp.readlines():
    matchObj =  re.search("LIBMSG: MMON", line)
    if matchObj:     
        tmpArr = re.split(r' +', line);
        arr2 = re.split(r";", tmpArr[8])    #tmpArr[8] is LIB MSG information
        if arr2[2] != "1/1": #no fragment
            continue
        msg_direction = arr2[3]        #IPC_IN or IPC_OUT
        if not tmpArr[5] in process:
            process.append(tmpArr[5])
        matchObj = re.search(r'([0-9A-Fa-f]{2} ){2,}', line);
        if matchObj:
            tmpArr = re.split(r' ',matchObj.group())
            if len(tmpArr) > 31 and msg_direction == "IPC_IN" :
                print "SRC:",
                print getNGName(int(tmpArr[24], 16), int(tmpArr[25], 16),int(tmpArr[26], 16),int(tmpArr[27], 16)), private_data.process_map[int(tmpArr[22], 16)], tmpArr[23],
                print "----->",  
                print "DST:",
                print getNGName(int(tmpArr[30], 16), int(tmpArr[31], 16), int(tmpArr[32], 16),int(tmpArr[33], 16)), private_data.process_map[int(tmpArr[28], 16)], tmpArr[29]
fp.close()
print process
            
