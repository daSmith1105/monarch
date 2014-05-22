/*
 * Store.js
 *
 * Global property store
 */

if ( ! dojo._hasResource[ "rda.config.Store" ] ) {
	dojo._hasResource[ "rda.config.Store" ] = true;
	dojo.provide( "rda.config.Store" );

	dojo.declare(
		"rda.config.Store",
		null,
		{
			_rgh: null,

			constructor: function()
			{
				this._rgh = new Object();
			},

			set: function( sName, oValue )
			{
				try {
					this._rgh[ sName ] = oValue;
				} catch ( e ) {
					alert( new Error( "Could not store" ) );
				}
			},

			get: function( sName )
			{
				var oValue = null;
				try {
					if ( this._rgh[ sName ] )
						oValue = this._rgh[ sName ];
				} catch ( e ) {}
				return oValue;
			}
		}
	);

	rda.config.Store._oInstance = null;

	rda.config.Store.getInstance = function()
	{
		if ( ! rda.config.Store._oInstance )
			rda.config.Store._oInstance = new rda.config.Store();
		return rda.config.Store._oInstance;
	};

}
