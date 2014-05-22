/**
 *
 * User Object holds the properties for each user in the system.
 * Ex. name, description, etc.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.User" );

dojo.declare(
	"rda.backend.config.User",
	null,
	{
		_bID: 0,
		_sName: "",
		_sDescription: "",
		_sPassword: "",
		_bType: 0,

		constructor: function()
		{
			if ( arguments.length > 0 )
				this.load( arguments[ 0 ] );
		},


		load: function( rgsUser )
		{
			for ( var sKey in rgsUser ) {
				if ( sKey == "bID" )
					this._bID = parseInt( rgsUser[ sKey ] );
				else if ( sKey == "sName" )
					this._sName = String( rgsUser[ sKey ] );
				else if ( sKey == "sDescription" )
					this._sDescription = String( rgsUser[ sKey ] );
				else if ( sKey == "sPassword" )
					this._sPassword = String( rgsUser[ sKey ] );
				else if ( sKey == "bType" )
					this._bType = parseInt( rgsUser[ sKey ] );
			}
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
		},

		getDescription: function()
		{
			return this._sDescription;
		},
		setDescription: function( sDescription )
		{
			this._sDescription = sDescription;
		},

		getPassword: function()
		{
			return this._sPassword;
		},
		setPassword: function( sPassword )
		{
			this._sPassword = sPassword;
		},

		getType: function()
		{
			return this._bType;
		},
		setType: function( bType )
		{
			this._bType = bType;
		}

	}
);
