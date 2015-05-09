	var triggerBttn = document.getElementById( 'trigger-overlay' ),
		// triggerBttnMobile = document.getElementsByClassName( 'link depth-0' ),
		overlay = document.querySelector( 'div.overlay' ),
		closeBttn = overlay.querySelector( 'button.overlay-close' );
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
			console.log("tourOpen");
			if (tourOpen) {
				$(document).unbind('scroll'); 
  				$('body').css({'overflow':'visible'});
  			}
		}
		else if( !classie.has( overlay, 'close' ) ) {
			if (tourOpen) {
				$('body').css({'overflow':'hidden'});
				$(document).bind('scroll', function() { 
					window.scrollTo(0,0); 
				});
			}
			classie.add( overlay, 'open' );
		}
	}
	triggerBttn.addEventListener( 'click', toggleOverlay);
	closeBttn.addEventListener( 'click', toggleOverlay);