/**
 *
 * Server Object holds the properties for each registered DVS.
 *
 * @author Ryan Ayers and assisted by Jake Tansey
 */

dojo.provide( "rda.backend.config.Server" );

dojo.declare(
	"rda.backend.config.Server",
	null,
	{
		_bSerial: 0,
		_bController: 0,
		_sCompany: "",
		_sName: "",
		_sCategories: "",
		_sPreferred: "",
		_sIP: "",
		_sRemoteIP: "",
		_sLocalIP: "",
		_bPort: 0,
		_bSshPort: 0,
		_sHostname: '',
		_bTimestamp: 0,
		_bInstall: 0,
		_sMaintenance: "",
		_bMaintenanceOnsite: 0,
		_fSkip: false,
		_fSick: false,
		_sOS: "",
		_sVersionInstalled: "",
		_sVersion: "",
		_bNumcam: 0,
		_sMac: "",
		_sKey: "",
		_sPosKey: "",
		_bPosLock: 0,
		_sKill: "",
		_fEnterprise: false,
		_fAuth: false,
		_sSeed: "",
		_sFeatures: "",
		_sPosTypes: "",
		_bLprLock: 0,

		_bTimeDiffMax: 36000,
		_bTimeDiffRefreshList: 3600, // 1 hour
		_bTimeDiffRefreshInfo: 10,   // 10 seconds

		// This is used to see if we need to pull a refresh from the server for this data
		_bServerSyncLast: 0,

		/**
		 * Creates a new instance of our Server Object
		 */
		constructor: function()
		{
			if ( arguments.length > 0 )
				this.load( arguments[ 0 ] );
		},

		/**
		 * Load Hash from server into our structure
		 */
		load: function( rgsServer )
		{
			for ( var sKey in rgsServer ) {
				if ( sKey == "bSerial" )
					this._bSerial = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "bController" )
					this._bController = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "sCompany" )
					this._sCompany = String( rgsServer[ sKey ] );
				else if ( sKey == "sName" )
					this._sName = String( rgsServer[ sKey ] );
				else if ( sKey == "sCategories" )
					this._sCategories = String( rgsServer[ sKey ] );
				else if ( sKey == "sPreferred" )
					this._sPreferred = String( rgsServer[ sKey ] );
				else if ( sKey == "sIP" )
					this._sIP = String( rgsServer[ sKey ] );
				else if ( sKey == "sRemoteIP" )
					this._sRemoteIP = String( rgsServer[ sKey ] );
				else if ( sKey == "sLocalIP" )
					this._sLocalIP = String( rgsServer[ sKey ] );
				else if ( sKey == "bPort" )
					this._bPort = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "bSshPort" )
					this._bSshPort = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "sHostname" )
					this._sHostname = String( rgsServer[ sKey ] );
				else if ( sKey == "bTimestamp" )
					this._bTimestamp = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "bInstall" )
					this._bInstall = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "sMaintenance" )
					this._sMaintenance = String( rgsServer[ sKey ] );
				else if ( sKey == "bMaintenanceOnsite" )
					this._bMaintenanceOnsite = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "fSkip" )
					this._fSkip = new Boolean( rgsServer[ sKey ] );
				else if ( sKey == "fSick" )
					this._fSick = new Boolean( rgsServer[ sKey ] );
				else if ( sKey == "sOS" )
					this._sOS = String( rgsServer[ sKey ] );
				else if ( sKey == "sVersionInstalled" )
					this._sVersionInstalled = String( rgsServer[ sKey ] );
				else if ( sKey == "sVersion" )
					this._sVersion = String( rgsServer[ sKey ] );
				else if ( sKey == "bNumcam" )
					this._bNumcam = parseInt( rgsServer[ sKey ] );
				else if ( sKey == "sMac" )
					this._sMac = String( rgsServer[ sKey ] );
				else if ( sKey == "sKey" )
					this._sKey = String( rgsServer[ sKey ] );
				else if ( sKey == "sPosKey" )
					this._sPosKey = String( rgsServer[ sKey ] );	
				else if ( sKey == "bPosLock" )
					this._bPosLock = parseInt( rgsServer[ sKey ] );		
				else if ( sKey == "sKill" )
					this._sKill = String( rgsServer[ sKey ] );
				else if ( sKey == "fEnterprise" )
					this._fEnterprise = new Boolean( rgsServer[ sKey ] );
				else if ( sKey == "fAuth" )
					this._fAuth = new Boolean( rgsServer[ sKey ] );
				else if ( sKey == "sSeed" )
					this._sSeed = String( rgsServer[ sKey ] );
				else if ( sKey == "sFeatures" )
					this._sFeatures = String( rgsServer[ sKey ] );
				else if ( sKey == "sPosTypes" )
					this._sPosTypes = String( rgsServer[ sKey ] );
				else if ( sKey == "bLprLock" )
					this._bLprLock = parseInt( rgsServer[ sKey ] );		
			}

			// Store this load time as our last server sync time
			var oDate = new Date();
			this._bServerSyncLast = parseInt( oDate.getTime() / 1000 );
		},

		/**
		 * Return a Hash of our object ready to send back to server
		 */
		freeze: function()
		{
			var rgs = new Object();

			rgs[ "bSerial" ] = this._bSerial;
			rgs[ "bController" ] = this._bController;
			rgs[ "sCompany" ] = this._sCompany;
			rgs[ "sName" ] = this._sName;
			rgs[ "sCategories" ] = this._sCategories;
			rgs[ "sPreferred" ] = this._sPreferred;
			rgs[ "sIP" ] = this._sIP;
			rgs[ "sRemoteIP" ] = this._sRemoteIP;
			rgs[ "sLocalIP" ] = this._sLocalIP;
			rgs[ "bPort" ] = this._bPort;
			rgs[ "bSshPort" ] = this._bSshPort;
			rgs[ "sHostname" ] = this._sHostname;
			rgs[ "bTimestamp" ] = this._bTimestamp;
			rgs[ "bInstall" ] = this._bInstall;
			rgs[ "sMaintenance" ] = this._sMaintenance;
			rgs[ "bMaintenanceOnsite" ] = this._bMaintenanceOnsite;
			rgs[ "fSkip" ] = this._fSkip;
			rgs[ "fSick" ] = this._fSick;
			rgs[ "sOS" ] = this._sOS;
			rgs[ "sVersionInstalled" ] = this._sVersionInstalled;
			rgs[ "sVersion" ] = this._sVersion;
			rgs[ "bNumcam" ] = this._bNumcam;
			rgs[ "sMac" ] = this._sMac;
			rgs[ "sKey" ] = this._sKey;
			rgs[ "sPosKey" ] = this._sPosKey;
			rgs[ "bPosLock" ] = this._bPosLock;
			rgs[ "sKill" ] = this._sKill;
			rgs[ "fEnterprise" ] = this._fEnterprise;
			rgs[ "fAuth" ] = this._fAuth;
			rgs[ "sSeed" ] = this._sSeed;
			rgs[ "sFeatures" ] = this._sFeatures;
			rgs[ "sPosTypes" ] = this._sPosTypes;
			rgs[ "bLprLock" ] = this._bLprLock;

			return rgs;
		},

		getSerial: function()
		{
			return this._bSerial;
		},
		setSerial: function( bSerial )
		{
			this._bSerial = bSerial;
		},

		getController: function()
		{
			return this._bController;
		},
		setController: function( bController )
		{
			this._bController = bController;
		},

		getCompany: function()
		{
			return this._sCompany;
		},
		setCompany: function( sCompany )
		{
			this._sCompany = sCompany;
		},

		getName: function()
		{
			return this._sName;
		},
		setName: function( sName )
		{
			this._sName = sName;
		},

		getCategories: function()
		{
			return this._sCategories;
		},
		setCategories: function( sCategories )
		{
			this._sCategories = sCategories;
		},

		getPreferred: function()
		{
			return this._sPreferred;
		},
		setPreferred: function( sPreferred )
		{
			this._sPreferred = sPreferred;
		},

		getIP: function()
		{
			return this._sIP;
		},
		setIP: function( sIP )
		{
			this._sIP = sIP;
		},

		getRemoteIP: function()
		{
			return this._sRemoteIP;
		},
		setRemoteIP: function( sRemoteIP )
		{
			this._sRemoteIP = sRemoteIP;
		},

		getLocalIP: function()
		{
			return this._sLocalIP;
		},
		setLocalIP: function( sLocalIP )
		{
			this._sLocalIP = sLocalIP;
		},

		getPort: function()
		{
			return this._bPort;
		},
		setPort: function( bPort )
		{
			this._bPort = bPort;
		},

		getSshPort: function()
		{
			return this._bSshPort;
		},
		setSshPort: function( bSshPort )
		{
			this._bSshPort = bSshPort;
		},

		getHostname: function()
		{
			return this._sHostname;
		},
		setHostname: function( sHostname )
		{
			this._sHostname = sHostname;
		},

		getTimestamp: function()
		{
			return this._bTimestamp;
		},
		setTimestamp: function( bTimestamp )
		{
			this._bTimestamp = bTimestamp;
		},
		checkIsAlive: function()
		{
			var oDate = new Date();
			var bNow = parseInt( oDate.getTime() / 1000 );
			return this._bTimeDiffMax > bNow - this._bTimestamp;
		},
		getTimestampPretty: function()
		{
			return this._toPretty( this._bTimestamp, true );
		},
		setTimestampPretty: function( sTimestamp )
		{
			this._bTimestamp = this._fromPretty( sTimestamp, true );
		},

		getInstall: function()
		{
			return this._bInstall;
		},
		setInstall: function( bInstall )
		{
			this._bInstall = bInstall;
		},
		getInstallPretty: function()
		{
			return this._toPretty( this._bInstall, false );
		},
		setInstallPretty: function( sInstall )
		{
			this._bInstall = this._fromPretty( sInstall, false );
		},

		getMaintenance: function()
		{
			return this._sMaintenance;
		},
		setMaintenance: function( sMaintenance )
		{
			this._sMaintenance = sMaintenance;
		},

		getMaintenanceOnsite: function()
		{
			return this._bMaintenanceOnsite;
		},
		setMaintenanceOnsite: function( bMaintenanceOnsite )
		{
			this._bMaintenanceOnsite = bMaintenanceOnsite;
		},
		getMaintenanceOnsitePretty: function()
		{
			return this._toPretty( this._bMaintenanceOnsite, false );
		},
		setMaintenanceOnsitePretty: function( sMaintenanceOnsite )
		{
			this._bMaintenanceOnsite = this._fromPretty( sMaintenanceOnsite, false );
		},

		checkHasSkip: function()
		{
			return ( this._fSkip == true ) ? true : false;
		},
		setSkip: function( fSkip )
		{
			this._fSkip = fSkip;
		},

		checkIsSick: function()
		{
			return ( this._fSick == true ) ? true : false;
		},
		setSick: function( fSick )
		{
			this._fSick = fSick;
		},

		getOS: function()
		{
			return this._sOS;
		},
		setOS: function( sOS )
		{
			this._sOS = sOS;
		},

		getVersionInstalled: function()
		{
			return this._sVersionInstalled;
		},
		setVersionInstalled: function( sVersionInstalled )
		{
			this._sVersionInstalled = sVersionInstalled;
		},

		getVersion: function()
		{
			return this._sVersion;
		},
		setVersion: function( sVersion )
		{
			this._sVersion = sVersion;
		},

		getNumcam: function()
		{
			return this._bNumcam;
		},
		setNumcam: function( bNumcam )
		{
			this._bNumcam = bNumcam;
		},

		getMac: function()
		{
			return this._sMac;
		},
		setMac: function( sMac )
		{
			this._sMac = sMac;
		},

		getKey: function()
		{
			return this._sKey;
		},
		setKey: function( sKey )
		{
			this._sKey = sKey;
		},
		
		getPosKey: function()
		{
			return this._sPosKey;
		},
		setPosKey: function( sPosKey )
		{
			this._sPosKey = sPosKey;
		},
		
		getPosLock: function()
		{
			return this._bPosLock;
		},
		setPosLock: function( bPosLock )
		{
			this._bPosLock = bPosLock;
		},

		getKill: function()
		{
			return this._sKill;
		},
		setKill: function( sKill )
		{
			this._sKill = sKill;
		},

		checkHasEnterprise: function()
		{
			return ( this._fEnterprise == true ) ? true : false;
		},
		setEnterprise: function( fEnterprise )
		{
			this._fEnterprise = fEnterprise;
		},

		checkHasAuth: function()
		{
			return ( this._fAuth == true ) ? true : false;
		},
		setAuth: function( fAuth )
		{
			this._fAuth = fAuth;
		},

		getSeed: function()
		{
			return this._sSeed;
		},
		setSeed: function( sSeed )
		{
			this._sSeed = sSeed;
		},

		getFeatures: function()
		{
			return this._sFeatures;
		},
		setFeatures: function( sFeatures )
		{
			this._sFeatures = sFeatures;
		},

		getPosTypes: function()
		{
			return this._sPosTypes;
		},
		setPosTypes: function( sPosTypes )
		{
			this._sPosTypes = sPosTypes;
		},

		getLprLock: function()
		{
			return this._bLprLock;
		},
		setLprLock: function( bLprLock )
		{
			this._bLprLock = bLprLock;
		},

		getServerSyncLast: function()
		{
			return this._bServerSyncLast;
		},
		checkRefreshListNeeded: function()
		{
			var oDate = new Date();
			var bNow = parseInt( oDate.getTime() / 1000 );
			return this._bTimeDiffRefreshList < bNow - this._bServerSyncLast;
		},
		checkRefreshInfoNeeded: function()
		{
			var oDate = new Date();
			var bNow = parseInt( oDate.getTime() / 1000 );
			return this._bTimeDiffRefreshInfo < bNow - this._bServerSyncLast;
		},

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
		},

		_fromPretty: function( sTimestamp, fTime )
		{
			var o = new Date();

			o.setFullYear( sTimestamp.substr( 0, 4 ) )
			o.setMonth( sTimestamp.substr( 5, 2 ) - 1 );
			o.setDate( sTimestamp.substr( 8, 2 ) );
			o.setHours( 0 );
			o.setMinutes( 0 );
			o.setSeconds( 0 );

			if ( fTime ) {
				o.setHours( sTimestamp.substr( 11, 2 ) );
				o.setMinutes( sTimestamp.substr( 14, 2 ) );
				o.setSeconds( sTimestamp.substr( 17, 2 ) );
			}

			return parseInt( o.getTime() / 1000 );
		}

	}
);
