/**
 *
 * Price List Category Object
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.PLCategory" );

dojo.declare(
	"rda.backend.config.PLCategory",
	null,
	{
		_bID: 0,
		_sName: "",

		/**
		 * Creates a new instance of our PLCategory Object
		 */
		constructor: function()
		{
			if ( arguments.length > 0 )
				this.load( arguments[ 0 ] );
		},

		/**
		 * Load Hash from server into our structure
		 */
		load: function( rgs )
		{
			for ( var sKey in rgs ) {
				if ( sKey == "bID" )
					this._bID = parseInt( rgs[ sKey ] );
				else if ( sKey == "sName" )
					this._sName = String( rgs[ sKey ] );
			}
		},

		/**
		 * Return a Hash of our object ready to send back to server
		 */
		freeze: function()
		{
			var rgs = new Object();

			rgs[ "bID" ] = this._bID;
			rgs[ "sName" ] = this._sName;

			return rgs;
		},

		getID: function()
		{
			return this._bID;
		},
		setID: function( bID )
		{
			this._bID = bID;
		},

		getName: function()
		{
			return this._sName;
		},
		setName: function( sName )
		{
			this._sName = sName;
		}

	}
);
