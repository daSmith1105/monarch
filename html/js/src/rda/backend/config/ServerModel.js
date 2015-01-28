/**
 *
 * Store ServerModel settings.
 * Enabled, Name, etc.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.ServerModel" );

dojo.require( "rda.common.Observable" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.Server" );

dojo.declare(
	"rda.backend.config.ServerModel",
	[ rda.common.Observable ],
	{
		_sSess: "",
		_oStore: null,
		_rgoServer: null,

		_fLoaded: false,

		constructor: function()
		{
			this._oStore = rda.config.Store.getInstance();

			this.reset();
		},


		/**
		 * Load server information from server.
		 * This will load all config and rights information per server.
		 */
		load: function()
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				rgsResult = oServer.Query( "config.server.getAllServers", this._sSess );
				this._rgoServer = new Array();
				for ( var ix = 0; ix < rgsResult.length; ix++ )
					this._rgoServer.push( new rda.backend.config.Server( rgsResult[ ix ] ) );

				this._fLoaded = true;
				this.setChanged();
				this.notifyObservers();

			} catch ( e ) {
				console.debug( "Server Model Load [" + e + "]" );
				alert( "Error querying server list" );
				this._fLoaded = false;
				this.setChanged();
				this.notifyObservers();
			}
		},

		/**
		 * Load updated information for this server.
		 * This is used to keep the server we are watching up2date.
		 */
		loadSerial: function( bSerial )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				rgsResult = oServer.Query( "config.server.getServerBySerial", this._sSess, bSerial );
				var oServer = new rda.backend.config.Server( rgsResult );
				for ( var ix = 0; ix < this._rgoServer.length; ix++ ) {
					if ( this._rgoServer[ ix ].getSerial() == oServer.getSerial() ) {
						// Save locally
						this._rgoServer[ ix ] = oServer;
						this.setChanged();
						this.notifyObservers();
						return;
					}
				}

			} catch ( e ) {
				console.debug( "Server Model Load Serial [" + e + "]" );
				alert( "Error updating server info" );
			}
		},

		/**
		 * Load updated information for these server.
		 * This is used to keep the server list page we are watching up2date.
		 */
		loadSerials: function( rgbSerial )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				rgsResult = oServer.Query( "config.server.getAllServersBySerial", this._sSess, rgbSerial );
				for ( var ix = 0; ix < rgsResult.length; ix++ ) {
					var oServer = new rda.backend.config.Server( rgsResult[ ix ] );
					for ( var ix2 = 0; ix2 < this._rgoServer.length; ix2++ ) {
						if ( this._rgoServer[ ix2 ].getSerial() == oServer.getSerial() ) {
							// Save locally
							this._rgoServer[ ix2 ] = oServer;
							this.setChanged();
							break;
						}
					}
				}

				this.notifyObservers();

			} catch ( e ) {
				console.debug( "Server Model Load Serial [" + e + "]" );
				alert( "Error updating server info" );
			}
		},

		/**
		 * Check if we successfully loaded
		 */
		checkIsLoaded: function()
		{
			return this._fLoaded;
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
			this._rgoServer = null;
			this._sSess = "";

			this._fLoaded = false;
			//this.setChanged();
			//this.notifyObservers();
		},

		/**
		 * Return a mixed server list of (id/name) pairs.
		 *
		 * @return Server List
		 */
		getList: function()
		{
			return this._rgoServer;
		},

		/**
		 * Return list of server names sorted by name
		 *
		 * @return Server List
		 */
		getListName: function()
		{
			var rgs = new Array();
			for ( var ix = 0; ix < this._rgoServer.length; ix++ )
				rgs.push( this._rgoServer[ ix ].getName() );
			rgs.sort();
			return rgs;
		},

		/**
		 * Return list of server names sorted by name
		 * That are "alive" and checking in.
		 * 
		 * @return Server List
		 */
		getListNameAlive: function()
		{
			var rgs = new Array();
			for ( var ix = 0; ix < this._rgoServer.length; ix++ )
				if ( this._rgoServer[ ix ].checkIsAlive() )
					rgs.push( this._rgoServer[ ix ].getName() );
			rgs.sort();
			return rgs;
		},

		/**
		 * Get a Server Object by Serial
		 *
		 * @param bSerial
		 *  Serial of server to get
		 *
		 * @return Server
		 */
		getServerBySerial: function( bSerial )
		{
			for ( var ix = 0; ix < this._rgoServer.length; ix++ )
				if ( this._rgoServer[ ix ].getSerial() == bSerial )
					return this._rgoServer[ ix ];
			throw new Error( "unknown server id [" + bSerial + "]" );
		},

		/**
		 * Get a Server Object by Seed
		 *
		 * @param bSeed
		 *  Seed of server to get
		 *
		 * @return Server
		 */
		getServerBySeed: function( sSeed )
		{
			for ( var ix = 0; ix < this._rgoServer.length; ix++ )
				if ( this._rgoServer[ ix ].getSeed() == sSeed )
					return this._rgoServer[ ix ];
			throw new Error( "unknown server seed [" + sSeed + "]" );
		},

		/**
		 * Get a Server Object
		 *
		 * @return Server
		 */
		getServer: function()
		{
			if ( typeof arguments[ 0 ] == "number" ) {
				// By Index
				var ix = arguments[ 0 ];
				if ( ix < 0 || ix > this._rgoServer.length )
					throw new Error( "unknown server id [" + ix + "]" );
				return this._rgoServer[ ix ];

			} else {
				// By Name
				for ( var ix = 0; ix < this._rgoServer.length; ix++ )
					if ( this._rgoServer[ ix ].getName() == arguments[ 0 ] )
						return this._rgoServer[ ix ];

				throw new Error( "unknown server name [" + arguments[ 0 ] + "]" );
			}
		},

		/**
		 * Set a Server Object
		 *
		 * @param oServer
		 *  Server object to replace (matches on ID)
		 */
		setServer: function( oServer )
		{
			try {
				for ( var ix = 0; ix < this._rgoServer.length; ix++ ) {
					if ( this._rgoServer[ ix ].getSerial() == oServer.getSerial() ) {
						// Setup server backend
						var oServ = this._oStore.get( "oServer" );
						rgsResult = oServ.Query( "config.server.setServer", this._sSess, oServer.freeze() );

						// Save locally
						this._rgoServer[ ix ] = new rda.backend.config.Server( rgsResult );
						this.setChanged();
						this.notifyObservers();
						return;
					}
				}

				throw new Error( "not found" );

			} catch ( e ) {
				console.debug( "Error saving server object" );
				console.debug( e );
				throw new Error( "Error updating server information id-[" + oServer.getSerial() + "]" );
			}
		},

		/**
		 * Add a new Server Object
		 *
		 * @param bSerial
		 *   Serial of server to add
		 * @param sVersion
		 *   Version installed on server
		 * @param bNumcam
		 *   Number of cameras supported for this server
		 * @param sMac
		 *   Mac to tie this product key to
		 */
		addServer: function( bSerial, sVersion, bNumcam, sMac )
		{
			try {
				var oServ = this._oStore.get( "oServer" );
				rgsResult = oServ.Query( "config.server.addServer", this._sSess, bSerial );

				var oServer = new rda.backend.config.Server( rgsResult );
				oServer.setVersion( sVersion );
				oServer.setNumcam( bNumcam );
				oServer.setMac( sMac );

				rgsResult = oServ.Query( "config.server.setServer", this._sSess, oServer.freeze() );

				var oServer = new rda.backend.config.Server( rgsResult );
				this._rgoServer.push( oServer );

				return oServer;

			} catch ( e ) {
				console.debug( "Error adding server object" );
				console.debug( e );
				throw new Error( "Error adding server information id-[" + bSerial + "]" );
			}
		},

		/**
		 * Add a new Server Object
		 *
		 * @param sSeed
		 *   Seed of server to add
		 */
		addServerV2: function( sSeed )
		{
			try {
				var oServ = this._oStore.get( "oServer" );
				rgsResult = oServ.Query( "config.server.addServerV2", this._sSess, sSeed );

				var oServer = new rda.backend.config.Server( rgsResult );
				this._rgoServer.push( oServer );

				return oServer;

			} catch ( e ) {
				console.debug( "Error adding server object" );
				console.debug( e );
				throw new Error( "Error adding server information id-[" + bSerial + "]" );
			}
		}

	}
);
