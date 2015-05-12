function loginButton() {
	var triggerBttn = document.getElementsByClassName( 'depth-0' );
	triggerBttn[0].addEventListener( 'click', toggleOverlay);
	triggerBttn[1].addEventListener( 'click', toggleOverlay2);
}

var bounds = [
	{min:0,max:736,func:loginButton}
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