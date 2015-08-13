#!/usr/bin/python 

import parseLog
import datetime

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

        start_datetime = inputToDatetime(rule[7], rule[8], '000000')
        end_datetime   = inputToDatetime(rule[9], rule[10], '999999')

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
                        if start_datetime <= msgData.timestamp <= end_datetime:
                            filterPair.msgDataList.append(msgData)
                            
                filterData.append(filterPair)  

def inputToDatetime(date_input, time_imput, time_ms_input):
    date_y = int(date_input.split('-')[0])
    date_m = int(date_input.split('-')[1])
    date_d = int(date_input.split('-')[2])

    time_h = int(time_imput.split(':')[0])
    time_m = int(time_imput.split(':')[1].split('.')[0])
    time_s = int(time_imput.split(':')[1].split('.')[1])

    the_datetime = datetime.datetime(date_y, date_m, date_d, time_h, time_m, time_s, int(time_ms_input))

    return the_datetime


    
#         debugErr()   
                    
def  debugErr():
    for pair in filterData:
        for lines in pair.msgDataList:
            print lines.line
            
            
                
    
