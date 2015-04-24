
	$(document).ready(function(){
		if (typeof sessionStorage['currPage'] == 'string' && $.inArray(sessionStorage['currPage'], ['0', '1', '2']) > -1) {
			$("#wrapper").children("div:eq('" + sessionStorage['currPage'] + "')").show().siblings().hide();
		}
		else {
			 $("#wrapper").children("div:eq('" + 0 + "')").show().siblings().hide();
		 }
		$(".side-nav li").each(function(i) {
			$(this).click(function() {
				$("#wrapper").children("div:eq('" + i + "')").show().siblings().hide();
				if(sessionStorage) {
					sessionStorage['currPage'] = i;
				}
			});
		}); 
	});

		$(function(){
			{% if messages %}
				//Created event
				{% for message in messages %}
					alert('{{message}}');
				{% endfor %}
			{% endif %}
			//Set default for create event
			{% if not time_range %}
				$("#time_range").val("2:00 PM-5:00 PM");
				$("#event_length").val("1 hour 30 minutes");
				//Get current date
				var d = new Date();
				var dString = d.getMonth() + 1 + "/" + d.getDate() + "/" + d.getFullYear();
				$("#from").val(dString);
				$("#to").val(dString);
			{% endif %}
		});

		$(document).ready(function(){
			function split( val ) {
				return val.split( / \s*/ );
			}
			function extractLast( term ) {
				return split( term ).pop();
			}

			$( "input#autocomplete" )
				// don't navigate away from the field on tab when selecting an item
				.bind( "keydown", function( event ) {
					if ( event.keyCode === $.ui.keyCode.TAB &&
						$( this ).autocomplete( "instance" ).menu.active ) {
					  event.preventDefault();
					}
				})
				.autocomplete({
					minLength: 2,
					source: function( request, response ) {
						$.getJSON("{% url 'events:autocomplete_user' %}", {
						term: extractLast( request.term )
						}, response );
					},
					change: function (event, ui) {
						var terms = split( this.value );
						// current input
						if (!lastInput) {
							terms.push( ui.item.value );
							//this.value = lastInput;
							this.value = terms.join( " " );
						}
					},
					search: function() {
						// custom minLength
						var term = extractLast( this.value );
						if ( term.length < 2 ) {
							return false;
						}
					},
					focus: function() {
						// prevent value inserted on focus
						return false;
					},
					select: function( event, ui ) {
						var terms = split( this.value );
						// remove the current input
						terms.pop();
						// add the selected item
						terms.push( ui.item.value );
						// add placeholder to get the comma-and-space at the end
						terms.push( "" );
						this.value = terms.join( " " );
						return false;
					}
				}); 
		});

	/* JQuery Date Picker */
		$(function() {
			$( "#from" ).datepicker({
				defaultDate: "+1w",
				changeMonth: false,
				numberOfMonths: 2,
				onClose: function( selectedDate ) {
					$( "#to" ).datepicker( "option", "minDate", selectedDate );
				}
			});
			$( "#to" ).datepicker({
				defaultDate: "+1w",
				changeMonth: false,
				numberOfMonths: 2,
				onClose: function( selectedDate ) {
					$( "#from" ).datepicker( "option", "maxDate", selectedDate );
				}
			});
		});

		$(function(){
			$('#timelength').combodate({
				firstItem: 'name', //show 'hour' and 'minute' string at first item of dropdown
				minuteStep: 15
			});  
		});

	/* JQuery Time Picker */
		$(function(){
			var times = $("#time_range").val().split('-');
			var start_minutes = Date.parse("January 1, 1970, " + times[0] + " UTC") / (60 * 1000);
			var end_minutes = Date.parse("January 1, 1970, " + times[1] + " UTC") / (60 * 1000);
			var start = 100;
			$( "#time_slider" ).slider({
				range: true,
				min: 0,
				max: 1440,
				step: 15,
				values: [start_minutes, end_minutes], //Set it to the current time
				slide: function(e, ui) {
					var hours1 = Math.floor(ui.values[0] / 60);
					var minutes1 = ui.values[0] - (hours1 * 60);

					if(hours1.length == 1) hours1 = '0' + hours1;
					if(minutes1.length == 1) minutes1 = '0' + minutes1;
					if(minutes1 == 0) minutes1 = '00';

					if(hours1 >= 12){

						if (hours1 == 12){
							hours1 = hours1;
							minutes1 = minutes1 + " PM";
						}
						else{
							hours1 = hours1 - 12;
							minutes1 = minutes1 + " PM";
						}
					}

					else{

						hours1 = hours1;
						minutes1 = minutes1 + " AM";
					}
					if (hours1 == 0){
						hours1 = 12;
						minutes1 = minutes1;
					}
					var hours2 = Math.floor(ui.values[1] / 60);
					var minutes2 = ui.values[1] - (hours2 * 60);

					if(hours2.length == 1) hours2 = '0' + hours2;
					if(minutes2.length == 1) minutes2 = '0' + minutes2;
					if(minutes2 == 0) minutes2 = '00';
					if(hours2 >= 12){
						if (hours2 == 12){
							hours2 = hours2;
							minutes2 = minutes2 + " PM";
						}
						else if (hours2 == 24){
							hours2 = 11;
							minutes2 = "59 PM";
						}
						else{
							hours2 = hours2 - 12;
							minutes2 = minutes2 + " PM";
						}
					}
					else{
						hours2 = hours2;
						minutes2 = minutes2 + " AM";
					}
					$("#time_range").val(hours1+":"+minutes1+"-"+hours2+":"+minutes2)
				}
			});
		});

	/* Slider for event length */
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
				max: 720,
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
		});