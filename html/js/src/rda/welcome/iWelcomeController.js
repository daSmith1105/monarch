dojo.provide( "rda.welcome.iWelcomeController" );

dojo.require( "rda.common.DController" );
dojo.require( "rda.welcome.iVideoController" );
dojo.require( "rda.welcome.iCamButtonsController" );
dojo.require( "rda.welcome.iControlBoxController" );
dojo.require( "rda.welcome.iPtzController" );

dojo.require( "rda.welcome.iVideoView" );
dojo.require( "rda.welcome.iCamButtonsView" );
dojo.require( "rda.welcome.iControlBoxView" );
dojo.require( "rda.welcome.iPtzView" );

dojo.declare(
	"rda.welcome.iWelcomeController",
	[ rda.common.DController ],
	{
		// Properties
		oVideoController: null,
		oCamButtonsController: null,
		oControlBoxController: null,
		oPtzController: null,

		oVideoView: null,
		oCamButtonsView: null,
		oControlBoxView: null,
		oPtzView: null,

		oView: null,

		_fControls: false,
		_fInstruction: true,

		constructor: function( oGeneralModel, oSystemModel, oCameraConfModel, oCameraModel, oPtzControlModel, oPtzConfigModel, oPtzPresetModel, oView )
		{
			this.oView = oView;

			// Create all sub components
			this.oCamButtonsView = new rda.welcome.iCamButtonsView();
			this.oCamButtonsController = new rda.welcome.iCamButtonsController( oGeneralModel, oSystemModel, oCameraConfModel, this.oCamButtonsView );

			this.oVideoView = new rda.welcome.iVideoView();
			this.oVideoController = new rda.welcome.iVideoController( oCameraConfModel, oCameraModel, this.oVideoView );

			this.oControlBoxView = new rda.welcome.iControlBoxView();
			this.oControlBoxController = new rda.welcome.iControlBoxController( oGeneralModel, oCameraConfModel, this.oControlBoxView );

			this.oPtzView = new rda.welcome.iPtzView();
			this.oPtzController = new rda.welcome.iPtzController( oCameraModel, oCameraConfModel, oPtzControlModel, oPtzConfigModel, oPtzPresetModel, this.oPtzView );

			// Make sure our view knows about all sub views
			oView.addCamButtonsView( this.oCamButtonsView );
			oView.addVideoView( this.oVideoView );
			oView.addControlBoxView( this.oControlBoxView );
			oView.addPtzView( this.oPtzView );

			// Wire up controllers to us
			this.oCamButtonsController.addActionListener( this );
			this.oVideoController.addActionListener( this );
			this.oControlBoxController.addActionListener( this );
			//this.oPtzView.addActionListener( this );   // Needed to manually redraw on WelcomeView when camera is shown/hidden

			this._fControls = false;
			this._fInstruction = true;
		},

		activate: function()
		{
			this.oCamButtonsController.activate();
			this.oVideoController.activate();
			this.oControlBoxController.activate();
			this.oPtzController.activate();

			if ( this._fControls )
				this.toggleControls();

			// Display instruction bar?
			if ( this._fInstruction ) {
				this._fInstruction = false;
				this.oView.showInstruction();
				setTimeout( dojo.hitch( this.oView, "hideInstruction" ), 10000 );
			}

			// Get rid of address bar
			setTimeout( scrollTo, 0, 0, 1 );
		},

		deactivate: function()
		{
			this.oVideoController.deactivate();
			this.oCamButtonsController.deactivate();
			this.oControlBoxController.deactivate();
			this.oPtzController.deactivate();
		},

		actionPerformed: function( sCommand )
		{
			try {
				console.debug( "iWelcomeController received action [" + sCommand + "]" );

				var rgs = sCommand.split( "-" );
				if ( sCommand == "toggle-controls" ) {
					this.toggleControls();

				} else if ( rgs[ 0 ] == "change" && rgs[ 1 ] == "cam" ) {
					// New camera button clicked
					var bCam = parseInt( rgs[ 2 ] );
					this.oPtzController.selectButton( bCam );
					this.oVideoController.selectButton( bCam );

				} else if ( rgs[ 0 ] == "screen" || rgs[ 0 ] == "system" ) {
					// Screen change, just propogate
					this.throwAction( sCommand );

				}

			} catch ( e ) {
				console.debug( "Error handling action for Welcome View [" + e + "]" );
			}
		},

		changeConf: function( bConf )
		{
			this.oVideoController.changeConf( bConf );
			this.oVideoController.selectButton( 1 );
			this.oPtzController.changeConf( bConf );
			this.oPtzController.selectButton( 1 );
		},

		toggleControls: function()
		{
			this._fControls = ! this._fControls;
			if ( this._fControls ) {
				// Start timer here to automatically hide them
				this.oCamButtonsController.showControls();
				this.oControlBoxController.showControls();
				this.oPtzController.showControls();
				this.oView.showControls();

			} else {
				// Kill timer here if there is one
				this.oCamButtonsController.hideControls();
				this.oControlBoxController.hideControls();
				this.oPtzController.hideControls();
				this.oView.hideControls();

			}
		}

	}
);
