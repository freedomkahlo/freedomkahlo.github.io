// JQuery Date Picker
$(function() {
	$( "#from" ).datepicker({
		defaultDate: "+0d",
		changeMonth: false,
		numberOfMonths: 1,
		onClose: function( selectedDate ) {
			$( "#to" ).datepicker( "option", "minDate", selectedDate );
		}
	});
	$( "#to" ).datepicker({
		defaultDate: "+0d",
		changeMonth: false,
		numberOfMonths: 1,
		onClose: function( selectedDate ) {
			$( "#from" ).datepicker( "option", "maxDate", selectedDate );
		}
	});
	$( "#from2" ).datepicker({
		defaultDate: "+0d",
		changeMonth: false,
		numberOfMonths: 1,
		onClose: function( selectedDate ) {
			$( "#to" ).datepicker( "option", "minDate", selectedDate );
		}
	});
	$( "#to2" ).datepicker({
		defaultDate: "+0d",
		changeMonth: false,
		numberOfMonths: 1,
		onClose: function( selectedDate ) {
			$( "#from" ).datepicker( "option", "maxDate", selectedDate );
		}
	});
	$("#from").datepicker().datepicker("setDate", new Date());
	$("#to").datepicker().datepicker("setDate", new Date());
	$("#from2").datepicker().datepicker("setDate", new Date());
	$("#to2").datepicker().datepicker("setDate", new Date());
});

// JQuery Time Picker
$(function(){
	var time = $("#start_time").val();
	var start_minutes = Date.parse("January 1, 1970, " + time + " UTC") / (60 * 1000);
	$( "#start_slider" ).slider({
		min: 0,
		max: 1425,
		step: 15,
		value: start_minutes, //Set it to the current time
		slide: function(e, ui) {
			var hours = Math.floor(ui.value / 60);
			var minutes = ui.value - (hours * 60);

			if(hours.length == 1) hours = '0' + hours;
			if(minutes.length == 1) minutes = '0' + minutes;
			if(minutes == 0) minutes = '00';

			if(hours >= 12){

				if (hours == 12){
					minutes = minutes + " PM";
				}
				else{
					hours = hours - 12;
					minutes = minutes + " PM";
				}
			}

			else{
				minutes = minutes + " AM";
			}
			if (hours == 0){
				hours = 12;
			}
			$("#start_time").val(hours+":"+minutes)
		}
	});

	var time = $("#start_time2").val();
	var start_minutes = Date.parse("January 1, 1970, " + time + " UTC") / (60 * 1000);
	$( "#start_slider2" ).slider({
		min: 0,
		max: 1425,
		step: 15,
		value: start_minutes, //Set it to the current time
		slide: function(e, ui) {
			var hours = Math.floor(ui.value / 60);
			var minutes = ui.value - (hours * 60);

			if(hours.length == 1) hours = '0' + hours;
			if(minutes.length == 1) minutes = '0' + minutes;
			if(minutes == 0) minutes = '00';

			if(hours >= 12){

				if (hours == 12){
					minutes = minutes + " PM";
				}
				else{
					hours = hours - 12;
					minutes = minutes + " PM";
				}
			}

			else{
				minutes = minutes + " AM";
			}
			if (hours == 0){
				hours = 12;
			}
			$("#start_time2").val(hours+":"+minutes)
		}
	});

	var time = $("#end_time").val();
	var end_minutes = Date.parse("January 1, 1970, " + time + " UTC") / (60 * 1000);
	$( "#end_slider" ).slider({
		min: 0,
		max: 1425,
		step: 15,
		value: end_minutes, //Set it to the current time
		slide: function(e, ui) {
			var hours = Math.floor(ui.value / 60);
			var minutes = ui.value - (hours * 60);

			if(hours.length == 1) hours = '0' + hours;
			if(minutes.length == 1) minutes = '0' + minutes;
			if(minutes == 0) minutes = '00';

			if(hours >= 12){

				if (hours == 12){
					minutes = minutes + " PM";
				}
				else{
					hours = hours - 12;
					minutes = minutes + " PM";
				}
			}

			else{
				minutes = minutes + " AM";
			}
			if (hours == 0){
				hours = 12;
			}
			$("#end_time").val(hours+":"+minutes)
		}
	});

	var time = $("#end_time2").val();
	var end_minutes = Date.parse("January 1, 1970, " + time + " UTC") / (60 * 1000);
	$( "#end_slider2" ).slider({
		min: 0,
		max: 1425,
		step: 15,
		value: end_minutes, //Set it to the current time
		slide: function(e, ui) {
			var hours = Math.floor(ui.value / 60);
			var minutes = ui.value - (hours * 60);

			if(hours.length == 1) hours = '0' + hours;
			if(minutes.length == 1) minutes = '0' + minutes;
			if(minutes == 0) minutes = '00';

			if(hours >= 12){

				if (hours == 12){
					minutes = minutes + " PM";
				}
				else{
					hours = hours - 12;
					minutes = minutes + " PM";
				}
			}

			else{
				minutes = minutes + " AM";
			}
			if (hours == 0){
				hours = 12;
			}
			$("#end_time2").val(hours+":"+minutes)
		}
	});
});

// Slider for event length
$(function(){
	var eventLength = $("#event_length").val().split(' ');
	var lengthPos;
	if (eventLength.length == 4)
		lengthPos = parseInt(eventLength[0]) * 60 + parseInt(eventLength[2]);
	else {
		if (eventLength[1].charAt(0) == 'h') //only hours
			lengthPos = parseInt(eventLength[0]) * 60;
		else //Only minutes
			lengthPos = parseInt(eventLength[0]);
	}
	$("#eventLengthSlider").slider(
	{
		value:lengthPos,
		min: 15,
		max: 480,
		step: 15,
		slide: function( event, ui ) {
			var hours = Math.floor(ui.value / 60);
			var minutes = ui.value - (hours * 60);

			var output = "";
			if (hours == 1)
				output = output + "1 hour";
			if (hours > 1)
				output = output + hours + " hours";

			if (minutes > 0) {
				if (hours > 0)
					output = output + " ";
				output = output + minutes + " minutes";
			}
			$( "#event_length" ).val(output);
		}
	});

	var eventLength = $("#event_length2").val().split(' ');
	var lengthPos;
	if (eventLength.length == 4)
		lengthPos = parseInt(eventLength[0]) * 60 + parseInt(eventLength[2]);
	else {
		if (eventLength[1].charAt(0) == 'h') //only hours
			lengthPos = parseInt(eventLength[0]) * 60;
		else //Only minutes
			lengthPos = parseInt(eventLength[0]);
	}
	$("#eventLengthSlider2").slider(
	{
		value:lengthPos,
		min: 15,
		max: 480,
		step: 15,
		slide: function( event, ui ) {
			var hours = Math.floor(ui.value / 60);
			var minutes = ui.value - (hours * 60);

			var output = "";
			if (hours == 1)
				output = output + "1 hour";
			if (hours > 1)
				output = output + hours + " hours";

			if (minutes > 0) {
				if (hours > 0)
					output = output + " ";
				output = output + minutes + " minutes";
			}
			$( "#event_length2" ).val(output);
		}
	});
});