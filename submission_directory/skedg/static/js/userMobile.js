function mobileModification() {
	document.getElementById('userRegular').style.display = 'none';
	document.getElementById('userMobile').style.display = 'block';
	document.getElementById('header').style.display = 'none';

	var wrapperStyle4Container = document.getElementsByClassName('wrapper style4 container');
	for (i = 0; i < wrapperStyle4Container.length; i++) {
		wrapperStyle4Container[i].style.paddingLeft = '1em';
		wrapperStyle4Container[i].style.paddingRight = '1em';
	}
}

function narrowerModification() {
	document.getElementById('userRegular').style.display = 'block';
	document.getElementById('userMobile').style.display = 'none';
	document.getElementById('header').style.display = 'none';

	var wrapperStyle4Container = document.getElementsByClassName('wrapper style4 container');
	for (i = 0; i < wrapperStyle4Container.length; i++) {
		wrapperStyle4Container[i].style.paddingLeft = '1em';
		wrapperStyle4Container[i].style.paddingRight = '1em';
	}
}

function resetModifications() {
	document.getElementById('userRegular').style.display = 'block';
	document.getElementById('userMobile').style.display = 'none';
	document.getElementById('header').style.display = 'block';

	var wrapperStyle4Container = document.getElementsByClassName('wrapper style4 container');
	for (i = 0; i < wrapperStyle4Container.length; i++) {
		wrapperStyle4Container[i].style.paddingLeft = '4em';
		wrapperStyle4Container[i].style.paddingRight = '4em';
	}
}

var bounds = [
	{min:0,max:736,func:mobileModification},
	{min:737,max:840,func:narrowerModification},
	{min:841,func:resetModifications}
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