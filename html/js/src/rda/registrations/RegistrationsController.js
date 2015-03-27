dojo.provide( "rda.registrations.RegistrationsController" );

/******************************************************
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
 ******************************************************/

dojo.require( "rda.common.DController" );
dojo.require( "rda.common.Observer" );

dojo.declare(
	"rda.registrations.RegistrationsController",
	[ rda.common.DController, rda.common.Observer ],
	{
		// Properties
		oView: null,
		oAuthModel: null,
		oServerModel: null,
		oKeyModel: null,
		oKeyModelV2: null,
		oTicketModel: null,
		bSpan: 100,
		sTabCurr: "list",
		ixPage: -1,
		bRefreshId: 0,

		// Server Info
		oServerCurr: null,

		/**
		 * Constructor
		 *
		 * @param oAuthModel
		 *   Currently authenticated user (used to filter certain options)
		 * @param oServerModel
		 *   List of all registered DVS systems
		 * @param oView
		 *   View for this module in MVC
		 */
		constructor: function( oAuthModel, oServerModel, oKeyModel, oKeyModelV2, oTicketModel, oView )
		{
			this.oView = oView;
			this.oAuthModel = oAuthModel;
			this.oServerModel = oServerModel;
			this.oKeyModel = oKeyModel;
			this.oKeyModelV2 = oKeyModelV2;
			this.oTicketModel = oTicketModel;

			this.oView.addActionListener( this );
			this.oServerModel.addObserver( this );
		},

		/**
		 * This function is called by Monarch.js when our
		 * screen is selected and shown on the screen.  We
		 * should initialize our state from this function.
		 */
		activate: function()
		{
			// Enable/disable Kill feature based on user
			if ( this.oAuthModel.checkIsLoaded() && this.oAuthModel.getName() == "rayers" )
				this.oView.toggleKill( true );
			else
				this.oView.toggleKill( false );

			this.changeTab( "change-tab-list" );

			if ( this.oServerModel.checkIsLoaded() ) return;
			this.oView.startLoading();
			this.oServerModel.load();
			this.oView.finishLoading();
			if ( ! this.oServerModel.checkIsLoaded() )
				this.throwAction( "backend-failed" );

			this.oKeyModelV2.load();
		},

		/**
		 * If we need to do any deactivation, like clearing
		 * Models to free memory, etc.  It should be done here.
		 */
		deactivate: function()
		{
			this.changeTab( "change-tab-list" );

			this.oKeyModelV2.reset();
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
			console.debug( "RegistrationsController received action [" + sCommand + "]" );

			var rgs = sCommand.split( "-" );

			if ( ( rgs[ 0 ] == "screen" ) && ( rgs[ 1 ] == "change" ) )
				this.throwAction( sCommand );

			else if ( ( rgs[ 0 ] == "change" ) && ( rgs[ 1 ] == "tab" ) )
				// Show a new tab (Server List, Server Info, Product Key Info)
				this.changeTab( sCommand );

			else if ( ( rgs[ 0 ] == "change" ) && ( rgs[ 1 ] == "list" ) && ( rgs[ 2 ] == "page" ) )
				// Update Server List table with new "page" of servers
				this.changeListPage( parseInt( rgs[ 3 ] ) );

			else if ( ( rgs[ 0 ] == "jump" ) && ( rgs[ 1 ] == "server" ) )
				// Open new tab in Browser for this DVS login page
				this.jumpServer( parseInt( rgs[ 2 ] ) );

			else if ( ( rgs[ 0 ] == "show" ) && ( rgs[ 1 ] == "ticket" ) )
				// Open new tab in Browser for this Bugzilla Bug
				this.showTicket( parseInt( rgs[ 2 ] ) );

			else if ( sCommand == "server-info-cancel" )
				// Reset server information to default
				this.cancelServerInfo();

			else if ( sCommand == "server-info-apply" )
				// Save server info changes to server
				this.applyServerInfo();

			else if ( sCommand == "server-info-open" )
				// Open Ticket for this server in Bugzilla
				this.openTicket();

			else if ( sCommand == "server-info-maint" )
				// Open Maintenance Ticket for this server in Bugzilla
				this.openMaintTicket();

			else if ( sCommand == "show-search-help" )
				// Show example searches
				this.oView.showSearchHelp();

			else if ( ( rgs[ 0 ] == "list" ) && ( rgs[ 1 ] == "search" ) && ( rgs[ 2 ] == "serial" ) )
				// Jump straight to Serial (We don't actually "filter" by serial yet)
				this.changeTab( "change-tab-info-serial-" + rgs[ 3 ] );

			else if ( ( rgs[ 0 ] == "list" ) && ( rgs[ 1 ] == "search" ) && ( rgs[ 2 ] == "string" ) )
				// Filter search list by name/company
				this.filterServerListString( rgs[ 3 ] );

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "seed" ) )
				// Handle new Product Key Seed search
				this.handleKeySeed( parseInt( rgs[ 3 ] ) );

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "seedv2" ) )
				// Handle new Product Key Seed search
				this.handleKeySeedV2( rgs[ 3 ] );

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "feature" ) && ( rgs[ 3 ] == "add" ) )
				// Prompt to add new feature to key
				this.addFeature();

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "feature" ) && ( rgs[ 3 ] == "remove" ) )
				// Prompt to remove feature from key
				this.removeFeature();

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "postype" ) && ( rgs[ 3 ] == "add" ) )
				// Prompt to add new pos-type to key
				this.addPosType();

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "postype" ) && ( rgs[ 3 ] == "remove" ) )
				// Prompt to remove pos-type from key
				this.removePosType();

			else if ( ( rgs[ 0 ] == "product" ) && ( rgs[ 1 ] == "key" ) && ( rgs[ 2 ] == "dialog" ) && ( rgs[ 3 ] == "ok" ) )
				// Prompt to remove pos-type from key
				this.handleAddRemove();

			else if ( ( rgs[ 0 ] == "list" ) && ( rgs[ 1 ] == "search" ) && ( rgs[ 2 ] == "version" ) )
				// Filter search list by version upgrade status
				this.filterServerListVersion( rgs[ 3 ] );

			else if ( ( rgs[ 0 ] == "list" ) && ( rgs[ 1 ] == "search" ) && ( rgs[ 2 ] == "distro" ) )
				// Filter search list by distro upgrade status
				this.filterServerListDistro( rgs[ 3 ] );

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
			if ( ! oObj.checkIsLoaded() ) return;

			// Setup Page Links
			if ( ! this.oView.isListPageSetup() ) {
				var bNum = Math.ceil( oObj.getList().length / this.bSpan ) + 1;
				this.oView.setListPage( bNum, this.bSpan );
			}

			if ( this.oServerCurr != null ) {
				// Update Server Info tab that is being displayed
				var oServerCurr = this.oServerModel.getServerBySerial( this.oServerCurr.getSerial() );
				this.oView.setServer( this.oServerCurr, oServerCurr );
				this.oServerCurr = oServerCurr;

				// Update this server info in our table list
				if ( this.ixRow >= 0 )
					this.oView.setListValues( this.ixRow, oServerCurr );

			} else {
				// Select first page
				if ( this.ixPage < 0 )
					this.actionPerformed( "change-list-page-1" );

				// Select current page (just does a refresh of our server list)
				else
					this.actionPerformed( "change-list-page-" + this.ixPage );

			}
		},

		/*********************************************
		 * Global Functions
		 *********************************************/

		/**
		 * This "screen" is broken up into several states/tabs.
		 * Server List, Server Info, Product Key Serial info, etc.
		 *
		 * @param sCommand
		 *   Name of tab to change to plus any other "state" information
		 */
		changeTab: function( sCommand )
		{
			if ( this.checkHasChanges() ) {
				// Prompt user to save changes here
				if ( this.oView.promptSaveChanges() )
					this.applyServerInfo();
				else 
					this.cancelServerInfo();
			}

			var rgs = sCommand.split( "-" );

			if ( rgs[ 2 ] == "list" ) {
				this.oView.changeTab( "list" );
				this.oServerCurr = null;
				this.ixRow = -1;
				this.sTabCurr = "list";
				this.setupRefresh();

				// Clear Bug info if it wasn't completed
				this.oView.clearSummary();
				this.oView.clearDescription();

			} else if ( rgs[ 2 ] == "info" ) {
				if ( rgs[ 3 ] == "row" ) {
					this.ixRow = parseInt( rgs[ 5 ] );
					var bSerial = parseInt( this.oView.getListValue( "serial", this.ixRow ) );
				} else {
					var bSerial = parseInt( rgs[ 4 ] );
				}
				try {
					oServerCurr = this.oServerModel.getServerBySerial( bSerial );
					this.oView.setServer( this.oServerCurr, oServerCurr );
					this.oServerCurr = oServerCurr;
					this.oView.changeTab( "info" );
					this.sTabCurr = "info";
					this.setupRefresh();

					// Load and display tickets
					this.oView.setTickets( this.oTicketModel.getTickets( bSerial ) );

				} catch ( e ) {
					console.debug( "Change Tab Error [" + e + "]" );
					this.oView.promptServerNotFound();
				}

			}
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
		 * Server List Functions
		 *********************************************/

		/**
		 * The Server List only shows X number of servers at
		 * a time.  Across the top of this "tab" we have pagination
		 * buttons to navigate 1-100, 101-200, etc.  This function
		 * updates which server group we are showing in the list.
		 *
		 * @param ixPage
		 *   Index of page to show in Server List
		 */
		changeListPage: function( ixPage )
		{
			this.ixPage = ixPage;
			this.oView.selectListPage( ixPage );

			// Update Servers in Grid
			var bStart = ( ixPage - 1 ) * this.bSpan + 1;
			var bEnd = ixPage * this.bSpan;
			var rgoServer = this.oServerModel.getList();
			if ( ixPage == 0 ) { // All
				bStart = 1;
				bEnd = rgoServer[ rgoServer.length - 1 ].getSerial();
			}

			var rgoFiltered = [];
			var ix = 0;
			while ( rgoServer[ ix ].getSerial() < bStart )
				ix++;
			while ( ix < rgoServer.length && rgoServer[ ix ].getSerial() <= bEnd )
				rgoFiltered.push( rgoServer[ ix++ ] );

			this.oView.setServerList( rgoFiltered );
		},

		/**
		 * Do a case-insensitivie regex search on Server Name and Company
		 * and show only those servers in our list.
		 *
		 * @param sName
		 *   Name to filter Server List by
		 */
		filterServerListString: function( sName )
		{
			// Deselect any page buttons
			this.oView.selectListPage( -99 );

			// Update Servers in Grid
			var oMatch = new RegExp( sName, "i" );
			var rgoServer = this.oServerModel.getList();
			var rgoFiltered = [];
			for ( var ix = 0; ix < rgoServer.length; ix++ )
				if ( oMatch.test( rgoServer[ ix ].getName() ) ||
				     oMatch.test( rgoServer[ ix ].getCompany() ) ||
				     oMatch.test( rgoServer[ ix ].getCategories() ) )
					rgoFiltered.push( rgoServer[ ix ] );

			this.oView.setServerList( rgoFiltered );

			this.oView.sortTable( "name" );
		},

		/**
		 * List all DVR's that are eligible for a DVR
		 * version upgrade.
		 *
		 * @param sFilter
		 *   Filter Server List by maint flag
		 */
		filterServerListVersion: function( sFilter )
		{
			// Deselect any page buttons
			this.oView.selectListPage( -99 );

			// Update Servers in Grid
			var rgoServer = this.oServerModel.getList();
			var rgoFiltered = [];
			for ( var ix = 0; ix < rgoServer.length; ix++ ) {
				var sVersion = rgoServer[ ix ].getVersion();
				var sInstalled = rgoServer[ ix ].getVersionInstalled();
				if ( sVersion == '' || sInstalled == '' ) continue;

				// Should we filter down to maint customers only?
				if ( sFilter == 'maint' && rgoServer[ ix ].getMaintenance() == 'no' ) continue;

				var rgsV1 = sVersion.split( '.' );
				var rgsV2 = sInstalled.split( '.' );
				if ( rgsV1[ 0 ] != rgsV2[ 0 ] || rgsV1[ 1 ] != rgsV2[ 1 ] )
					rgoFiltered.push( rgoServer[ ix ] );
			}

			this.oView.setServerList( rgoFiltered );
		},

		/**
		 * List all DVR's that are eligible for a DVR
		 * distro upgrade.
		 *
		 * @param sFilter
		 *   Filter Server List by maint flag
		 */
		filterServerListDistro: function( sFilter )
		{
			// Deselect any page buttons
			this.oView.selectListPage( -99 );

			// Update Servers in Grid
			var rgoServer = this.oServerModel.getList();
			var rgoFiltered = [];
			for ( var ix = 0; ix < rgoServer.length; ix++ ) {
				if ( rgoServer[ ix ].getOS() == '' ) continue;

				// Should we filter down to maint customers only?
				if ( sFilter == 'maint' && rgoServer[ ix ].getMaintenance() == 'no' ) continue;

				// co5 is our latest distro
				if ( rgoServer[ ix ].getOS() != 'co5' )
					rgoFiltered.push( rgoServer[ ix ] );
			}

			this.oView.setServerList( rgoFiltered );
		},

		/**
		 * A POS Key Seed was entered.  We can do one of three things with it:
		 *  - Add new server (serial does not exist)
		 *  - Jump string to server page (key exists and matched)
		 *  - Reset key since something about server changes (mac, pos, etc)
		 */
		handleKeySeedPos: function( bSeed )
		{
			var bSerial = this.oKeyModel.getSerial();
			var bPosLock = this.oKeyModel.getPosLock();
			var sMac = this.oKeyModel.getMac();

			// Range check variables
			if ( ( bSerial < 1 || bSerial > 4096 ) ||
			     ( parseInt( sMac, 16 ) > 255 ) ) {
				this.oView.promptSeedInvalid();
				return;
			}

			var oServer = null;
			try {
				oServer = this.oServerModel.getServerBySerial( bSerial );
			} catch ( e ) {}

			// Server does not exist, add?
			if ( oServer == null ) {
				this.oView.promptServerNotFound();
				return;
			}
			
			// Key information is all the same, just display
			if (
			     ( oServer.getPosLock() == bPosLock ) &&
			     ( oServer.getMac() == sMac ) ) {
			     
			     this.oView.promptPosLock();
			   
				this.changeTab( "change-tab-info-serial-" + bSerial );
				return;
			}

			// Key information does not match, prompt reset?
			var sKey = this.oKeyModel.makeKeyPos( oServer.getSerial(), bPosLock, sMac );
			if ( this.oView.promptKeyInvalid( oServer, sKey, bPosLock, sMac ) ) {
				// Reset server key information
				
				oServer.setNumcam( 1);
				oServer.setPosLock( bPosLock );
				oServer.setMac( sMac );
				this.oServerModel.setServer( oServer );
				this.changeTab( "change-tab-info-serial-" + bSerial );
			} 
		},
	
		/**
		 * A Product Key Seed was entered.  We can do one of three things with it:
		 *  - Add new server (serial does not exist)
		 *  - Jump string to server page (key exists and matched)
		 *  - Reset key since something about server changes (mac, numcam, etc)
		 */
		handleKeySeed: function( bSeed )
		{
			if ( ! this.oKeyModel.load( bSeed ) ) {
				alert( "Unable to parse Seed." );
				return;
			}

			if ( this.oKeyModel.isPosSeed() ) {
				this.handleKeySeedPos( bSeed );
				return;
			}
			
			var bSerial = this.oKeyModel.getSerial();
			var sVersion = this.oKeyModel.getVersion();
			var bNumcam = this.oKeyModel.getNumcam();
			var sMac = this.oKeyModel.getMac();

			// Range check variables
			if ( ( bSerial < 1 || bSerial > 4096 ) ||
			     ( sVersion != "2.0" && sVersion != "2.5" && sVersion != "3.0" && sVersion != "3.1" && sVersion != "3.2" && sVersion != "3.3" && sVersion != "3.4" ) ||
			     ( bNumcam != 4 && bNumcam != 8 && bNumcam != 16 ) ||
			     ( parseInt( sMac, 16 ) > 255 ) ) {
				this.oView.promptSeedInvalid();
				return;
			}

			var oServer = null;
			try {
				oServer = this.oServerModel.getServerBySerial( bSerial );
			} catch ( e ) {}

			// Server does not exist, add?
			if ( oServer == null ) {
				var sKey = this.oKeyModel.makeKeyDVS( bSerial, sVersion, bNumcam, sMac );
				if ( this.oView.promptAddServer( sKey, bSerial, sVersion, bNumcam, sMac ) ) {
					try {
						this.oServerModel.addServer( bSerial, sVersion, bNumcam, sMac );
					} catch ( e ) {
						console.debug( "Handle Key Seed Error [" + e + "]" );
						alert( "Error adding server." );
						return;
					}
					this.changeTab( "change-tab-info-serial-" + bSerial );
				}
				return;
			}

			// Key information is all the same, just display
			if ( ( oServer.getVersion() == sVersion ) &&
			     ( oServer.getNumcam() == bNumcam ) &&
			     ( oServer.getMac() == sMac ) ) {
				this.changeTab( "change-tab-info-serial-" + bSerial );
				return;
			}

			// Key information does not match, prompt reset?
			var sKey = this.oKeyModel.makeKeyDVS( oServer.getSerial(), sVersion, bNumcam, sMac );
			if ( this.oView.promptKeyInvalid( oServer, sKey, sVersion, bNumcam, sMac ) ) {
				// Reset server key information
				oServer.setVersion( sVersion );
				oServer.setNumcam( bNumcam );
				oServer.setMac( sMac );
				this.oServerModel.setServer( oServer );
				this.changeTab( "change-tab-info-serial-" + bSerial );
			}
		},

		/**
		 * A Product Key Seed V2 was entered.  We can do one of three things with it:
		 *  - Add new server (seed not assigned to any existing system)
		 *  - Jump string to server page (key exists and matched)
		 */
		handleKeySeedV2: function( sSeed )
		{
			var oServer = null;
			try {
				oServer = this.oServerModel.getServerBySeed( sSeed );
			} catch ( e ) {}

			// Server does not exist, add?
			if ( oServer == null ) {
				if ( this.oView.promptAddServerV2( sSeed ) ) {
					try {
						oServer = this.oServerModel.addServerV2( sSeed );
					} catch ( e ) {
						console.debug( "Handle Key Seed V2 Error [" + e + "]" );
						alert( "Error adding server by seed." );
						return;
					}
				}
			}

			if ( oServer == null ) {
				alert( 'Cannot add server' );
				return;
			}

			this.changeTab( "change-tab-info-serial-" + oServer.getSerial() );
		},

		addFeature: function()
		{
			this.oView.promptAddRemove( 'feature', 'add', this.oView.getFeatures(), this.oKeyModelV2.getFeatures() )
		},

		removeFeature: function()
		{
			this.oView.promptAddRemove( 'feature', 'remove', this.oView.getFeatures(), this.oKeyModelV2.getFeatures() )
		},

		addPosType: function()
		{
			this.oView.promptAddRemove( 'postype', 'add', this.oView.getPosTypes(), this.oKeyModelV2.getPosTypes() )
		},

		removePosType: function()
		{
			this.oView.promptAddRemove( 'postype', 'remove', this.oView.getPosTypes(), this.oKeyModelV2.getPosTypes() )
		},

		handleAddRemove: function()
		{
			this.oView._dlgAddRemove.hide()

			var sType = this.oView.getAddRemoveType();
			var sValue = this.oView.getAddRemoveValue();

			if ( sValue == '' ) return;

			var rgs = sType.split( '-' );
			if ( rgs[ 0 ] == 'feature' ) {
				// Feature
				if ( rgs[ 1 ] == 'add' ) {
					var s = this.oView.getFeatures();
					if ( s != '' )
						s += ',';
					s += sValue;
					this.oView.setFeatures( s );

				} else {
					var rgs = this.oView.getFeatures().split( ',' );
					var s = '';
					for ( var ix = 0; ix < rgs.length; ix++ ) {
						if ( rgs[ ix ] == sValue ) continue;
						if ( s != '' )
							s += ',';
						s += rgs[ ix ];
					}
					this.oView.setFeatures( s );

				}

			} else {
				// Pos Type
				if ( rgs[ 1 ] == 'add' ) {
					var s = this.oView.getPosTypes();
					if ( s != '' )
						s += ',';
					s += sValue;
					this.oView.setPosTypes( s );

				} else {
					var rgs = this.oView.getPosTypes().split( ',' );
					var s = '';
					for ( var ix = 0; ix < rgs.length; ix++ ) {
						if ( rgs[ ix ] == sValue ) continue;
						if ( s != '' )
							s += ',';
						s += rgs[ ix ];
					}
					this.oView.setPosTypes( s );

				}
			
			}

		},

		/*********************************************
		 * Server Info Functions
		 *********************************************/

		/**
		 * Check if there are any changes to our Server Info object
		 *
		 * @return True if there are changes, False otherwise
		 */
		checkHasChanges: function()
		{
			if ( this.oServerCurr == null ) return;
			var oServer = this.oServerCurr;
			var oView = this.oView;

			if ( oServer.getName() != oView.getName() )
				return true;

			if ( oServer.getCompany() != oView.getCompany() )
				return true;

			if ( oServer.getInstallPretty() != oView.getInstall() )
				return true;

			if ( oServer.getMaintenance() != oView.getMaintenance() )
				return true;

			if ( oServer.getMaintenanceOnsitePretty() != oView.getMaintenanceOnsite() )
				return true;

			if ( oServer.checkHasSkip() != oView.checkHasSkip() )
				return true;

			if ( oServer.getHostname() != oView.getHostname() )
				return true;

			if ( oServer.getCategories() != oView.getCategories() )
				return true;

			if ( oServer.getPreferred() != oView.getPreferred() )
				return true;

			if ( oServer.getKill() != oView.getKill() )
				return true;

			if ( oServer.getKey() != oView.getKey() )
				return true;

			if ( oServer.getVersion() != oView.getVersion() )
				return true;

			if ( oServer.getNumcam() != oView.getNumcam() )
				return true;

			if ( oServer.getPosKey() != oView.getPosKey() )
				return true;
				
			if ( oServer.getPosLock() != oView.getPosLock() )
				return true;
				
			if ( oServer.getMac() != oView.getMac() )
				return true;

			if ( oServer.getSeed() != oView.getSeed() )
				return true;

			if ( oServer.getFeatures() != oView.getFeatures() )
				return true;

			if ( oServer.getPosTypes() != oView.getPosTypes() )
				return true;

			if ( oServer.getLprLock() != oView.getLprLock() )
				return true;
				
			if ( oServer.checkHasEnterprise() != oView.checkHasEnterprise() )
				return true;

			if ( oServer.checkHasAuth() != oView.checkHasAuth() )
				return true;

			return false;
		},

		/**
		 * Cancel all changes to Server Info
		 */
		cancelServerInfo: function()
		{
			if ( this.oServerCurr == null ) {
				console.debug( "BUG: how can we cancel if there is no server selected?" );
				return;
			}

			this.oView.setServer( null, this.oServerCurr );

			this.changeTab( "change-tab-list" );
		},

		/**
		 * Save changes to Server Info object to database.
		 */
		applyServerInfo: function()
		{
			if ( this.oServerCurr == null ) {
				console.debug( "BUG: how can we save changes if there is no server selected?" );
				return;
			}
			var oServer = this.oServerCurr;
			var oView = this.oView;

			oServer.setName( oView.getName() );
			oServer.setCompany( oView.getCompany() );
			oServer.setInstallPretty( oView.getInstall() );
			oServer.setMaintenance( oView.getMaintenance() );
			oServer.setMaintenanceOnsitePretty( oView.getMaintenanceOnsite() );
			oServer.setSkip( oView.checkHasSkip() );
			oServer.setHostname( oView.getHostname() );
			oServer.setCategories( oView.getCategories() );
			oServer.setPreferred( oView.getPreferred() );
			oServer.setKill( oView.getKill() );
			oServer.setKey( oView.getKey() );
			oServer.setVersion( oView.getVersion() );
			oServer.setNumcam( oView.getNumcam() );
			oServer.setPosKey( oView.getPosKey() );
			oServer.setPosLock( oView.getPosLock() );
			oServer.setMac( oView.getMac() );
			oServer.setEnterprise( oView.checkHasEnterprise() );
			oServer.setAuth( oView.checkHasAuth() );
			oServer.setSeed( oView.getSeed() );
			oServer.setFeatures( oView.getFeatures() );
			oServer.setPosTypes( oView.getPosTypes() );
			oServer.setLprLock( oView.getLprLock() );

			this.oServerCurr = oServer;
			this.oServerModel.setServer( this.oServerCurr );
		},

		/**
		 * Setup refresh to pull updated information from server while we are loaded
		 */
		setupRefresh: function()
		{
			// Cancel existing refresh cycle
			if ( this.bRefreshId != 0 ) {
				clearInterval( this.bRefreshId );
				this.bRefreshId = 0;
			}

			if ( this.sTabCurr == "list" ) {
				this.bRefreshId = setInterval( dojo.hitch( this, "refreshData" ), 600000 );

			} else if ( this.sTabCurr == "info" ) {
				this.bRefreshId = setInterval( dojo.hitch( this, "refreshData" ), 10000 );

			}

			this.refreshData();
		},

		/**
		 * Refresh our ServerModel data
		 */
		refreshData: function()
		{
			//console.debug( "Refreshing server data" );
			if ( this.sTabCurr == "list" ) {
				var rgb = this.oView.getSerials();
				var rgbSerial = new Array();
				for ( var ix = 0, ix2 = 0; ix < rgb.length; ix++ ) {
					try {
						var oServer = this.oServerModel.getServerBySerial( rgb[ ix ] );
						if ( ! oServer.checkRefreshListNeeded() ) continue;
						rgbSerial[ ix2++ ] = rgb[ ix ];
					} catch ( e ) {}
				}
				if ( rgbSerial.length > 0 )
					this.oServerModel.loadSerials( rgbSerial );

			} else if ( this.sTabCurr == "info" ) {
				if ( this.oServerCurr == null ) return;
				if ( ! this.oServerCurr.checkRefreshInfoNeeded() ) return;
				this.oServerModel.loadSerial( this.oServerCurr.getSerial() );

			}
		},

		/**
		 * Open Ticket in Bugzilla for currently display Serial
		 */
		openTicket: function()
		{
			if ( this.oServerCurr == null ) {
				console.debug( "BUG: how can we open a ticket if there is no server selected?" );
				return;
			}

			sSummary = this.oView.getSummary();
			sDesc = this.oView.getDescription();

			if ( sSummary == '' || sDesc == '' ) {
				alert( 'You must specify a Summary and Description before we can open a ticket.');
				return;
			}

			if ( ! this.oTicketModel.openTicket( this.oServerCurr.getSerial(), sSummary, sDesc ) ) {
				alert( "Unable to open ticket." );
				return;
			}

			this.oView.clearSummary();
			this.oView.clearDescription();

			alert( "Opened service ticket for scheduling." );
		},

		/**
		 * Open Maintenance Ticket in Bugzilla for currently display Serial
		 */
		openMaintTicket: function()
		{
			if ( this.oServerCurr == null ) {
				console.debug( "BUG: how can we open a ticket if there is no server selected?" );
				return;
			}

			if ( ! this.oTicketModel.openMaintTicket( this.oServerCurr.getSerial() ) ) {
				alert( "Unable to open maintenance ticket." );
				return;
			}

			alert( "Opened maintenance ticket for scheduling." );
		},

		/**
		 * Open a new tab with Bugzilla ticket pulled up
		 *
		 * @param bID
		 *   Bug ID
		 */
		showTicket: function( bID )
		{
			// Build jump string
			var sUrl = "http://tickets.dividia.net/show_bug.cgi?id=" + bID;

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
