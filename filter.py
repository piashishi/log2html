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

        start_date, start_time, end_date, end_time = ruleToDateAndTime(rule);

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
                        log_date = datetime.date(msgData.timestamp.year, msgData.timestamp.month, msgData.timestamp.day)
                        log_time = datetime.time(msgData.timestamp.hour, msgData.timestamp.minute, msgData.timestamp.second, msgData.timestamp.microsecond)
                        if start_date <= log_date <= end_date and start_time <= log_time <= end_time:
                            filterPair.msgDataList.append(msgData)
                            
                filterData.append(filterPair)  
     
def ruleToDateAndTime(rule):
    start_date_input, start_time_input, start_time_s_input = rule[7] , rule[8] , rule[9]
    end_date_input  , end_time_input  , end_time_s_input   = rule[10], rule[11], rule[12]

    if start_date_input == '':
        start_date_input = '1970-01-01'

    if start_time_input == '':
        start_time_input = '00:00'
        
    if end_date_input == '':
        end_date_input = '2038-01-18'

    if end_time_input == '':
        end_time_input = '23:59'

    start_date, start_time = inputToDateAndTime(start_date_input, start_time_input, start_time_s_input, '000000')
    end_date  , end_time   = inputToDateAndTime(end_date_input  , end_time_input  , end_time_s_input  , '999999')

    return start_date, start_time, end_date, end_time


def inputToDateAndTime(date_input, time_imput, time_s_input, time_ms_input):
    date_y = int(date_input.split('-')[0])
    date_m = int(date_input.split('-')[1])
    date_d = int(date_input.split('-')[2])

    time_h = int(time_imput.split(':')[0])
    time_m = int(time_imput.split(':')[1])

    the_date = datetime.date(date_y, date_m, date_d)
    the_time = datetime.time(time_h, time_m, int(time_s_input), int(time_ms_input))

    return the_date, the_time


    
#         debugErr()   
                    
def  debugErr():
    for pair in filterData:
        for lines in pair.msgDataList:
            print lines.line
            
            
                
    
