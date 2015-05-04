(function() {
	var triggerBttnMobile = document.getElementsByClassName( 'link depth-0' ),
		overlay = document.querySelector( 'div.overlay' ),
		overlay2 = document.querySelector( 'div.overlay2' ),
		closeBttn = overlay.querySelector( 'button.overlay-close' );
		closeBttnTwo = overlay2.querySelector( 'button.overlay-close' );
		transEndEventNames = {
			'WebkitTransition': 'webkitTransitionEnd',
			'MozTransition': 'transitionend',
			'OTransition': 'oTransitionEnd',
			'msTransition': 'MSTransitionEnd',
			'transition': 'transitionend'
		},
		transEndEventName = transEndEventNames[ Modernizr.prefixed( 'transition' ) ],
		support = { transitions : Modernizr.csstransitions };

	function toggleOverlay() {
		if (classie.has( overlay2, 'open') ) {
			classie.remove( overlay2, 'open' );
		}
		if( classie.has( overlay, 'open' ) ) {
			classie.remove( overlay, 'open' );
			classie.add( overlay, 'close' );
			var onEndTransitionFn = function( ev ) {
				if( support.transitions ) {
					if( ev.propertyName !== 'visibility' ) return;
					this.removeEventListener( transEndEventName, onEndTransitionFn );
				}
				classie.remove( overlay, 'close' );
			};
			if( support.transitions ) {
				overlay.addEventListener( transEndEventName, onEndTransitionFn );
			}
			else {
				onEndTransitionFn();
			}
		}
		else if( !classie.has( overlay, 'close' ) ) {
			classie.add( overlay, 'open' );
		}
	}

	function toggleOverlay2() {
		if (classie.has( overlay, 'open') ) {
			classie.remove( overlay, 'open' );
		}
		if( classie.has( overlay2, 'open' ) ) {
			classie.remove( overlay2, 'open' );
			classie.add( overlay2, 'close' );
			var onEndTransitionFn = function( ev ) {
				if( support.transitions ) {
					if( ev.propertyName !== 'visibility' ) return;
					this.removeEventListener( transEndEventName, onEndTransitionFn );
				}
				classie.remove( overlay2, 'close' );
			};
			if( support.transitions ) {
				overlay2.addEventListener( transEndEventName, onEndTransitionFn );
			}
			else {
				onEndTransitionFn();
			}
		}
		else if( !classie.has( overlay2, 'close' ) ) {
			classie.add( overlay2, 'open' );
		}
	}

	triggerBttnMobile[0].addEventListener( 'click', toggleOverlay);
	closeBttn.addEventListener( 'click', toggleOverlay);
	triggerBttnMobile[1].addEventListener( 'click', toggleOverlay2 );
	closeBttnTwo.addEventListener( 'click', toggleOverlay2 );
})();