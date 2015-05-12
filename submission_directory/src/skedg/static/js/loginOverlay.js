	var triggerBttn = document.getElementById( 'trigger-overlay' ),
		triggerBttnTwo = document.getElementById( 'trigger-overlay-two' ),
		triggerBttnThree = document.getElementById( 'getStarted' ),
		triggerBttnFour = document.getElementById( 'trigger-overlay-three' ),
		// triggerBttnMobile = document.getElementsByClassName( 'link depth-0' ),
		overlay = document.querySelector( 'div.overlay' ),
		overlay2 = document.querySelector( 'div.overlay2' ),
		overlay3 = document.querySelector( 'div.overlay3' ),
		closeBttn = overlay.querySelector( 'button.overlay-close' );
		closeBttnTwo = overlay2.querySelector( 'button.overlay-close' );
		closeBttnThree = overlay3.querySelector( 'button.overlay-close' );
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
		if (classie.has( overlay3, 'open') ) {
			classie.remove( overlay3, 'open' );
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
		if (classie.has( overlay3, 'open') ) {
			classie.remove( overlay3, 'open' );
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

	function toggleOverlay3() {
		if (classie.has( overlay, 'open') ) {
			classie.remove( overlay, 'open' );
		}
		if (classie.has( overlay2, 'open') ) {
			classie.remove( overlay2, 'open' );
		}
		if( classie.has( overlay3, 'open' ) ) {
			classie.remove( overlay3, 'open' );
			classie.add( overlay3, 'close' );
			var onEndTransitionFn = function( ev ) {
				if( support.transitions ) {
					if( ev.propertyName !== 'visibility' ) return;
					this.removeEventListener( transEndEventName, onEndTransitionFn );
				}
				classie.remove( overlay3, 'close' );
			};
			if( support.transitions ) {
				overlay3.addEventListener( transEndEventName, onEndTransitionFn );
			}
			else {
				onEndTransitionFn();
			}
		}
		else if( !classie.has( overlay3, 'close' ) ) {
			classie.add( overlay3, 'open' );
		}
	}

	triggerBttn.addEventListener( 'click', toggleOverlay);
	closeBttn.addEventListener( 'click', toggleOverlay);
	triggerBttnTwo.addEventListener( 'click', toggleOverlay2 );
	closeBttnTwo.addEventListener( 'click', toggleOverlay2 );
	triggerBttnThree.addEventListener('click', toggleOverlay2);
	triggerBttnFour.addEventListener( 'click', toggleOverlay3 );
	closeBttnThree.addEventListener( 'click', toggleOverlay3 );