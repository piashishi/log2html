#!/usr/bin/python 

import parseLog

filterData = []
filterProcesses = []

def filterMsg(rules):
    print rules
    for rule in rules:
        print rule
        srcNode = rule[0]
        srcProcess = rule[1]
        srcInstance = rule[2]
        dstNode = rule[3]
        dstProcess = rule[4]
        dstInstance = rule[5]
        msgType = rule[6]
        
        for pair in parseLog.processPairArray:
            if pair.src != srcProcess or pair.srcNode != srcNode or \
                pair.srcInstance != srcInstance or pair.dst != dstProcess or \
                pair.dstNode != dstNode or pair.dstInstance != dstInstance:
                continue
            filterData.src = pair.src
            filterData.srcNode = pair.srcNode
            filterData.srcInstance = pair.srcInstance
            filterData.dst = pair.dst
            filterData.dstNode = pair.dstNode
            filterData.dstInstance = pair.dstInstance
            
            if srcProcess not in filterProcesses:
                filterProcesses.append(srcProcess)
            if dstProcess not in filterProcesses:
                filterProcesses.append(dstProcess)
            
            for msgData in pair.msgDataList:
                if msgData.msgString in msgType:
                    filterData.msgDataList.append(msgData)
                
    
