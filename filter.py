#!/usr/bin/python 

import parseLog

filterData = []
filterProcesses = []

def filterMsg(rules):
    for rule in rules:
        srcNode = rule[0]
        srcProcess = rule[1]
        srcInstance = int(rule[2])
        dstNode = rule[3]
        dstProcess = rule[4]
        dstInstance = int(rule[5])
        msgType = rule[6]
        
        for pair in parseLog.processPairArray:
            if (pair.src != srcProcess or pair.srcNode != srcNode or \
                pair.srcInstance != srcInstance or pair.dst != dstProcess or \
                pair.dstNode != dstNode or pair.dstInstance != dstInstance ) \
                and ( \
                pair.src != dstProcess or pair.srcNode != dstNode or \
                pair.srcInstance != dstInstance or pair.dst != srcProcess or \
                pair.dstNode != srcNode or pair.dstInstance != srcInstance ):
                continue
            
            filterPair = parseLog.processPair(pair.srcNode, pair.src, pair.srcInstance, \
                                                                        pair.dstNode, pair.dst, pair.dstInstance,  pair.srcPid)
            filterPair.dstPid = pair.dstPid
            
            if srcProcess not in filterProcesses:
                filterProcesses.append(srcProcess)
            if dstProcess not in filterProcesses:
                filterProcesses.append(dstProcess)
            
            for msgData in pair.msgDataList:
                if msgData.msgString in msgType:
                    filterPair.msgDataList.append(msgData)
            filterData.append(filterPair)   
                    
def  debugErr():
    for pair in filterData:
        for lines in pair.msgDataList:
            print lines.line
            
            
                
    
