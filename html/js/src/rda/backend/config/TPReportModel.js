/**
 *
 * Store Price List Categories.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.TPReportModel" );

dojo.require( "rda.common.Observable" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.TPReport" );

dojo.declare(
	"rda.backend.config.TPReportModel",
	[ rda.common.Observable ],
	{
		_sSess: "",
		_oStore: null,
		_rgoReport: null,

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
				rgsResult = oServer.Query( "tigerpaw.getReports", this._sSess );
				this._rgoReport = new Array();
				for ( var ix = 0; ix < rgsResult.length; ix++ )
					this._rgoReport.push( new rda.backend.config.TPReport( rgsResult[ ix ] ) );

				this._fLoaded = true;
				this.setChanged();
				this.notifyObservers();

			} catch ( e ) {
				console.debug( "TPReport Model Load [" + e + "]" );
				alert( "Error querying tigerpaw reports list" );
				this._fLoaded = false;
				this.setChanged();
				this.notifyObservers();
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
			this._rgoReport = null;
			this._sSess = "";

			this._fLoaded = false;
			//this.setChanged();
			//this.notifyObservers();
		},

		/**
		 * Return a mixed server list of (id/name) pairs.
		 *
		 * @return Report List
		 */
		getList: function()
		{
			return this._rgoReport;
		},

		/**
		 * Get a Report Object
		 *
		 * @return Report
		 */
		getReport: function()
		{
			for ( var ix = 0; ix < this._rgoReport.length; ix++ ) {
				if ( typeof arguments[ 0 ] == "number" ) {
					// By ID
					if ( this._rgoReport[ ix ].getID() == arguments[ 0 ] )
						return this._rgoReport[ ix ];

				} else {
					// By Name
					if ( this._rgoReport[ ix ].getName() == arguments[ 0 ] )
						return this._rgoReport[ ix ];

				}
			}

			throw new Error( "unknown tigerpaw report [" + arguments[ 0 ] + "]" );
		},

		/**
		 * Run report on server and get HTML result page
		 */
		runReport: function()
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				if ( arguments.length == 1 ) {
					var bReport = arguments[ 0 ];
					sResult = oServer.Query( "tigerpaw.runReport", this._sSess, bReport );

				} else {
					var bReport = arguments[ 0 ];
					var sDateFrom = arguments[ 1 ];
					var sDateTo = arguments[ 2 ];
					sResult = oServer.Query( "tigerpaw.runReport", this._sSess, bReport, sDateFrom, sDateTo );

				}

				return sResult;

			} catch ( e ) {
				console.debug( "TPReport Model runReport [" + e + "]" );
				alert( "Error running tigerpaw report" );
				return 'Error running tigerpaw report';
			}
		}

	}
);
