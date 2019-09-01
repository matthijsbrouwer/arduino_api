$(function() {
	
	var measurement_number = 5;
	var measurement_last = 0;
	
	/* update status demo periodically */
	function check_status(url, loop) {
		$.ajax({
			url : url,
			data : { "measurement_number": measurement_number, "measurement_last": measurement_last },
			success : function(data) {
				$("#demo_arduino").removeClass("btn-danger").addClass(
						"btn-light");
				set_status("demo_led1", data.led1);
				set_status("demo_led2", data.led2);
				set_status("demo_button1", data.button);
				set_status("demo_modus", data.modus);	
				set_sensor("demo_sensor1", "sensor1", data.measurements.last);
				$("button.demo_manual").prop("disabled", (data.modus == "AUTOMATIC"));				
				set_measurement(data.measurements);
				set_program(data.program);
				if (loop) {
					setTimeout(function() {
						check_status(url, true);
					}, 1000);
				}
			},
			error : function(error) {
				$("#demo_arduino").removeClass("btn-light").addClass(
						"btn-danger");
				$("#demo_led1 span.status").text("???");
				$("#demo_led2 span.status").text("???");
				$("#demo_button1 span.status").text("???");
				$("#demo_modus span.status").text("???");
				$("#demo_sensor1 span.value").text("???");
				$("#demo_sensor1 span.time").text("???");
				if (loop) {
					setTimeout(function() {
						check_status(url, true);
					}, 1000);
				}
			}
		});
	}
	//change status in demo
	function set_status(id, status) {
		$("#" + id + " span.status").text(status);
		if ((status == "ON") || (status == "AUTOMATIC")) {
			$("#" + id).removeClass("btn-danger").removeClass("btn-light")
					.addClass("btn-warning");
		} else if ((status == "OFF") || (status == "MANUAL")) {
			$("#" + id).removeClass("btn-danger").removeClass("btn-warning")
					.addClass("btn-light");
		} else {
			$("#" + id).removeClass("btn-warning").removeClass("btn-light")
					.addClass("btn-danger");
		}
	}
	//change sensor
	function set_sensor(id, name, last) {
		if (last && last.id) {
			measurement_last = last.id;
			if($("#"+id).data("id")!=last.id) {
				$("#"+id).data("id",last.id);
				$("#"+id).removeClass("btn-light").addClass("btn-warning");
			} else {
				$("#"+id).removeClass("btn-warning").addClass("btn-light");
			}					
			$("#"+id+" span.measurement").css("visibility", "visible");
			$("#"+id+" span.value").text(last[name]);
			$("#"+id+" span.time").text(last.time);
		} else {
			$("#"+id).data("id",0);
			$("#"+id+" span.measurement").css("visibility", "hidden");
			$("#"+id+" span.value").text("");
			$("#"+id+" span.time").text("");
		}		
	}
	//register measurement
	function set_measurement(measurements) {
		if(measurements.number>0) {
			$("#demo_measurement table").show();
		} else {
			$("#demo_measurement table").hide();
			$(".demo_measurement_number").text("");
		}
		$("#demo_measurement tbody tr[data-id]").filter(function() {
			return $(this).data("id")<measurements.min_id;
		}).remove();
		for(i=0;i<measurements.list.length;i++) {			
			if ($("#demo_measurement  tbody tr[data-id=" + measurements.list[i]["id"] + "]").length == 0) {
				$("#demo_measurement  tbody tr:gt("+(measurement_number-2)+")").remove();
				var tr = $("<tr/>").attr("data-id", measurements.list[i]["id"]);
				tr.append($("<td/>").text(measurements.list[i]["id"]));
				tr.append($("<td/>").text(measurements.list[i]["date"]));
				tr.append($("<td/>").text(measurements.list[i]["time"]));
				tr.append($("<td/>").text(measurements.list[i]["modus"]));
				tr.append($("<td/>").text(measurements.list[i]["led1"]));
				tr.append($("<td/>").text(measurements.list[i]["led2"]));
				tr.append($("<td/>").text(measurements.list[i]["button1"]));
				tr.append($("<td/>").text(measurements.list[i]["sensor1"]));
				$("#demo_measurement tbody").prepend(tr);
			}
		}
		if(measurements.number>0) {
			var subtotal = $("#demo_measurement tbody tr").length;
		    if(subtotal==measurements.number) {		 
		        $(".demo_measurement_number").text("("+measurements.number+")");
		    } else {
			    $(".demo_measurement_number").text("("+subtotal+" of "+measurements.number+")");  
		    }
		}    
		
	}
	//change program
	function set_program(program) {
		if(program_last!=program.last) {
			program_last = program.last;
			program_led1 = program.led1;
			program_led2 = program.led2;
			program_measurement = program.measurement;
			program_led1_timing = [program.led1_start,program.led1_end];
			program_led2_timing = [program.led2_start,program.led2_end];
			program_measurement_timing = program.measurement_start;
			program_period = program.period;
			program_delay = program.delay;
			program_repeats = program.repeats;
			updateProgram();
		}	
	}
	//start periodical check status  
	$("#demo_measurement table").hide();
	check_status($("body").data("url-status"), true);

	/* make buttons demo work */
	$("#arduino-demo button.default_button").click(
			function() {
				var oThis = $(this);
				var url = oThis.data("url");
				var requestMethod = oThis.data("method");
				oThis.attr("disabled", true);
				if ((requestMethod == "get") || (requestMethod == "put")) {
					var requestData = JSON.stringify(oThis.data("data"));
					$.ajax({
						url : url,
						type : requestMethod.toUpperCase(),
						data : requestData,
						contentType : "application/json",
						success : function(data) {
							$("#demo_arduino").removeClass("btn-danger")
									.addClass("btn-light");
							oThis.attr("disabled", false);
						},
						error : function(error) {
							$("#demo_arduino").removeClass("btn-light")
									.addClass("btn-danger");
							oThis.attr("disabled", false);
						}
					});
				}
			});

	var program_changed = false;
	var program_last = 0;
	var program_led1 = false;
	var program_led2 = false;
	var program_led1_timing = [0,0];
	var program_led2_timing = [0,0];
	var program_measurement_timing = 0;
	var program_period = 0;
	var program_delay = 0;
	var program_repeats = 0;	
	
	initProgram();
	
	$("#program_reset").click(function() {
		if(program_changed) {
			program_changed = false;
			$("button.demo_program").prop("disabled",true);
			updateProgram();
		}	
	});
	
	$("#program_save").click(function() {
		var oThis = $(this);
		if(program_changed) {
			var url = oThis.data("url");
			var requestMethod = oThis.data("method");
			var requestData = {
					period: $("#program_period .ui-slider-handle").attr("data-value"),
					led1: $("#program_led1").prop("checked"),
					led1_start: $("#program_led1_timing .ui-slider-handle[data-index=1]").attr("data-value"),
					led1_end: $("#program_led1_timing .ui-slider-handle[data-index=2]").attr("data-value"),
					led2: $("#program_led2").prop("checked"),
					led2_start: $("#program_led2_timing .ui-slider-handle[data-index=1]").attr("data-value"),
					led2_end: $("#program_led2_timing .ui-slider-handle[data-index=2]").attr("data-value"),
					measurement: $("#program_measurement").prop("checked"),
					measurement_start: $("#program_measurement_timing .ui-slider-handle").attr("data-value"),
					repeats: $("#program_repeats .ui-slider-handle").attr("data-value"),
					delay: $("#program_delay .ui-slider-handle").attr("data-value")
			};
			$.ajax({
				url : url,
				type : requestMethod.toUpperCase(),
				data : requestData,
				success : function(data) {
					console.log(data);
				},
				error : function(error) {
					console.log("ERROR");
				}
			});
			program_changed = false;
			$("button.demo_program").prop("disabled",true);			
		}		
	});
	
	function editProgram() {
		program_changed = true;	
		$("button.demo_program").prop("disabled",false);		
	}
	
	function updateProgram() {
		if(!program_changed) {
			function updateValue(ui, postfix) {
				$(ui.handle).attr("data-value", ui.value);
			    $(ui.handle).attr("data-label", ui.value+postfix);
			}
			$("#program_led1").prop("checked",program_led1);
			$("#program_led2").prop("checked",program_led2);
			$("#program_measurement").prop("checked",program_measurement);
			update_range("program_led1_timing",program_led1_timing,program_period," ms");
			update_range("program_led2_timing",program_led2_timing,program_period," ms");
			update_number("program_measurement_timing",program_measurement_timing,program_period," ms");
			update_number("program_period",program_period,60000," ms");
			update_number("program_repeats",program_repeats,20,"");
			update_number("program_delay",program_delay,60000," ms");
			function update_range(id,values,max,postfix) {
				$("#"+id).slider("option", "max", max);
				$("#"+id).slider("option", "values", values.slice(0));
				for(i in values) {
                    updateValue({
			            value: values[i],
			            handle: $("#"+id+" .ui-slider-handle").eq(i)
			        },postfix);
				}			
			}
			function update_number(id,value,max,postfix) {
				$("#"+id).slider("option", "max", max);
				$("#"+id).slider("option", "value", value);
				updateValue({
		            value: value,
		            handle: $("#"+id+" .ui-slider-handle")
		        },postfix);					
			}		
		}	
    }
	
	function initProgram() {
		
		$("button.demo_program").prop("disabled",true);
		function updateValue(ui, postfix) {
			$(ui.handle).attr("data-index", $(ui.handle).index());
			$(ui.handle).attr("data-value", ui.value);
		    $(ui.handle).attr("data-label", ui.value+postfix);
		}		
		$("#program_led1,#program_led2,#program_measurement").change(function() {
			editProgram();
		});
		$("#program_led1").prop("checked",program_led1);
		$("#program_led2").prop("checked",program_led2);
		$("#program_measurement").prop("checked",program_measurement);
		program_range("program_led1_timing",program_led1_timing,0,program_period,100," ms");
	    program_range("program_led2_timing",program_led2_timing,0,program_period,100," ms");
	    program_number("program_measurement_timing",program_measurement_timing,0,program_period,100," ms");
	    program_number("program_period",program_period,0,60000,100," ms");
	    program_number("program_repeats",program_repeats,1,20,1,"");
	    program_number("program_delay",program_delay,0,60000,100," ms");
	    function program_range(id,values,min,max,step,postfix) {	    	
	    	$("#"+id).mousedown(function(){
	    		editProgram();
	    		$(this).parent("div").find("input[type=checkbox]").prop("checked",true);
	    	}).slider({
	    		min : min,
	    		max : max,
	    		range: true,
	    		step: step,
	    		values: values,
	    		create: function (event, ui) {
	    	        $.each(values, function(i, v){
	    	        	updateValue({
	    	                value: v,
	    	                handle: $("#"+id+" .ui-slider-handle").eq(i) 
	    	            }, postfix);
	    	        });
	    	    },
	    	    slide: function (event, ui) {
	    	    	updateValue(ui,postfix);
	    	    }
	    	});	
	    }
	    function program_number(id,value,min,max,step,postfix) {
	    	$("#"+id).mousedown(function(){
	    		editProgram();
	    		$(this).parent("div").find("input[type=checkbox]").prop("checked",true);
	    	}).slider({
	    		min : min,
	    		max : max,
	    		step: step,
	    		value: value,
	    		create: function (event, ui) {
	    	        $.each([value], function(i, v){
	    	            updateValue({
	    	                value: v,
	    	                handle: $("#"+id+" .ui-slider-handle").eq(i) 
	    	            }, postfix);
	    	        });
	    	    },
	    	    slide: function (event, ui) {
	    	    	if(id=="program_period") {
	    	    		var max_led1 = $("#program_led1_timing .ui-slider-handle[data-index=2]").attr("data-value");
	    	    		var max_led2 = $("#program_led2_timing .ui-slider-handle").eq(1).attr("data-value");
	    	    		var max_measurement = $("#program_measurement_timing .ui-slider-handle").attr("data-value");
	    	    		if((ui.value<max_led1)||(ui.value<max_led2)||(ui.value<max_measurement)) {
	    	    			return false;
	    	    		}
	    	    		$("#program_led1_timing ").slider("option", "max", ui.value);
	    	    		$("#program_led2_timing").slider("option", "max", ui.value);
	    	    		$("#program_measurement_timing").slider("option", "max", ui.value);	    	    		
	    	    	} 
	    	        updateValue(ui,postfix);
	    	    }
	    	});
	    }
		
	}
	
	
    
    
    

});