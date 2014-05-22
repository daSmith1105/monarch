/**
 *
 * Store Price List Items.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.PLItemModel" );

dojo.require( "rda.common.Observable" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.PLItem" );

dojo.declare(
	"rda.backend.config.PLItemModel",
	[ rda.common.Observable ],
	{
		_sSess: "",
		_oStore: null,
		_rgoItem: null,
		_bDiscount: 0.0,

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
				rgsResult = oServer.Query( "config.pricelist.getItems", this._sSess );
				this._rgoItem = new Array();
				for ( var ix = 0; ix < rgsResult.length; ix++ )
					this._rgoItem.push( new rda.backend.config.PLItem( rgsResult[ ix ] ) );

				// Pull discount from server
				this._bDiscount = oServer.Query( "config.pricelist.getDiscount", this._sSess );

				this._fLoaded = true;
				this.setChanged();
				this.notifyObservers();

			} catch ( e ) {
				console.debug( "PLItem Model Load [" + e + "]" );
				alert( "Error querying pricelist item list" );
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
			this._rgoItem = null;
			this._sSess = "";

			this._fLoaded = false;
			//this.setChanged();
			//this.notifyObservers();
		},

		/**
		 * Return a mixed server list of (id/name) pairs.
		 *
		 * @return Item List
		 */
		getList: function()
		{
			return this._rgoItem;
		},

		/**
		 * Get a Item Object
		 *
		 * @return Item
		 */
		getItem: function()
		{
			for ( var ix = 0; ix < this._rgoItem.length; ix++ ) {
				if ( typeof arguments[ 0 ] == "number" ) {
					// By ID
					if ( this._rgoItem[ ix ].getID() == arguments[ 0 ] )
						return this._rgoItem[ ix ];

				} else {
					// By Name
					if ( this._rgoItem[ ix ].getName() == arguments[ 0 ] )
						return this._rgoItem[ ix ];

				}
			}

			throw new Error( "unknown pricelist item [" + arguments[ 0 ] + "]" );
		},

		/**
		 * Get default Discount percentage
		 *
		 * @return Discount Percentage
		 */
		getDiscount: function()
		{
			return this._bDiscount;
		},

		/**
		 * Set default Discount percentage
		 *
		 * @param bDiscount
		 *   Discount percentage to assign to item.
		 *
		 * @return True/False
		 */
		setDiscount: function( bDiscount )
		{
			// Setup server backend
			var oServer = this._oStore.get( "oServer" );

			var fStatus = oServer.Query( "config.pricelist.setDiscount", this._sSess, bDiscount );
			if ( ! fStatus ) return false;

			this._bDiscount = bDiscount;
		},

		/**
		 * Set item Discount percentage
		 *
		 * @param bDiscount
		 *   Discount percentage to assign to item.
		 *
		 * @return True/False
		 */
		setItemDiscount: function( bItem, bDiscount )
		{
			// Setup server backend
			var oServer = this._oStore.get( "oServer" );

			var fStatus = oServer.Query( "config.pricelist.setItemDiscount", this._sSess, bItem, bDiscount );
			if ( ! fStatus ) return false;

			// Now update our object
			for ( var ix = 0; ix < this._rgoItem.length; ix++ )
				if ( this._rgoItem[ ix ].getID() == bItem )
					this._rgoItem[ ix ].setDiscount( bDiscount );
		}

	}
);
