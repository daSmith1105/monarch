/**
 *
 * Store Price List Categories.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.PLCategoryModel" );

dojo.require( "rda.common.Observable" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.PLCategory" );

dojo.declare(
	"rda.backend.config.PLCategoryModel",
	[ rda.common.Observable ],
	{
		_sSess: "",
		_oStore: null,
		_rgoCategory: null,

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
				rgsResult = oServer.Query( "config.pricelist.getCategories", this._sSess );
				this._rgoCategory = new Array();
				for ( var ix = 0; ix < rgsResult.length; ix++ )
					this._rgoCategory.push( new rda.backend.config.PLCategory( rgsResult[ ix ] ) );

				this._fLoaded = true;
				this.setChanged();
				this.notifyObservers();

			} catch ( e ) {
				console.debug( "PLCategory Model Load [" + e + "]" );
				alert( "Error querying pricelist category list" );
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
			this._rgoCategory = null;
			this._sSess = "";

			this._fLoaded = false;
			//this.setChanged();
			//this.notifyObservers();
		},

		/**
		 * Return a mixed server list of (id/name) pairs.
		 *
		 * @return Category List
		 */
		getList: function()
		{
			return this._rgoCategory;
		},

		/**
		 * Get a Category Object
		 *
		 * @return Category
		 */
		getCategory: function()
		{
			for ( var ix = 0; ix < this._rgoCategory.length; ix++ ) {
				if ( typeof arguments[ 0 ] == "number" ) {
					// By ID
					if ( this._rgoCategory[ ix ].getID() == arguments[ 0 ] )
						return this._rgoCategory[ ix ];

				} else {
					// By Name
					if ( this._rgoCategory[ ix ].getName() == arguments[ 0 ] )
						return this._rgoCategory[ ix ];

				}
			}

			throw new Error( "unknown pricelist category [" + arguments[ 0 ] + "]" );
		}

	}
);
