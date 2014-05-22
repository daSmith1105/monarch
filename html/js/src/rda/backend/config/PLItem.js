/**
 *
 * Price List Item Object
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.PLItem" );

dojo.declare(
	"rda.backend.config.PLItem",
	null,
	{
		_bID: 0,
		_bCategory: 0,
		_sName: "",
		_sDescription: "",
		_bCost: 0.0,
		_bRetail: 0.0,
		_bDiscount: 0.0,

		/**
		 * Creates a new instance of our PLItem Object
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
				else if ( sKey == "bCategory" )
					this._bCategory = parseInt( rgs[ sKey ] );
				else if ( sKey == "sName" )
					this._sName = String( rgs[ sKey ] );
				else if ( sKey == "sDescription" )
					this._sDescription = String( rgs[ sKey ] );
				else if ( sKey == "bCost" )
					this._bCost = parseFloat( rgs[ sKey ] );
				else if ( sKey == "bRetail" )
					this._bRetail = parseFloat( rgs[ sKey ] );
				else if ( sKey == "bDiscount" )
					this._bDiscount = parseFloat( rgs[ sKey ] );
			}
		},

		/**
		 * Return a Hash of our object ready to send back to server
		 */
		freeze: function()
		{
			var rgs = new Object();

			rgs[ "bID" ] = this._bID;
			rgs[ "bCategory" ] = this._bCategory;
			rgs[ "sName" ] = this._sName;
			rgs[ "sDescription" ] = this._sDescription;
			rgs[ "bCost" ] = this._bCost;
			rgs[ "bRetail" ] = this._bRetail;
			rgs[ "bDiscount" ] = this._bDiscount;

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

		getCategory: function()
		{
			return this._bCategory;
		},
		setCategory: function( bCategory )
		{
			this._bCategory = bCategory;
		},

		getName: function()
		{
			return this._sName;
		},
		setName: function( sName )
		{
			this._sName = sName;
		},

		getDescription: function()
		{
			return this._sDescription;
		},
		setDescription: function( sDescription )
		{
			this._sDescription = sDescription;
		},

		getCost: function()
		{
			return this._bCost;
		},
		setCost: function( bCost )
		{
			this._bCost = bCost;
		},

		getRetail: function()
		{
			return this._bRetail;
		},
		setRetail: function( bRetail )
		{
			this._bRetail = bRetail;
		},

		getDiscount: function()
		{
			return this._bDiscount;
		},
		setDiscount: function( bDiscount )
		{
			this._bDiscount = bDiscount;
		}

	}
);
