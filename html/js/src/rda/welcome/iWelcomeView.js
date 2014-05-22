dojo.provide( "rda.welcome.iWelcomeView" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.welcome.iWelcomeView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/iWelcomeView.html"),

		// Properties
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),
		_imgWatermark: dojo.moduleUrl( "rda", "themes/tundra/images/dt_watermark.gif" ),
		_fPortrait: true,
		_fControls: false,

		// our DOM nodes 
		divLogo: null,
		divWatermark: null,
		divInstruction: null,
		divVideo: null,
		divCamButtons: null,
		divControlBox: null,
		divPtz: null,
		divPlaceholder: null,

		/*
		 * Widget functions
		 */
		postMixInProperties: function()
		{
		},

		postCreate: function()
		{
			// Placeholder to make scrolling work correctly on Portrait view
			with ( this.divPlaceholder.style ) {
				position = "absolute";
				top = 0;
				left = 0;
				width = 320;
				height = 416;
				zIndex = 0;
				display = "";
			}

			with ( this.divLogo.style ) {
				position = "absolute";
				top = 19;
				left = 10;
				zIndex = -1;
				display = "none";
			}

			with ( this.divWatermark.style ) {
				position = "absolute";
				top = 10;
				left = 10;
				zIndex = -1;
				display = "none";
			}

			// Handle browser resizing
			dojo.connect( window, "onorientationchange", this, "_doResize" );
			this._doResize();

			this.hideControls();
		},

		/*
		 * Private functions
		 */
		_doResize: function()
		{
			var oSize = dijit.getViewport();

			if ( oSize.w == 480 ) {
				// Landscape
				this._fPortrait = false;
				with ( this.divPlaceholder.style ) {
					width = 480;
					height = 256;
				}
				with ( this.divInstruction.style ) {
					position = "absolute";
					top = 0;
					left = 0;
					width = 480;
					zIndex = 100;
				}

			} else {
				// Portrait
				this._fPortrait = true;
				with ( this.divPlaceholder.style ) {
					width = 320;
					height = 416;
				}
				with ( this.divInstruction.style ) {
					position = "absolute";
					top = 88;
					left = 0;
					width = 320;
					zIndex = 100;
				}

			}

			if ( this._fControls )
				this.showControls();
			else
				this.hideControls();

			// Get rid of address bar
			scrollTo( 0, 1 );
		},

		/*
		 * Public functions
		 */
		setVisible: function( fVisible )
		{
		},

		addVideoView: function( oVideoView )
		{
			this.divVideo.appendChild( oVideoView.domNode );
		},

		addCamButtonsView: function( oCamButtonsView )
		{
			this.divCamButtons.appendChild( oCamButtonsView.domNode );
		},

		addControlBoxView: function( oControlBoxView )
		{
			this.divControlBox.appendChild( oControlBoxView.domNode );
		},

		addPtzView: function( oPtzView )
		{
			this.divPtz.appendChild( oPtzView.domNode );
		},

		showControls: function()
		{
			this._fControls = true;

			if ( this._fPortrait ) {
				this.divLogo.style.display = "";
				this.divLogo.style.zIndex = 99;
				this.divWatermark.style.display = "none";
				this.divWatermark.style.zIndex = -1;

			} else { // Landscape
				this.divLogo.style.display = "none";
				this.divLogo.style.zIndex = -1;
				this.divWatermark.style.display = "";
				this.divWatermark.style.zIndex = 99;

			}
		},

		hideControls: function()
		{
			this._fControls = false;

			if ( this._fPortrait ) {
				this.divLogo.style.display = "";
				this.divLogo.style.zIndex = 99;
				this.divWatermark.style.display = "none";
				this.divWatermark.style.zIndex = -1;

			} else { // Landscape
				this.divLogo.style.display = "none";
				this.divLogo.style.zIndex = -1;
				this.divWatermark.style.display = "none";
				this.divWatermark.style.zIndex = -1;

			}
		},

		showInstruction: function()
		{
			this.divInstruction.style.display = "";
		},

		hideInstruction: function()
		{
			this.divInstruction.style.display = "none";
		}

	}
);
