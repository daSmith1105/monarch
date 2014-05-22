dojo.provide( "rda.camfail.CameraFailController" );

/********************************************************
 * Camera Fail
 * This module contains a list of all cameras that have
 * reported failed from DVS systems in the field.
 ********************************************************/

dojo.require( "rda.common.DController" );
dojo.require( "rda.common.Observer" );

dojo.declare(
	"rda.camfail.CameraFailController",
	[ rda.common.DController, rda.common.Observer ],
	{
		// Properties
		oView: null,
		oCameraModel: null,
		oServerModel: null,
		fBlockUpdate: false,

		/**
		 * Constructor
		 *
		 * @param oCameraModel
		 *   List of all registered DVS systems
		 * @param oView
		 *   View for this module in MVC
		 */
		constructor: function( oCameraModel, oServerModel, oView )
		{
			this.oView = oView;
			this.oCameraModel = oCameraModel;
			this.oServerModel = oServerModel;

			this.oView.addActionListener( this );
			this.oCameraModel.addObserver( this );
		},

		/**
     * This function is called by Monarch.js when our
     * screen is selected and shown on the screen.  We
     * should initialize our state from this function.
     */
		activate: function()
		{
			if ( ! this.oServerModel.checkIsLoaded() ) {
				this.oView.startLoading();
				this.oServerModel.load();
				this.oView.finishLoading();
				if ( ! this.oServerModel.checkIsLoaded() )
					this.throwAction( "backend-failed" );
			}
			if ( ! this.oCameraModel.checkIsLoaded() ) {
				this.oView.startLoading();
				this.oCameraModel.load();
				this.oView.finishLoading();
				if ( ! this.oCameraModel.checkIsLoaded() )
					this.throwAction( "backend-failed" );
			}
		},

		/**
     * If we need to do any deactivation, like clearing
     * Models to free memory, etc.  It should be done here.
     */
		deactivate: function()
		{
		},

		/**
     * We receive any callbacks from Views here and dispatch
     * accordingly.  Should be screen changes, tab changes, etc.
     *
     * @param sCommand
     *   String parameter to determine what action to take
     */
		actionPerformed: function( sCommand )
		{
			console.debug( "CameraFailController received action [" + sCommand + "]" );

			var rgs = sCommand.split( "-" );
			if ( ( rgs[ 0 ] == "screen" ) && ( rgs[ 1 ] == "change" ) )
				this.throwAction( sCommand );

			else if ( ( rgs[ 0 ] == "skip" ) && ( rgs[ 1 ] == "camera" ) )
				this.skipCamera( parseInt( rgs[ 2 ] ) );

			else if ( ( rgs[ 0 ] == "delete" ) && ( rgs[ 1 ] == "camera" ) )
				this.deleteCamera( parseInt( rgs[ 2 ] ) );

			else if ( ( rgs[ 0 ] == "jump" ) && ( rgs[ 1 ] == "server" ) )
				// Open new tab in Browser for this DVS login page
				this.jumpServer( parseInt( rgs[ 2 ] ) );

		},

		/**
     * This function is called from any Model objects we are "observing".
     * This implements the Observer pattern.
     *
     * @param oObj
     *   Model object that has been updated.
     */
		update: function( oObj )
		{
			if ( this.fBlockUpdate ) return;
			if ( ! oObj.checkIsLoaded() ) return;

			this.oView.setCameraList( this.oCameraModel.getList(), this.oServerModel );
		},

		/**
		 * Skip button was clicked for camera.  Find out its checked flag
		 * and send to backend.
		 *
		 * @param bRow
		 *   Row ID of camera that was clicked
		 */
		skipCamera: function( bRow )
		{
			var rgb = this.oView.getCamera( bRow );
			var oCamera = this.oCameraModel.getCamera( rgb[ 0 ], rgb[ 1 ] );
			oCamera.setSkip( this.oView.checkHasSkip( bRow ) );
			this.fBlockUpdate = true;
			this.oCameraModel.setCamera( oCamera );
			this.fBlockUpdate = false;
		},

		/**
		 * Delete button was clicked for camera.  Find out its serial/camera
		 * number and remove from backend.  Then, remove from table.
		 *
		 * @param bRow
		 *   Row ID of camera that was clicked
		 */
		deleteCamera: function( bRow )
		{
			var rgb = this.oView.getCamera( bRow );
			var oCamera = this.oCameraModel.getCamera( rgb[ 0 ], rgb[ 1 ] );
			this.fBlockUpdate = true;
			fDelete = this.oCameraModel.delCamera( oCamera );
			this.fBlockUpdate = false;

			if ( ! fDelete ) return;

			this.oView.deleteRow( bRow );
		},

		/**
		 * Open a new tab with the DVS login pulled up.
		 *
		 * @param bSerial
		 *   Serial of server to login to
		 */
		jumpServer: function( bSerial )
		{
			var oServer = this.oServerModel.getServerBySerial( bSerial );

			// Build jump string
			var sUrl = "http://" + oServer.getIP();
			if ( oServer.getPort() != 80 )
				sUrl += ":" + oServer.getPort();

			if ( ! this._openInNewWindow( sUrl ) )
				alert( "Cannot open link!" );
		},

		/*********************************************
		 * Helper Functions
		 *********************************************/

		/**
		 * Utility function to open a new Window/Tab in the Browser.
		 *
		 * @param sUrl
		 *   URL to open in new tab
		 */
		_openInNewWindow: function( sUrl )
		{
			// Change "_blank" to something like "newWindow" to load all links in the same new window
			var newWindow = window.open( sUrl, '_blank' );
			if ( newWindow ) {
				if ( newWindow.focus ) {
					newWindow.focus();
				}
				return true;
			}
			return false;
		}

	}
);
