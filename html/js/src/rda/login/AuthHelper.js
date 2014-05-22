/**
 *
 * Helper class to encapsulate all login related functions.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.login.AuthHelper" );

dojo.require( "rda.backend.RDAServer" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.login.LoginResult" );
dojo.require( "rda.login.LoginStatus" );

dojo.declare(
	"rda.login.AuthHelper",
	null,
	{
		_oStore: null,
		_sServer: "",
		_oServer: null,

		constructor: function()
		{
			this._oStore = rda.config.Store.getInstance();

			this._oServer = new rda.backend.RDAServer();

			this.setServer( '' );
			this.storeServer();
			if ( arguments.length > 0 ) {
				this.setServer( arguments[ 0 ] );
				this.storeServer();
			}
		},

		_buildServerString: function( sServer )
		{
			if ( sServer == '' )
				return sServer;
			return 'http://' + sServer;
		},

		setServer: function( sServer )
		{
			try {
				this._sServer = sServer;

				this._oServer.setServer( this._buildServerString( sServer ) );

				// Reset our autoroute variable
				// This determines if we route our xmlrpc calls through our
				// proxy server.  This is cached so we only check once.
				// If we switch the server, we should reset our cache.
				XMLRPC.autoroute = true;

			} catch ( e ) {
				console.debug ( 'Error setting server for login [' + e + ']' );
			}
		},

		getServer: function()
		{
			return this._sServer;
		},

		storeServer: function()
		{
			this._oStore.set( "sServer", this._sServer );
			this._oStore.set( "oServer", this._oServer );
		},

		doLogout: function( sSess )
		{
			try {
				// Logout
				if ( sSess != null )
					this._oServer.Query( "auth.logoutUser", sSess );

			} catch ( e ) {
				// Eat any exceptions since logout might be while trying to close
			}
		},

		loginSession: function( sName, sPass, fForce )
		{
			try {
				// Attempt Login (respecting force)
				sSess = this._oServer.Query( "auth.loginUser", sName, sPass, fForce );

				// Login Failed
				if ( sSess == "noauth" )
					return new rda.login.LoginResult( rda.login.LoginStatus.NOAUTH );

				// Login succeeded, but we have another active session
				if ( sSess == "exists" )
					return new rda.login.LoginResult( rda.login.LoginStatus.EXISTS );

				return new rda.login.LoginResult( rda.login.LoginStatus.SUCCESS, sSess, sName );

			} catch ( e ) {
				console.debug( "Login Error [" + e + "]" );
				alert( "Error logging into server" );
				return new rda.login.LoginResult( rda.login.LoginStatus.ERROR );;
			}
		},

		checkSession: function( sSess )
		{
			try {
				return this._oServer.Query( "auth.checkExists", sSess );

			} catch ( e ) {
				console.debug( "Check Session Error [" + e + "]" );
				alert( "Error checking session with server" );
				return false;
			}
		},

		whichIP: function( oServ )
		{
			var oServerTemp = new rda.backend.RDAServer();
			var sServer;
			var sUrl;

			/*
			 * Disabled since we have to use rpcproxy.cgi
			 * so we probably will never be local
			 *

			// Try local IP direct
			try {
				sServer = oServ.getLocalIP();
				sUrl = "http://" + sServer;
				oServerTemp.setServer( sUrl );
				oServerTemp.Query( "util.isAwelcome" );
				return sServer;
			} catch ( e ) {
			}

			// Try local IP with non-standard port
			if ( oServ.getPort() != 80 ) {
				try {
					sServer = oServ.getLocalIP() + ":" + oServ.getPort();
					sUrl = "http://" + sServer;
					oServerTemp.setServer( sUrl );
					oServerTemp.Query( "util.isAwelcome" );
					return sServer;
				} catch ( e ) {
				}
			}
			*/

			// Assume Public IP
			sServer = oServ.getIP();
			if ( oServ.getPort() != 80 )
				sServer += ":" + oServ.getPort();

			return sServer;
		}

	}
);
