  var dataList = [];
    var nodeList = [];
    var instanceList = [];
    var msgType 
    dataList[0] = {
        t: 'Choose Process...',
        v: "0"
    };
    nodeList[0] = {
        t: 'Choose Node...',
        v: "0"
    };
    instanceList[0] = {
        t: 'Choose Instance...',
        v: "0"
    };

    $(document).ready(function() {
    	
    		$.getJSON('msgTypes.json',
        function(json) {
        	msgType = json
        })
        	
        	
        $.getJSON('nodes.json',
        function(json) {
            var node_index = 0
            var process_index = 0
            for (var node in json) {
            	  node_index += 1
								var nodeInfo = {
									t: node,
									v: node_index
								}
								nodeList[node_index] = nodeInfo
                var processesInfo = json[node];

                var processList = new Array();
                for (var i = 0; i < processesInfo.length; i++) {
                		process_index += 1
                    var process = {
                        t: processesInfo[i][0],
                        v: process_index
                    }
                    processList[i] = process;
                    instanceArray = processesInfo[i][1] 
                    instanceArray[instanceArray.length] = 'ALL'
										instanceList[process_index] = instanceArray   
                }
                dataList[node_index] = processList
            }
            addNodeOptions('node_1', 'node_2')
        })
    })


    function addNodeOptions(id1, id2) {
        var s_node = document.getElementById(id1), arr = nodeList; 
        var r_node = document.getElementById(id2)
        
        s_node.options.length = 0; 
        r_node.options.length = 0;
        for (var i = 0, j = arr.length; i < j; i++) {
        	  r_node.options.add(new Option(arr[i].t, arr[i].v));
            s_node.options.add(new Option(arr[i].t, arr[i].v));

        }

        addProcessOptions(0, id1)
        addProcessOptions(0, id2)
    }
    
    function addProcessOptions(v, nodeID) {
    		var processId = nodeID.replace("node","process")
        var process = document.getElementById(processId), arr = dataList[v]; 
        process.options.length = 0; 
        if (v == 0)
        {
        	process.options.add(new Option(arr.t, arr.v));
        	addInstanceOptions(v, processId)
        }
        else {
        	for (var i = 0, j = arr.length; i < j; i++) {
            	process.options.add(new Option(arr[i].t, arr[i].v));
        	}
        	//as default the first will be shown
        	addInstanceOptions(arr[0].v, processId)
      	}

    }
    
		function addInstanceOptions(v, processID) {
				var instanceId = processID.replace("process","instance")
        var instance = document.getElementById(instanceId), arr = instanceList[v];
        instance.options.length = 0; 
        if (v == 0)
        {
        	instance.options.add(new Option(arr.t, arr.v));
        }
        else {
        	for (var i = 0, j = arr.length; i < j; i++) {
            	instance.options.add(new Option(arr[i], arr[i]));
        	}
      	}
      	addMsgTypeCheckBoxes(processID)
    } 
    
  	function addMsgTypeCheckBoxes(processID) {
  		var num = Number(processID.match(/\d/g)[0])
  		if (num % 2) { //odd , processID is sender process
  			num += 1
  		} 
  		else{
  			num -= 1        //processID is receiver process
  		}
  		var others = processID.replace(/\d/g, num);
  		var process1= document.getElementById(processID)
  		var process2 = document.getElementById(others)  			
  		var list=document.getElementById("listID")
  		var tmp1 = process1.options[process1.selectedIndex].text
  		var tmp2 = process2.options[process2.selectedIndex].text
  		list.innerHTML=""; //clear all li

  		if(tmp1 != "Choose Process..." && tmp2 != "Choose Process...")
  		{
  			for (var key in  msgType) {
  				if ( (msgType[key][0] == tmp1 && msgType[key][1] == tmp2) || 
  						(msgType[key][0] == tmp2 && msgType[key][1] == tmp1)) {
  						var obj = document.createElement('input');
							obj.type="checkbox";
							obj.value = key
							var li=document.createElement("li");
        			li.appendChild(obj);        
        			li.appendChild(document.createTextNode(key));
        			list.appendChild(li)
  				}
  			}
  		}
  	}