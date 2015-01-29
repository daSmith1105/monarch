/**
 *
 * Product Key V2 helper functions
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.KeyModelV2" );

dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.Server" );

dojo.declare(
	"rda.backend.KeyModelV2",
	[],
	{
		_sSess: "",
		_oStore: null,

		_rgsFeatures: new Array(),
		_rgsPosTypes: new Array(),

		constructor: function()
		{
			this._oStore = rda.config.Store.getInstance();

			this.reset();
		},

		load: function()
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				oResult = dojo.fromJson( oServer.Query( "key.getSupportedFeaturesV2", this._sSess ) );
			
				this._rgsFeatures = oResult[ 'features' ];
				this._rgsPosTypes = oResult[ 'pos_types' ];
				
				return true;
				
			} catch ( e ) {
				console.debug( "Key Model V2 Load [" + e + "]" );
				alert( "Error loading Key Model V2" );
				return false;
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
			this._rgsFeatures = new Array();
			this._rgsPosTypes = new Array();
		},

		getFeatures: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._rgsFeatures;
		},

		getPosTypes: function()
		{
			if ( this._sSess == "" )
				throw new Error( "KeyModel session is not set.  Data may not be valid." );

			return this._rgsPosTypes;
		}

	}
);
