/**
 *
 * Data Model to store all auth and rights information
 * for the currently Authenticated user.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.AuthModel" );

dojo.require( "rda.common.Observable" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.User" );
dojo.require( "rda.backend.config.Rights" );

dojo.declare(
	"rda.backend.AuthModel",
	[ rda.common.Observable ],
	{
		_oUser: null,
		_oRights: null,
		_sSess: "",
		_fLoaded: false,

		constructor: function()
		{
			this.reset();
		},

		load: function( sSess, sName )
		{
			try {
				var oStore = rda.config.Store.getInstance();
				var oServer = oStore.get( "oServer" );

				// Get User Object
				rgsUser = oServer.Query( "config.user.getUserByName", sSess, sName );
				this._oUser = new rda.backend.config.User( rgsUser );

				// Rights
				rgbRight = oServer.Query( "config.user.getRights", sSess, this._oUser.getID() );

				this._oRights = new rda.backend.config.Rights( rgbRight );

				this._sSess = sSess;
				this._fLoaded = true;
				this.setChanged();
				this.notifyObservers();

			} catch ( e ) {
				console.debug( "Error AuthModel Load [" + e + "]" );
				alert( "Error getting rights for user" );
				this._fLoaded = false;
				this.setChanged();
				this.notifyObservers();
			}
		},

		/**
		 * Clear all our internal data
		 */
		reset: function()
		{
			this._sSess = "";
			this._oUser = null;
			this._oRights = null;

			this._fLoaded = false;
			this.setChanged();	
			this.notifyObservers();
		},

		/**
		 * Check if our Model has successfully been loaded
		 * and we have not been cleared
		 */
		checkIsLoaded: function()
		{
			return this._fLoaded;
		},

		getID: function()
		{
			return this._oUser.getID();
		},

		getName: function()
		{
			return this._oUser.getName();
		},

		getSession: function()
		{
			return this._sSess;
		},

		checkHasRight: function( bRight )
		{
			return this._oRights.checkHasRight( bRight );
		}

	}
);
