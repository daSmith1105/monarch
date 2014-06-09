dojo.provide( "rda.registrations.RegistrationsView" );

/****************************************************
 * Registrations
 * This module contains a list of all registered DVS
 * systems that we have sold.  This allows us to
 * retrieve IP information and change things like
 * install date and maintenance plan information.
 *
 * This screen contains multiple "Tabs" depending on
 * the state of the application.  Additionally, we
 * have "pages" of Server List links.  This wording
 * seemed a little confusing to me, so I'm writing
 * this to remind me of the breakdowns.
 ****************************************************/

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.require( "dijit.Dialog" );
dojo.require( "dijit.form.Button" );

dojo.require( "rda.util.Table" );

dojo.declare(
	"rda.registrations.RegistrationsView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/RegistrationsView.html"),

		// Properties
		_sCopyright: "",
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),
		_rgoListener: [],
		_oTabCurr: null,
		_dlgLoading: null,
		_fVisible: false,

		_tblServerList: null,
		_rgbtnListPage: [],
		_ixListPage: 0,
		_bHandlerId: 0,

		// our DOM nodes 
		tblHeader: null,
		tdMenu: null,
		btnMenuHome: null,
		btnMenuList: null,
		btnLogout: null,

		divTabList: null,
		entSearch: null,
		btnHelp: null,
		divListPage: null,
		divServerList: null,

		divTabInfo: null,
		imgStatus: null,
		btnCancel: null,
		btnApply: null,
		pSerial: null,
		pController: null,
		entName: null,
		entCompany: null,
		entInstall: null,
		cbxMaint: null,
		entMaintenanceOnsite: null,
		btnSkip: null,
		pHeartbeat: null,
		pIP: null,
		pRemoteIP: null,
		pLocalIP: null,
		pPort: null,
		pSshPort: null,
		entCategories: null,
		entPreferred: null,
		entKey: null,
		cbxVersion: null,
		cbxNumcam: null,
		entPosKey: null,
		entPosLock: null,
		entMac: null,
		btnKillHard: null,
		btnKillSoft: null,
		btnEnterprise: null,
		btnAuth: null,
		pVersionInstalled: null,
		entSummary: null,
		entDesc: null,
		btnOpen: null,
		btnMaint: null,
		tblTicketList: null,

		/**************************************************
		 * Widget functions
		 **************************************************/

		/**
		 * Constructor
		 * This is called after dojo creates this widget as part
		 * of an initializer.
		 */
		postCreate: function()
		{
			this._tblServerList = new rda.util.Table();
			this._tblServerList.addFields( [
				{ field: "serial", name: "Serial", styles: "text-align: center;", type: "numeric" },
				{ field: "company", name: "Company" },
				{ field: "name", name: "Name" },
				{ field: "channel", name: "Channel", styles: "text-align: center;", type: "numeric" },
				{ field: "version", name: "Version", styles: "text-align: center;" },
				{ field: "distro", name: "Distro", styles: "text-align: center;" },
				{ field: "jump", name: "Jump", styles: "text-align: center;" },
			] );
			dojo.attr( this._tblServerList.domNode, "align", "center" );

			this.divServerList.appendChild( this._tblServerList.domNode );

			this._dlgLoading = new dijit.Dialog( {
				title     : "Loading...",
				content   : "Please wait while we retrieve data from the server.",
				style     : "width: 200px",
				draggable : false
			} );

			// Create Menu buttons
			this.btnMenuHome = this._createLink( "Home" );
			this.btnMenuList = this._createLink( "Registrations" );

			// Hook Product Key events
			dojo.connect( this.cbxVersion, "onchange", this, this.clearKey );
			dojo.connect( this.cbxNumcam, "onchange", this, this.clearKey );
			dojo.connect( this.entMac, "onchange", this, this.clearKey );
			dojo.connect( this.entPosLock, "onchange", this, this.clearKeyPos );
		},

		/**
		 * Destructor
		 * We should free up any DOM objects/widgets we've created.
		 */
		destroy: function()
		{
			for ( var ix = 0; ix < this._rgbtnListPage.length; ix++ )
				this._rgbtnListPage[ ix ].destroy();

			this.divServerList.removeChild( this._tblServerList.domNode );
			this._tblServerList.destroy();

			this.inherited( arguments );
		},

		/**
		 * This is called after dojo creates this widget but before
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
			//this.divListPage.style.width = bWidth;
			//this.divServerList.style.width = bWidth;

			//var oPosition = this._findPosition( this.divServerList );
			//this.divServerList.style.height = oViewport.h - 10 - oPosition.t;
		},

		/**************************************************
		 * Global functions
		 **************************************************/

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
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnMenuList,"change-tab-list");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnLogout,"screen-change-logout");

			(function(btn,sCommand){dojo.connect(btn,"onClick",null,function(sField,ixRow){oListener.actionPerformed(sCommand+"-"+sField+"-"+ixRow);});})(this._tblServerList,"change-tab-info-row");

			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnCancel,"server-info-cancel");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnApply,"server-info-apply");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnOpen,"server-info-open");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnMaint,"server-info-maint");

			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnHelp,"show-search-help");

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
			this._fVisible = fVisible;

			this.setupTabFocus();
		},

		/**
		 * Display new "tab" - Server List, Server Info, Product Key Serial info
		 *
		 * @param sTab
		 *   Name of tab to display
		 */
		changeTab: function( sTab )
		{
			var o = this.divTabList;
			if ( sTab == "info" )
				o = this.divTabInfo;

			if ( this._oTabCurr != null )
				this._oTabCurr.style.display = "none";
			this._oTabCurr = o;
			this._oTabCurr.style.display = "block";

			this._createMenu( o );

			this.setupTabFocus();
		},

		/**
		 * Handle anything special with keypresses and focus for the different tabs.
		 */
		setupTabFocus: function()
		{
			if ( this._fVisible && this._oTabCurr == this.divTabList ) {
				if ( this._bHandlerId == 0 )
					this._bHandlerId = dojo.connect( document, 'onkeypress', this, '_onKey' );

			} else {
				if ( this._bHandlerId != 0 ) {
					dojo.disconnect( this._bHandlerId );
					this._bHandlerId = 0;
				}

			}
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

		/**
		 * Ask user to save changes
		 *
		 * @return True if we should continue with save
		 */
		promptSaveChanges: function()
		{
			return confirm( "Would you like to save your changes to this Server?" );
		},

		/**************************************************
		 * Tab - Server List functions
		 **************************************************/

		/**
		 * Setup our pagination links that will allow the user
		 * to switch which "group" of servers to display in list.
		 *
		 * @param bNum
		 *   Number of buttons to create
		 * @param bSpan
		 *   Number of servers to display at a time
		 */
		setListPage: function( bNum, bSpan )
		{
			// Clear old buttons
			for ( var ix = 0; ix < this._rgbtnListPage.length; ix++ ) {
				this.divListPage.removeChild( this._rgbtnListPage[ ix ].domNode );
				this._rgbtnListPage[ ix ].destroy();
			}
			this._rgbtnListPage = [];

			// Create new buttons
			for ( var ix = 0; ix <= bNum; ix++ ) {
				var ixPage = ix + 1;
				var sLabel = ixPage;

				// Handle All link special
				if ( ix == bNum ) {
					sLabel = "All";
					ixPage = 0;
				}

				var btn = new dijit.form.Button( { label: sLabel } );
				this.divListPage.appendChild( btn.domNode );

				for ( var ixEvent = 0; ixEvent < this._rgoListener.length; ixEvent++ )
					(function(btn,sCommand,oListener){dojo.connect(btn,"onClick",null,function(e){oListener.actionPerformed(sCommand);});})(btn,"change-list-page-" + ixPage,this._rgoListener[ ixEvent ]);

				this._rgbtnListPage.push( btn );
			}
		},

		/**
		 * Have we already setup our pagination?
		 *
		 * @return true/false if we have setup pagination
		 */
		isListPageSetup: function()
		{
			return this._rgbtnListPage.length != 0;
		},

		/**
		 * A pagination link was pressed so we should update
		 * our button disabled "status".
		 *
		 * @param ix
		 *   Index of pagination button
		 */
		selectListPage: function( ix )
		{
			this._rgbtnListPage[ this._ixListPage ].attr( "disabled", false );
			if ( ix == -99 ) return;
			this._ixListPage = ix - 1;
			if ( this._ixListPage < 0 )
				this._ixListPage = this._rgbtnListPage.length - 1;
			this._rgbtnListPage[ this._ixListPage ].attr( "disabled", true );
			this.entSearch.focus();
		},

		/**
		 * Display all of these servers in our Table.
		 * This list has already been filtered down and
		 * the pagination is handled elsewhere.
		 *
		 * @param rgoServer
		 *   Filtered list of Server objects to display
		 */
		setServerList: function( rgoServer )
		{
			this._tblServerList.clear();

			for ( var ix = 0; ix < rgoServer.length; ix++ ) {
				var oServer = rgoServer[ ix ];

				// If this system is alive, create a jump link
				var oJump = this._createJumpLink( oServer );

				this._tblServerList.addRow( {
					"serial": oServer.getSerial(),
					"company": oServer.getCompany(),
					"name": oServer.getName(),
					"channel": oServer.getVersion(),
					"version": ( oServer.getVersionInstalled() != '' ) ? oServer.getVersionInstalled() : 'N/A',
					"distro": ( oServer.getOS() != '' ) ? oServer.getOS() : 'N/A',
					"jump": oJump
				} );
			}
		},

		/**
		 * Sort server list by field
		 *
		 * @param sField
		 *   Field of server list to sort by
		 */
		sortTable: function( sField )
		{
			this._tblServerList.sortTable( sField );
		},

		/**
		 * Get all serials displayed in table
		 */
		getSerials: function()
		{
			var rgbSerial = new Array();
			for ( var ixRow = 0; ixRow < this._tblServerList.size(); ixRow++ ) {
				var bSerial = parseInt( this._tblServerList.getValue( "serial", ixRow ) );
				rgbSerial[ ixRow ] = bSerial;
			}
			return rgbSerial;
		},

		/**
		 * Get a value from our Server List table by row/column
		 *
		 * @param sField
		 *   Column field name to set value for
		 * @param ixRow
		 *   Zero based row index to get value for
		 */
		getListValue: function( sField, ixRow )
		{
			return this._tblServerList.getValue( sField, ixRow );
		},

		/**
		 * Update server info in our Table list
		 *
		 * @param ixRow
		 *   Zero based row index to get value for
		 * @param oServer
		 *   Server to update row for
		 */
		setListValues: function( ixRow, oServer )
		{
			this._tblServerList.setValue( "company", ixRow, oServer.getCompany() );
			this._tblServerList.setValue( "name", ixRow, oServer.getName() );
			this._tblServerList.setValue( "channel", ixRow, oServer.getVersion() );
			this._tblServerList.setValue( "version", ixRow, oServer.getVersionInstalled() );
			this._tblServerList.setValue( "distro", ixRow, oServer.getOS() );
			this._tblServerList.setValue( "jump", ixRow, this._createJumpLink( oServer ) );
		},

		/**
		 * Show search examples
		 */
		showSearchHelp: function()
		{
			alert(
				"Supported searches:\n" +
				" Project Key Seed values [552853041]\n" +
				" Searching based on Serial [386]\n" +
				" Searching based on Name/Company [Dividia]\n" +
				" Searching based on DVR Version upgrade status\n" +
				"   [check upgrade] [check upgrade maint]\n" +
				" Searching based on DVR Distro upgrade status\n" +
				"   [check distro upgrade] [check distro upgrade maint]"
			);
		},

		/**
		 * Figure out what kind of data is in our search box.
		 * Currently, we support entering:
		 *  - Product Key Seed values
		 *  - Searching based on Serial (numbers)
		 *  - Searching based on Name/Company (string)
		 *  - Searching based on DVR Version upgrade status (string)
		 *  - Searching based on DVR Distro upgrade status (string)
		 */
		parseSearch: function()
		{
			var s = this.entSearch.value;
			var b = parseInt( s );

			// DVR Version Upgrade Status
			if ( s == 'check upgrade' )
				this.throwAction( "list-search-version-all" );

			else if ( s == 'check upgrade maint' )
				this.throwAction( "list-search-version-maint" );

			// DVR Distro Upgrade Status
			else if ( s == 'check distro upgrade' )
				this.throwAction( "list-search-distro-all" );

			else if ( s == 'check distro upgrade maint' )
				this.throwAction( "list-search-distro-maint" );

			// String Search (Name, Company)
			else if ( isNaN( b ) || ( String( b ) != s ) )
				this.throwAction( "list-search-string-" + s );

			// Number Search (Serial)
			else if ( b < 99999 )
				this.throwAction( "list-search-serial-" + b );

			// Product Key Seed
			else
				this.throwAction( "product-key-seed-" + b + "]" );

			this.entSearch.value = "";
		},

		/**
		 * Handle all keypresses for ServerList Tab
		 * This should detect a 't' keypress and give focus
		 * to our search box.  Then, when enter is pressed
		 * it should perform the search
		 */
		_onKey: function( e )
		{
			try {
				if ( e.target == this.entSearch ) {
					if ( e.keyCode == dojo.keys.ENTER )
						this.parseSearch();
				} else {
					if ( String.fromCharCode( e.which ) == 't' ) {
						this.entSearch.focus();
						dojo.stopEvent( e );
					}
				}
			} catch ( e ) {
				console.debug( "Error handling key press [" + e + "]" );
			}
		},

		/**
		 * Ask user if we should add this server to our database.
		 *
		 * @param sKey
		 *   Product Key we would create for serial
		 * @param bSerial
		 *   Serial of server to add
		 * @param sVersion
		 *   Version installed on server
		 * @param bNumcam
		 *   Number of cameras supported for this server
		 * @param sMac
		 *   Mac to tie this product key to
		 *
		 * @return True if the user wants to add this server
		 */
		promptAddServer: function( sKey, bSerial, sVersion, bNumcam, sMac )
		{
			var sMsg = "Would you like to add this Server?\n" +
			           " - Key\t\t" + sKey + "\n" +
			           " - Serial\t\t" + bSerial + "\n" +
			           " - Version\t\t" + sVersion + "\n" +
			           " - Numcam\t" + bNumcam + "\n" +
			           " - Mac\t\t" + sMac;

			return confirm( sMsg );
		},

		/**
		 * Ask user if we should reset key information for this server.
		 *
		 * @param oServer
		 *   Server object to reset
		 * @param sKey
		 *   Product Key for new server information (version,numcam,mac)
		 * @param sVersion
		 *   Version installed on server
		 * @param bNumcam
		 *   Number of cameras supported for this server
		 * @param sMac
		 *   Mac to tie this product key to
		 *
		 * @return True if the user wants to reset this server
		 */
		promptKeyInvalid: function( oServer, sKey, sVersion, bNumcam, sMac )
		{
			var sMsg = "Would you like to generate a new Product Key for this Server?\n" +
			           " - Serial\t\t" + oServer.getSerial() + "\n" +
			           " - Company\t" + oServer.getCompany() + "\n" +
			           " - Name\t\t" + oServer.getName() + "\n" +
			           "\n" +
			           "Old\n" +
			           " - Key\t\t" + oServer.getKey() + "\n" +
			           " - Version\t\t" + oServer.getVersion() + "\n" +
			           " - Numcam\t" + oServer.getNumcam() + "\n" +
			           " - Mac\t\t" + oServer.getMac() + "\n" +
			           "New\n" +
			           " - Key\t\t" + sKey + "\n" +
			           " - Version\t\t" + sVersion + "\n" +
			           " - Numcam\t" + bNumcam + "\n" +
			           " - Mac\t\t" + sMac;

			return confirm( sMsg );
		},

		/**
		 * Show error that seed parameters were not valid
		 */
		promptSeedInvalid: function()
		{
			alert( "The Product Key Seed you entered was not valid." );
		},

		/**
		 * Show error that Server object could not be found
		 */
		promptServerNotFound: function()
		{
			alert( "The serial you requested cannot be found." );
		},

		/**
		 * Show message notifying that the POS Lock is the same.
		 * We will show the server info tab and allow them to set a new one.
		 */
		promptPosLock: function()
		{
			var sMsg = "The POS Lock for this seed has already been set.\n\n" +
				"Redirecting to Server Info page.  Please update POS Lock if you " +
				"would like to generate a new POS Key.";
				
			alert( sMsg );
		},
		
		/**************************************************
		 * Tab - Server Info functions
		 **************************************************/

		/**
		 * Some part of the Product Key information changed, so
		 * clear out the existing key so they can rekey.
		 */
		clearKey: function()
		{
			this.entKey.value = "";
		},

		/**
		 * Some part of the Pos Key information changes (POS Lock?), so
		 * clear out the existing key so they can rekey.
		 */
		clearKeyPos: function()
		{
			this.entPosKey.value = "";
		},
		
		/**
		 * Display this server's information to update/change.
		 *
		 * @param oServerPrev
		 *   Server Object currently set to
		 * @param oServerCurr
		 *   Server Object to update to
		 */
		setServer: function( oServerPrev, oServer )
		{
			var fSoftUpdate = false;
			if ( oServerPrev != null && oServerPrev.getSerial() == oServer.getSerial() )
				fSoftUpdate = true;

			// Server Status
			if ( ! oServer.checkIsAlive() ) {
				this.imgStatus.src = "images/status_red.gif";
			} else if ( oServer.checkIsSick() ) {
				this.imgStatus.src = "images/status_yellow.gif";
			} else {
				this.imgStatus.src = "images/status_green.gif";
			}

			// DVS Info
			while ( this.pSerial.childNodes.length > 0 )
				this.pSerial.removeChild( this.pSerial.childNodes[ 0 ] )
			this.pSerial.appendChild( document.createTextNode( oServer.getSerial() ) );

			while ( this.pController.childNodes.length > 0 )
				this.pController.removeChild( this.pController.childNodes[ 0 ] )
			this.pController.appendChild( document.createTextNode( oServer.getController() ) );

			this.softUpdate( fSoftUpdate, this.entName, oServerPrev != null ? oServerPrev.getName() : null, oServer.getName() );

			this.softUpdate( fSoftUpdate, this.entCompany, oServerPrev != null ? oServerPrev.getCompany() : null, oServer.getCompany() );

			this.softUpdate( fSoftUpdate, this.entInstall, oServerPrev != null ? oServerPrev.getInstallPretty() : null, oServer.getInstallPretty() );

			this.softUpdate( fSoftUpdate, this.cbxMaint, oServerPrev != null ? oServerPrev.getMaintenance() : null, oServer.getMaintenance() );
			this.softUpdate( fSoftUpdate, this.entMaintenanceOnsite, oServerPrev != null ? oServerPrev.getMaintenanceOnsitePretty() : null, oServer.getMaintenanceOnsitePretty() );

			this.softUpdateBoolean( fSoftUpdate, this.btnSkip, oServerPrev != null ? oServerPrev.checkHasSkip() : null, oServer.checkHasSkip() );

			this.softUpdateBoolean( fSoftUpdate, this.btnKillHard, oServerPrev != null ? oServerPrev.getKill() == 'hardkill' : null, oServer.getKill() == 'hardkill' );
			this.softUpdateBoolean( fSoftUpdate, this.btnKillSoft, oServerPrev != null ? oServerPrev.getKill() == 'softkill' : null, oServer.getKill() == 'softkill' );

			this.softUpdateBoolean( fSoftUpdate, this.btnEnterprise, oServerPrev != null ? oServerPrev.checkHasEnterprise() : null, oServer.checkHasEnterprise() );

			// Network Info
			while ( this.pHeartbeat.childNodes.length > 0 )
				this.pHeartbeat.removeChild( this.pHeartbeat.childNodes[ 0 ] )
			this.pHeartbeat.appendChild( document.createTextNode( oServer.getTimestampPretty() ) );
			this.pHeartbeat.appendChild( document.createTextNode( " " ) );
			var oJump = this._createJumpLink( oServer );
			if ( typeof( oJump ) == "string" ) {
				this.pHeartbeat.appendChild( document.createTextNode( "(" + oJump + ")" ) );
			} else {
				this.pHeartbeat.appendChild( oJump.domNode );
			}

			while ( this.pIP.childNodes.length > 0 )
				this.pIP.removeChild( this.pIP.childNodes[ 0 ] )
			this.pIP.appendChild( document.createTextNode( oServer.getIP() ) );

			while ( this.pRemoteIP.childNodes.length > 0 )
				this.pRemoteIP.removeChild( this.pRemoteIP.childNodes[ 0 ] )
			this.pRemoteIP.appendChild( document.createTextNode( oServer.getRemoteIP() ) );

			while ( this.pLocalIP.childNodes.length > 0 )
				this.pLocalIP.removeChild( this.pLocalIP.childNodes[ 0 ] )
			this.pLocalIP.appendChild( document.createTextNode( oServer.getLocalIP() ) );

			while ( this.pPort.childNodes.length > 0 )
				this.pPort.removeChild( this.pPort.childNodes[ 0 ] )
			this.pPort.appendChild( document.createTextNode( oServer.getPort() ) );

			while ( this.pSshPort.childNodes.length > 0 )
				this.pSshPort.removeChild( this.pSshPort.childNodes[ 0 ] )
			this.pSshPort.appendChild( document.createTextNode( oServer.getSshPort() ) );

			this.softUpdate( fSoftUpdate, this.entCategories, oServerPrev != null ? oServerPrev.getCategories() : null, oServer.getCategories() );

			this.softUpdate( fSoftUpdate, this.entPreferred, oServerPrev != null ? oServerPrev.getPreferred() : null, oServer.getPreferred() );

			this.softUpdateBoolean( fSoftUpdate, this.btnAuth, oServerPrev != null ? oServerPrev.checkHasAuth() : null, oServer.checkHasAuth() );

			// Product Key
			this.softUpdate( fSoftUpdate, this.entKey, oServerPrev != null ? oServerPrev.getKey() : null, oServer.getKey() );

			this.softUpdate( fSoftUpdate, this.cbxVersion, oServerPrev != null ? oServerPrev.getVersion() : null, oServer.getVersion() );

			this.softUpdate( fSoftUpdate, this.cbxNumcam, oServerPrev != null ? oServerPrev.getNumcam() : null, oServer.getNumcam() );

			this.softUpdate( fSoftUpdate, this.entPosKey, oServerPrev != null ? oServerPrev.getPosKey() : null, oServer.getPosKey() );
			this.softUpdate( fSoftUpdate, this.entPosLock, oServerPrev != null ? oServerPrev.getPosLock() : null, oServer.getPosLock() );
			
			this.softUpdate( fSoftUpdate, this.entMac, oServerPrev != null ? oServerPrev.getMac() : null, oServer.getMac() );

			while ( this.pVersionInstalled.childNodes.length > 0 )
				this.pVersionInstalled.removeChild( this.pVersionInstalled.childNodes[ 0 ] )
			this.pVersionInstalled.appendChild( document.createTextNode(
				'[' +
				( oServer.getVersionInstalled() != '' ) ? oServer.getVersionInstalled() : 'N/A' + '-' +
				( oServer.getOS() != '' ) ? oServer.getOS() : 'N/A' +
				']'
			) );
		},

		/**
		 * Update this entry softly, so only if we haven't changed it ourselves
		 */
		softUpdate: function( fSoftUpdate, oObj, sValuePrev, sValue )
		{
			if ( ! fSoftUpdate ) {
				// Update no matter what
				oObj.value = sValue;
				return;
			}

			// Update softly
			if ( sValuePrev == oObj.value ) {
				oObj.value = sValue;
				return;
			}
		},

		/**
		 * Update this entry softly, so only if we haven't changed it ourselves
		 */
		softUpdateBoolean: function( fSoftUpdate, oObj, fValuePrev, fValue )
		{
			if ( ! fSoftUpdate ) {
				// Update no matter what
				oObj.checked = fValue;
				return;
			}

			// Update softly
			if ( fValuePrev == oObj.checked ) {
				oObj.checked = fValue;
				return;
			}
		},

		/**
		 * Set Tickets for this serial
		 */
		setTickets: function( rgoTicket )
		{
			this._clearTickets();

			// If None, just show that
			if ( rgoTicket.length <= 0 ) {
				this._addNoneTicket();
				return;
			}

			for ( var ix = 0; ix < rgoTicket.length; ix++ )
				this._addTicket( rgoTicket[ ix ][ 0 ], rgoTicket[ ix ][ 1 ], rgoTicket[ ix ][ 2 ], rgoTicket[ ix ][ 3 ], rgoTicket[ ix ][ 4 ] );
		},

		/**
		 * Getter functions for Server Info
		 */
		getName: function()
		{
			return this.entName.value;
		},
		getCompany: function()
		{
			return this.entCompany.value;
		},
		getInstall: function()
		{
			return this.entInstall.value;
		},
		getMaintenance: function()
		{
			return this.cbxMaint.value;
		},
		getMaintenanceOnsite: function()
		{
			return this.entMaintenanceOnsite.value;
		},
		checkHasSkip: function()
		{
			return this.btnSkip.checked;
		},
		getCategories: function()
		{
			return this.entCategories.value;
		},
		getPreferred: function()
		{
			return this.entPreferred.value;
		},
		getKey: function()
		{
			return this.entKey.value;
		},
		getVersion: function()
		{
			return this.cbxVersion.value;
		},
		getNumcam: function()
		{
			return this.cbxNumcam.value;
		},
		getPosKey: function()
		{
			return this.entPosKey.value;
		},
		getPosLock: function()
		{
			return this.entPosLock.value;
		},
		getMac: function()
		{
			return this.entMac.value;
		},
		getKill: function()
		{
			if ( this.btnKillHard.checked )
				return "hardkill";
			else if ( this.btnKillSoft.checked )
				return "softkill";
			return "";
		},
		checkHasEnterprise: function()
		{
			return this.btnEnterprise.checked;
		},
		checkHasAuth: function()
		{
			return this.btnAuth.checked;
		},
		getSummary: function()
		{
			return this.entSummary.value;
		},
		clearSummary: function()
		{
			this.entSummary.value = '';
		},
		getDescription: function()
		{
			return this.entDesc.value;
		},
		clearDescription: function()
		{
			this.entDesc.value = '';
		},

		/**************************************************
		 * Helper functions
		 **************************************************/

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

			if ( o == this.divTabList ) {
				this.tdMenu.appendChild( this.btnMenuHome );

			} else if ( o == this.divTabInfo ) {
				this.tdMenu.appendChild( this.btnMenuHome );
				this.tdMenu.appendChild( document.createTextNode( " > " ) );
				this.tdMenu.appendChild( this.btnMenuList );

			}
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
		_createJumpLink: function( oServer )
		{
			var oJump = "Offline";
			if ( oServer.checkIsAlive() ) {
				var btn = new dijit.form.Button( { label: "Go" } );
				for ( var ix2 = 0; ix2 < this._rgoListener.length; ix2++ )
					(function(btn,sCommand,oListener){dojo.connect(btn,"onClick",null,function(e){oListener.actionPerformed(sCommand);});})(btn,"jump-server-" + oServer.getSerial(),this._rgoListener[ ix2 ]);
				oJump = btn;
			}
			return oJump;
		},

		/**
		 * Helper function to throwActions manually to our Controller
		 */
		throwAction: function( sCommand )
		{
			for ( var ix = this._rgoListener.length - 1; ix >= 0; ix-- )
				this._rgoListener[ ix ].actionPerformed( sCommand );
		},

		/**
		 * Enable/Disable kill settings
		 */
		toggleKill: function( fEnable )
		{
			if ( fEnable ) {
				this.btnKillHard.disabled = '';
				this.btnKillSoft.disabled = '';
			} else {
				this.btnKillHard.disabled = 'disabled';
				this.btnKillSoft.disabled = 'disabled';
			}
		},

		/**
		 * Clear all Tickets from our ticket list table
		 */
		_clearTickets: function()
		{
			// Remove old ticket entries
			var tblBody = this.tblTicketList.childNodes[ 1 ];
			while ( tblBody.childNodes.length > 2 )
				tblBody.removeChild( tblBody.childNodes[ tblBody.childNodes.length - 1 ] );
		},

		/**
		 * Add a new ticket to our table list
		 *
		 * @param bID
		 *   Bug ID
		 * @param sAssign
		 *   Who is this bug assigned to
		 * @param sStatus
		 *   Ticket Status (CONFIRMED, IN_PROGRESS, RESOLVED, etc)
		 * @param sSummary
		 *   Ticket Summary
		 */
		_addTicket: function( bID, sAssign, sStatus, sSummary, bTimestamp )
		{
			var tblBody = this.tblTicketList.childNodes[ 1 ];

			// Alright, add a new row for these columns
			var oRow = document.createElement( "tr" );

			// ID
			var oCol = document.createElement( "td" );
			var a = this._createLink( bID );
			for ( var ix2 = 0; ix2 < this._rgoListener.length; ix2++ )
				(function(btn,sCommand,oListener){dojo.connect(a,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(a,"show-ticket-" + bID,this._rgoListener[ ix2 ]);
			oCol.appendChild( a );
			oRow.appendChild( oCol );

			// Modified
			oCol = document.createElement( "td" );
			oCol.appendChild( document.createTextNode( this._toPretty( bTimestamp, true ) ) );
			oRow.appendChild( oCol );

			// Assignee
			oCol = document.createElement( "td" );
			oCol.appendChild( document.createTextNode( sAssign ) );
			oRow.appendChild( oCol );

			// Status
			oCol = document.createElement( "td" );
			oCol.appendChild( document.createTextNode( sStatus ) );
			oRow.appendChild( oCol );

			// Summary
			oCol = document.createElement( "td" );
			var a = this._createLink( sSummary );
			for ( var ix2 = 0; ix2 < this._rgoListener.length; ix2++ )
				(function(btn,sCommand,oListener){dojo.connect(a,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(a,"show-ticket-" + bID,this._rgoListener[ ix2 ]);
			oCol.appendChild( a );
			oRow.appendChild( oCol );

			tblBody.appendChild( oRow );
		},

		/**
		 * Add row to Ticket Table that says no tickets found
		 */
		_addNoneTicket: function()
		{
			var tblBody = this.tblTicketList.childNodes[ 1 ];

			// Alright, add a new row for these columns
			var oRow = document.createElement( "tr" );

			oCol = document.createElement( "td" );
			dojo.attr( oCol, "colspan", "5" );
			oCol.appendChild( document.createTextNode( "No Tickets Found" ) );
			oRow.appendChild( oCol );

			tblBody.appendChild( oRow );
		},

		/**
		 * Make unix timestamp into a date/time string
		 */
		_toPretty: function( bTimestamp, fTime )
		{
			var o = new Date( bTimestamp * 1000 );
			var bYear = o.getFullYear();
			var bMonth = o.getMonth() + 1;
			var bDay = o.getDate();
			var bHour = o.getHours();
			var bMinute = o.getMinutes();
			var bSecond = o.getSeconds();

			if ( bMonth < 10 ) bMonth = '0' + bMonth;
			if ( bDay < 10 ) bDay = '0' + bDay;
			if ( bHour < 10 ) bHour = '0' + bHour;
			if ( bMinute < 10 ) bMinute = '0' + bMinute;
			if ( bSecond < 10 ) bSecond = '0' + bSecond;

			if ( fTime )
				return bYear + '-' + bMonth + '-' + bDay + ' ' + bHour + ':' + bMinute + ':' + bSecond;
			else
				return bYear + '-' + bMonth + '-' + bDay;
		}


	}
);
