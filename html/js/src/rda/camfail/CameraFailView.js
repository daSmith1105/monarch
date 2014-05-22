dojo.provide( "rda.camfail.CameraFailView" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.require( "dijit.Dialog" );
dojo.require( "dijit.form.Button" );
dojo.require( "dijit.form.CheckBox" );

dojo.require( "rda.util.Table" );

dojo.declare(
	"rda.camfail.CameraFailView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/CameraFailView.html"),

		// Properties
		_sCopyright: "",
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),
		_rgoListener: [],
		_dlgLoading: null,

		_tblCameraList: null,
		_rgbtnSkip: [],
		_rgbtnDelete: [],

		// our DOM nodes 
		tblHeader: null,
		tdMenu: null,
		btnMenuHome: null,
		btnLogout: null,

		divCamera: null,

		/************************************************
		 * Widget functions
		 ************************************************/

		/**
		 * Constructor
		 * This is called after dojo creates this widget as part
		 * of an initializer.
		 */
		postCreate: function()
		{
			this._tblCameraList = new rda.util.Table();
			this._tblCameraList.addFields( [
				{ field: "id", name: "ID", hidden: true },
				{ field: "serial", name: "Serial", styles: "text-align: center;", type: "numeric" },
				{ field: "name", name: "Name" },
				{ field: "camera", name: "Camera", styles: "text-align: center;", type: "numeric" },
				{ field: "timestamp", name: "Timestamp" },
				{ field: "skip", name: "Skip", styles: "text-align: center;", type: "nosort" },
				{ field: "delete", name: "Delete", styles: "text-align: center;", type: "nosort" },
				{ field: "jump", name: "Jump", styles: "text-align: center;" }
			] );
			dojo.attr( this._tblCameraList.domNode, "align", "center" );

			this.divCamera.appendChild( this._tblCameraList.domNode );

			this._dlgLoading = new dijit.Dialog( {
				title     : "Loading...",
				content   : "Please wait while we retrieve data from the server.",
				style     : "width: 200px",
				draggable : false
			} );

			// Create Menu buttons
			this.btnMenuHome = this._createLink( "Home" );

			this._createMenu( this.divCamera );
		},

		/**
		 * Destructor
		 * We should free up any DOM objects/widgets we've created.
		 */
		destroy: function()
		{
			this.divCamera.removeChild( this._tblCameraList.domNode );
			this.setCameraList( [], null );

			this.inherited( arguments );
		},

		/**
		 * This is called after dojo creates this widgets but before
		 * the template is created.  This fills the template variables in.
		 */
		postMixInProperties: function()
		{
			var oDate = new Date();
			var bYear = oDate.getYear();
			if ( bYear < 1000 ) bYear += 1900;
			this._sCopyright = 'Copyright &copy;' + bYear + ' Dividia Technologies, LLC';
		},

		/**
		 * Our view has been resized, so redraw anything that depends on it.
		 *
		 * @param oViewport
		 *   Viewport object that contains our new dimensions.
		 */
		onResize: function( oViewport )
		{
			var bWidth = oViewport.w - 20;
			this.tblHeader.style.width = bWidth;
			this.divCamera.style.width = bWidth;

			var oPosition = this._findPosition( this.divCamera );
			this.divCamera.style.height = oViewport.h - 10 - oPosition.t;
		},

		/************************************************
		 * Global functions
		 ************************************************/

		/**
		 * Register new ActionListeners.  This will call the actionPerformed
		 * function usually residing on the Controller.
		 *
		 * @param oListener
		 *   The listener is usually just the Controller object.
		 */
		addActionListener: function( oListener )
		{
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnMenuHome,"screen-change-welcome");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnLogout,"screen-change-logout");

			this._rgoListener.push( oListener );
		},

		/**
		 * When our "screen" is switched to/away from this function
		 * is called with a true for Show and a false for Hide.
		 *
		 * @param fVisible
		 *   Is our view currently visible in the browser?
		 */
		setVisible: function( fVisible )
		{
			if ( ! fVisible ) return;
		},

		/**
		 * Show a dialog when we are querying the server and it is going
		 * to take some time to get the data.  This is just feedback to
		 * show the user we are doing something.
		 */
		startLoading: function()
		{
			this._dlgLoading.show();
		},

		/**
		 * Hide dialog when we are querying the server and it is going
		 * to take some time to get the data.  This is just feedback to
		 * show the user we are doing something.
		 */
		finishLoading: function()
		{
			this._dlgLoading.hide();
		},

		/************************************************
		 * Main Tab functions
		 ************************************************/

		/**
		 * Display all of these cameras in our Table.
		 *
		 * @param rgoCamera
		 *   List of Camera objects to display
		 */
		setCameraList: function( rgoCamera, oServerModel )
		{
			this._tblCameraList.clear();
			for ( var ix = 0; ix < this._rgbtnSkip.length; ix++ ) {
				this._rgbtnSkip[ ix ].destroy();
				this._rgbtnDelete[ ix ].destroy();
			}
			this._rgbtnSkip = [];
			this._rgbtnDelete = [];

			for ( var ix = 0; ix < rgoCamera.length; ix++ ) {
				var oCamera = rgoCamera[ ix ];
				var bRow = ix + 1;

				var btnSkip = this._createButton( "checkbox", "skip-camera-" + bRow );
				btnSkip.attr( "checked", oCamera.checkHasSkip() );
				var btnDelete = this._createButton( "button", "delete-camera-" + bRow, "Delete" );

				// If this system is alive, create a jump link
				var oJump = this._createJumpLink( oCamera, oServerModel );

				this._tblCameraList.addRow( {
					"id": bRow,
					"serial": oCamera.getSerial(),
					"name": oCamera.getServer(),
					"camera": oCamera.getCamera(),
					"timestamp": oCamera.getTimestampPretty(),
					"skip": btnSkip,
					"delete": btnDelete,
					"jump": oJump
				} );

				this._rgbtnSkip.push( btnSkip );
				this._rgbtnDelete.push( btnDelete );

			}
		},

		/**
		 * Delete row from table by ID number
		 *
		 * @param bID
		 *   Row ID to delete (field 1)
		 */
		deleteRow: function( bRow )
		{
			for ( var ixRow = 0; ixRow < this._tblCameraList.size(); ixRow++ ) {
				if ( bRow == parseInt( this._tblCameraList.getValue( "id", ixRow ) ) ) {
					this._tblCameraList.delRow( ixRow );
					return;
				}
			}
			throw new Error( "deleteRow failed, does not exist" );
		},

		/**
		 * Get Serial/Camera of row that was just toggled for Skip
		 *
		 * @param bRow
		 *   Row ID that skip button was clicked
		 *
		 * @return Array( Serial, Camera )
		 */
		getCamera: function( bRow )
		{
			for ( var ixRow = 0; ixRow < this._tblCameraList.size(); ixRow++ ) {
				if ( bRow == parseInt( this._tblCameraList.getValue( "id", ixRow ) ) ) {
					var bSerial = parseInt( this._tblCameraList.getValue( "serial", ixRow ) );
					var bCamera = parseInt( this._tblCameraList.getValue( "camera", ixRow ) );
					return [ bSerial, bCamera ];
				}
			}
			throw new Error( "getCamera failed, does not exist" );
		},

		/**
		 * Get Skip toggle status
		 *
		 * @param bRow
		 *   Row ID that was clicked
		 *
		 * @return Checkbox checked flag
		 */
		checkHasSkip: function( bRow )
		{
			return this._rgbtnSkip[ bRow - 1 ].checked;
		},

		/************************************************
		 * Helper functions
		 ************************************************/

		/**
		 * Find our absolute position on the screen.
		 * This works even if we are nested.
		 *
		 * @param o
		 *   Object we want to locate
		 */
		_findPosition: function( o )
		{
			var bTop = bLeft = 0;
			if ( o.offsetParent ) {
				do {
					bTop += o.offsetTop;
					bLeft += o.offsetLeft;
				} while ( o = o.offsetParent );
			}

			return { t: bTop, l: bLeft };
		},

		/**
		 * Create an <a> HTML link to display to the user.
		 * This is used when making our navigation list, etc.
		 *
		 * @param sName
		 *   Text that should show for this link (label)
		 */
		_createLink: function( sName )
		{
			var a = document.createElement( "a" );
			dojo.attr( a, "href", "#" );
			a.appendChild( document.createTextNode( sName ) );
			return a;
		},

		/**
		 * If a server is alive, this will create an HTML INPUT
		 * button that will open a new tab in the browser to go
		 * to it.
		 */
		_createJumpLink: function( oCamera, oServerModel )
		{
			var oJump = "Offline";
			if ( oServerModel == null )  return oJump;

			try {
				var oServer = oServerModel.getServerBySerial( oCamera.getSerial() );
			} catch ( e ) {
				return oJump;
			}

			if ( ! oServer.checkIsAlive() ) return oJump;

			var btn = new dijit.form.Button( { label: "Go" } );
			for ( var ix2 = 0; ix2 < this._rgoListener.length; ix2++ )
				(function(btn,sCommand,oListener){dojo.connect(btn,"onClick",null,function(e){oListener.actionPerformed(sCommand);});})(btn,"jump-server-" + oServer.getSerial(),this._rgoListener[ ix2 ]);
			oJump = btn;
			return oJump;
		},

		/**
		 * Create links to navigate within module (bread crumbs)
		 *
		 * @param o
		 *   DOM object of tab we are displaying
		 */
		_createMenu: function( o )
		{
			// Remove old menu entries
			while ( this.tdMenu.childNodes.length )
				this.tdMenu.removeChild( this.tdMenu.childNodes[ 0 ] );

			if ( o == this.divCamera ) {
				this.tdMenu.appendChild( this.btnMenuHome );

			}
		},

		/**
		 *  Creates a button or checkbox with events attached
		 *
		 * @param sType
		 *   Type of button to create (button/checkbox)
		 * @param sCommand
		 *   Command to throw to listeners
		 * @param sLabel
		 *   If this is a button, what should the label be?
		 */
		_createButton: function( sType, sCommand, sLabel )
		{
			var btn = null;
			if ( sType == "button" ) {
				btn = new dijit.form.Button( { label: sLabel } );
				for ( var ix = 0; ix < this._rgoListener.length; ix++ )
					(function(btn,sCommand,oListener){dojo.connect(btn,"onClick",null,function(e){oListener.actionPerformed(sCommand);});})(btn,sCommand,this._rgoListener[ ix ]);

			} else if ( sType == "checkbox" ) {
				btn = new dijit.form.CheckBox();
				for ( var ix = 0; ix < this._rgoListener.length; ix++ )
					(function(btn,sCommand,oListener){dojo.connect(btn,"onClick",null,function(e){oListener.actionPerformed(sCommand);});})(btn,sCommand,this._rgoListener[ ix ]);

			} else {
				throw new Error( "unknown button type" );

			}

			return btn;
		}

	}
);
