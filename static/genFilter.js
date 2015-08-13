var processList = [];
var nodeList = [];
var instanceList = [];
var msgTypeJson

processList[0] = {
    t : 'Processes...',
    v : "0"
};
nodeList[0] = {
    t : 'Nodes...',
    v : "0"
};
instanceList[0] = {
    t : 'Instances...',
    v : "0"
};

function parseNodeInfo(nodeinfoJson) {
    var node_index = 0
    var process_index = 0
    for ( var node in nodeinfoJson) {
        node_index += 1
        var nodeInfo = {
            t : node,
            v : node_index
        }
        nodeList[node_index] = nodeInfo
        var processesInfo = nodeinfoJson[node];

        var processArray = new Array();
        for ( var i = 0; i < processesInfo.length; i++) {
            process_index += 1
            var process = {
                t : processesInfo[i][0],
                v : process_index
            }
            processArray[i] = process;
            var instanceArray = processesInfo[i][1]
            instanceArray[instanceArray.length] = 'ALL'
            instanceList[process_index] = instanceArray
        }
        processList[node_index] = processArray
    }
}

function getNextSelect(obj) {
    while (obj.nextSibling) {
        obj = obj.nextSibling
        if (obj.tagName == "SELECT") {
            return obj
        }
    }
}

function addNodeOptions(divId) {
    var arr = nodeList;
    var srcNode = $("#" + divId).children("select.srcNode")[0]
    var dstNode = $("#" + divId).children("select.dstNode")[0]

    srcNode.options.length = 0
    dstNode.options.length = 0
    for ( var i = 0, j = arr.length; i < j; i++) {
        srcNode.options.add(new Option(arr[i].t, arr[i].v));
        dstNode.options.add(new Option(arr[i].t, arr[i].v));
    }

    addProcessOptions(0, srcNode)
    addProcessOptions(0, dstNode)
}

function addProcessOptions(v, node) {
    var arr = processList[v];
    var process = getNextSelect(node)
    process.options.length = 0
    if (v == 0) {
        process.options.add(new Option(arr.t, arr.v));
        addInstanceOptions(v, process)
    } else {
        for ( var i = 0, j = arr.length; i < j; i++) {
            process.options.add(new Option(arr[i].t, arr[i].v));
        }
        // as default the first will be shown
        addInstanceOptions(arr[0].v, process)
    }
}

function addInstanceOptions(v, process) {
    var arr = instanceList[v];
    var instance = getNextSelect(process)
    instance.options.length = 0;

    if (v == 0) {
        instance.options.add(new Option(arr.t, arr.v));
    } else {
        for ( var i = 0, j = arr.length; i < j; i++) {
            instance.options.add(new Option(arr[i], arr[i]));
        }
    }
    addMsgTypeCheckBoxes(process.parentNode.id)
}

function addMsgTypeCheckBoxes(divID) {
    var process1 = $("#" + divID).children("select.srcProcess")[0]
    var process2 = $("#" + divID).children("select.dstProcess")[0]

    if (process1.options.length > 0 && process2.options.length > 0) {
        var list = $("#" + divID).find("ul.listID")[0]
        var pText1 = process1.options[process1.selectedIndex].text
        var pText2 = process2.options[process2.selectedIndex].text
        list.innerHTML = ""; // clear all li

        if (pText1 != "Processes..." && pText2 != "Processes...") {
            for ( var key in msgTypeJson) {
                if ((msgTypeJson[key][0] == pText1 && msgTypeJson[key][1] == pText2)
                        || (msgTypeJson[key][0] == pText2 && msgTypeJson[key][1] == pText1)) {
                    var obj = document.createElement('input');
                    obj.type = "checkbox";
                    obj.value = key
                    obj.checked = true
                    var li = document.createElement("li");
                    li.appendChild(obj);
                    var msg_span = document.createElement('span');
                    msg_span.setAttribute("class", "messageType")
                    var text = document.createTextNode(key)
                    msg_span.appendChild(text)
                    li.appendChild(msg_span);
                    list.appendChild(li)
                }
            }
        }
    }
}

function addOptions(selectName, OptionList) {
    for ( var i = 0; i < OptionList.length; i++) {
        $(selectName).append($('<option>', {value:OptionList[i], text:OptionList[i]}));
    }
}

function getFilter() {
    var count = $(".srcNode").size();
    var filter_array = []
    for ( var i = 0; i < count; i++) {
        var filter = []
        var srcNode = $(".srcNode").eq(i).find("option:selected").text();
        var srcProcess = $(".srcProcess").eq(i).find("option:selected").text();
        var srcInstance = $(".srcInstance").eq(i).find("option:selected").text();
        var dstNode = $(".dstNode").eq(i).find("option:selected").text();
        var dstProcess = $(".dstProcess").eq(i).find("option:selected").text();
        var dstInstance = $(".dstInstance").eq(i).find("option:selected").text();
        
        var start_date = $("#start_date").val();
        var start_time = $("#start_time").val();
        
        var end_date = $("#end_date").val();
        var end_time = $("#end_time").val();
        
        var msgType = []

        var msgTypeDiv = $("ul.listID").eq(i).find("input[type='checkbox']").each(function() {
            if ($(this).is(':checked')) {
                msgType.push($(this).val())
            }
        })
        filter.push(srcNode)
        filter.push(srcProcess)
        filter.push(srcInstance)
        filter.push(dstNode)
        filter.push(dstProcess)
        filter.push(dstInstance)
        filter.push(msgType)
        
        filter.push(start_date)
        filter.push(start_time)
        
        filter.push(end_date)
        filter.push(end_time)
        
        filter_array.push(filter)
    }
    return filter_array;
}
