#!/usr/bin/python 

import parseLog

filterData = []
filterProcesses = []

def checkInstance(rule, value):
    if rule == "ALL":
        return True
    if int(rule) == value:
        return True
    return False

def filterMsg(rules):
    global filterData
    global filterProcesses 
    filterData = []
    filterProcesses = []
    for rule in rules:
        srcNode = rule[0]
        srcProcess = rule[1]
        srcInstance = rule[2]
        dstNode = rule[3]
        dstProcess = rule[4]
        dstInstance = rule[5]
        msgType = rule[6]
        
        for pair in parseLog.processPairArray:
            if (pair.src == srcProcess  and  pair.srcNode == srcNode and \
                 checkInstance(srcInstance, pair.srcInstance)  and  pair.dst == dstProcess and \
                 pair.dstNode == dstNode and checkInstance(dstInstance, pair.dstInstance)) \
                 or ( \
                pair.src == dstProcess and  pair.srcNode == dstNode and \
                checkInstance(dstInstance, pair.srcInstance) and  pair.dst == srcProcess  and \
                pair.dstNode == srcNode and   checkInstance(srcInstance, pair.dstInstance)):
            
                filterPair = parseLog.processPair(pair.srcNode, pair.src, pair.srcInstance,  pair.srcPid ,\
                                                                        pair.dstNode, pair.dst, pair.dstInstance,  pair.dstPid)
            
                if srcProcess not in filterProcesses:
                    filterProcesses.append(srcProcess)
                if dstProcess not in filterProcesses:
                    filterProcesses.append(dstProcess)
                    
                for msgData in pair.msgDataList:
                    if msgData.msgString in msgType:
                        filterPair.msgDataList.append(msgData)
                filterData.append(filterPair)   
#         debugErr()   
                    
def  debugErr():
    for pair in filterData:
        for lines in pair.msgDataList:
            print lines.line
            
            
                
    
