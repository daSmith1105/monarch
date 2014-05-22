/**
 *
 * Load Product Key information based on Seed
 * Serial, Version, Numcam, Mac
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.KeyModel" );

dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.Server" );

dojo.declare(
	"rda.backend.KeyModel",
	[],
	{
		_sSess: "",
		_oStore: null,
		_bSerial: 0,
		_sVersion: "",
		_bNumcam: 0,
		_bPosLock: 0,
		_fIsPosSeed: false,
		_sMac: "",

		constructor: function()
		{
			this._oStore = rda.config.Store.getInstance();

			this.reset();
		},

		/**
		 * Call backend to decompose product key seed.
		 *
		 * @param bSeed
		 *   Product Key Seed to decompose
		 *
		 * @return true/false decompose status
		 */
		 
		 isPosSeed: function ()
		 {
		 
		 return this._fIsPosSeed;
		 
		 },
		loadDVS: function( bSeed )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				rgoResult = oServer.Query( "key.decomposeSeed", this._sSess, String( bSeed ) );

				this._bSerial = rgoResult[ 0 ];
				this._sVersion = rgoResult[ 1 ];
				this._bNumcam = rgoResult[ 2 ];
				this._sMac = rgoResult[ 3 ];

				return true;

			} catch ( e ) {
				console.debug( "Key Model Load [" + e + "]" );
				alert( "Error decomposing DVS product key seed" );
				return false;
			}
		},

		loadPos: function( bSeed )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				rgoResult = oServer.Query( "key.decomposeSeedPos", this._sSess, String( bSeed ) );

				this._bSerial = rgoResult[ 0 ];
				this._bPosLock = rgoResult[ 1 ];
				this._sMac = rgoResult[ 2 ];

				return true;

			} catch ( e ) {
				console.debug( "Key Model Load [" + e + "]" );
				alert( "Error decomposing Pos product key seed" );
				return false;
			}
		},

		load: function( bSeed )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				oResult = oServer.Query( "key.isPosSeed", this._sSess, String( bSeed ) );
				
				this._fIsPosSeed = oResult;
				if ( oResult )
				{
					this.loadPos( bSeed );
				}
				
				else
				
				{
					this.loadDVS( bSeed );
				}
				
				return true;
				
			} catch ( e ) {
				console.debug( "Key Model Load [" + e + "]" );
				alert( "Error decomposing product key seed" );
				return false;
			}
		},
	
		/**
		 * Call backend to retrieve the Product Key for this serial
		 *
		 * @param bSerial
		 *   Serial ID of Server
		 * @param sVersion
		 *   Version installed on Server
		 * @param bNumcam
		 *   Number of cameras supported on system
		 * @param sMac
		 *   Mac address to lock serial to
		 *
		 * @return String of product key
		 */
		makeKeyDVS: function( bSerial, sVersion, bNumcam, sMac )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				sKey = oServer.Query( "key.makeKey", this._sSess, bSerial, sVersion, bNumcam, sMac );

				return sKey;

			} catch ( e ) {
				alert( "Error making product key" );
				console.log( "Key Model makeKeyDVS [" + e + "]" );
				return "";
			}
		},
		
		makeKeyPos: function( bSerial, bPosLock, sMac )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				sKey = oServer.Query( "key.makeKey", this._sSess, bSerial, bPosLock, sMac );

				return sKey;

			} catch ( e ) {
				alert( "Error making product key" );
				console.log( "Key Model makeKeyPos [" + e + "]" );
				return "";
			}
		},

		/**
		 * Call backend to retrieve the Product Key for this seed
		 *
		 * @param bSeed
		 *   Product Key Seed to decompose
		 *
		 * @return String of product key
		 */
		getKeyDVS: function( bSeed )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				var rgs = oServer.Query( "key.getKeyDVS", String( bSeed ) );

				if ( ! rgs[ 0 ] )
					throw new Error( rgs[ 1 ] );

				return rgs[ 1 ];

			} catch ( e ) {
				alert( "Error getting product key" );
				console.log( "Key Model getKeyDvs [" + e + "]" );
				return "";
			}
		},
		
		getKeyPos: function( bSeed )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				var rgs = oServer.Query( "key.getKeyPos", String( bSeed ) );

				if ( ! rgs[ 0 ] )
					throw new Error( rgs[ 1 ] );

				return rgs[ 1 ];

			} catch ( e ) {
				alert( "Error getting product key" );
				console.log( "Key Model getKeyPos [" + e + "]" );
				return "";
			}
		},

		/**
		 * Set Session
		 */
		setSession: function(sSess)
		{
			this._sSess = sSess;
		},

		/**
		 * Clear all config information
		 */
		reset: function()
		{
			this._sSess = "";
			this._bSerial = 0;
			this._sVersion = "";
			this._bNumcam = 0;
			this._bPosLock = 0;
			this._sMac = "";
		},

		getSerial: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._bSerial;
		},

		getVersion: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._sVersion;
		},

		getNumcam: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._bNumcam;
		},
		
		getPosLock: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._bPosLock;
		},

		getMac: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._sMac;
		}

	}
);
