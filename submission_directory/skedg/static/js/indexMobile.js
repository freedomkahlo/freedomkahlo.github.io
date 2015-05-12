function mobileModification() {
	document.getElementById('boxedForm').style.display = 'none';
	document.getElementById('boxedFormMobile').style.display = 'block';
	document.getElementById('eventsForm').style.display = 'none';
	document.getElementById('eventsFormMobile').style.display = 'block';
	document.getElementById('header').style.display = 'none';
	document.getElementById('calendarLink').style.display = 'none';
	document.getElementById('notification_li').style.display = 'none';
	var triggerBttn = document.getElementsByClassName( 'depth-0' );
	$(triggerBttn[0]).click(function(){
		location.href='/userPage';
	})

	var wrapperStyle4Container = document.getElementsByClassName('wrapper style4 container');
	for (i = 0; i < wrapperStyle4Container.length; i++) {
		wrapperStyle4Container[i].style.paddingLeft = '1em';
		wrapperStyle4Container[i].style.paddingRight = '1em';
	}
}

function narrowerModification() {
	document.getElementById('boxedForm').style.display = 'none';
	document.getElementById('boxedFormMobile').style.display = 'block';
	document.getElementById('eventsForm').style.display = 'none';
	document.getElementById('eventsFormMobile').style.display = 'block';
	document.getElementById('header').style.display = 'none';
	document.getElementById('calendarLink').style.display = 'inline-block';
	document.getElementById('notification_li').style.display = 'inline-block';
	var triggerBttn = document.getElementsByClassName( 'depth-0' );
	$(triggerBttn[0]).click(function(){
		location.href='/userPage';
	})

	var wrapperStyle4Container = document.getElementsByClassName('wrapper style4 container');
	for (i = 0; i < wrapperStyle4Container.length; i++) {
		wrapperStyle4Container[i].style.paddingLeft = '1em';
		wrapperStyle4Container[i].style.paddingRight = '1em';
	}
}

function createEventMobileReset() {
	document.getElementById('boxedForm').style.display = 'block';
	document.getElementById('boxedFormMobile').style.display = 'none';
	document.getElementById('eventsForm').style.display = 'block';
	document.getElementById('eventsFormMobile').style.display = 'none';
	document.getElementById('header').style.display = 'block';
	document.getElementById('calendarLink').style.display = 'inline-block';
	document.getElementById('notification_li').style.display = 'inline-block';

	var wrapperStyle4Container = document.getElementsByClassName('wrapper style4 container');
	for (i = 0; i < wrapperStyle4Container.length; i++) {
		wrapperStyle4Container[i].style.paddingLeft = '4em';
		wrapperStyle4Container[i].style.paddingRight = '4em';
	}
}

var bounds = [
	{min:0,max:736,func:mobileModification},
	{min:737,max:840,func:narrowerModification},
	{min:841,func:createEventMobileReset}
];

var resizeFn = function(){
	var lastBoundry; // cache the last boundry used
	return function(){
		var width = window.innerWidth;
		var boundry, min, max;
		for(var i=0; i<bounds.length; i++){
			boundry = bounds[i];
			min = boundry.min || Number.MIN_VALUE;
			max = boundry.max || Number.MAX_VALUE;
			if(width > min && width < max 
			   && lastBoundry !== boundry){
				lastBoundry = boundry;
				return boundry.func.call(boundry);
			}
		}
	}
};
$(window).resize(resizeFn());
$(document).ready(function(){
	$(window).trigger('resize');
});