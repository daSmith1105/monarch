dojo.provide( "rda.login.LoginController" );

dojo.require( "dojo.cookie" );

dojo.require( "rda.common.DController" );
dojo.require( "rda.common.Observer" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.login.AuthHelper" );
dojo.require( "rda.login.LoginStatus" );

dojo.declare(
	"rda.login.LoginController",
	[ rda.common.DController, rda.common.Observer ],
	{
		// Properties
		oStore: null,
		oAuthHelper: null,
		oAuthModel: null,
		oView: null,

		constructor: function( oAuthHelper, oAuthModel, oView )
		{
			this.oAuthHelper = oAuthHelper;
			this.oAuthModel = oAuthModel;
			this.oView = oView;

			this.oStore = rda.config.Store.getInstance();

			this.oAuthModel.addObserver( this );
			this.oView.addListener( this );
		},

		activate: function()
		{
			// If we are authenticated already, then logout first
			if ( this.oAuthModel.checkIsLoaded() )
				this.doLogout();

			// Enable/Disable Auto-Login based on if cookies are supported
			this.oView.toggleAuto( ! dojo.cookie.isSupported() );
			// Do we have a cookie?  If so, then perform auto-login
			var oUser = dojo.fromJson( dojo.cookie( "userInfo" ) );
			this.oView.setAuto( oUser != null );
			if ( oUser == null ) return;
			this.oView.setName( oUser[ 'name' ] );
			this.oView.setPassword( oUser[ 'pass' ] );
		},

		deactivate: function()
		{
		},

		actionPerformed: function( sCommand )
		{
			if ( sCommand == "login" ) {
				this.doLogin( false );

			} else if ( sCommand == "force" ) {
				this.doLogin( true );

			} else {
				console.log( "Unknown command from LoginView [" + sCommand + "]" );

			}
		},

		update: function( oObj )
		{
			if ( oObj == this.oAuthModel ) {
				if ( ! this.oAuthModel.checkIsLoaded() ) return;

				this.oAuthHelper.storeServer();
				this.throwAction( "screen-change-welcome" );

			}
		},

		promptError: function( sError )
		{
			this.oView.promptError( sError );
		},

		doLogin: function( fForce )
		{
			try {
				// Grab user/pass
				var sName = this.oView.getName();
				var sPass = this.oView.getPassword();

				// Update display before connecting to server
				this.oView.promptLoginAttempt();

				// Attempt Login
				oResult = this.oAuthHelper.loginSession( sName, sPass, fForce );

				// Login Error
				if ( oResult.getStatus() == rda.login.LoginStatus.ERROR ) {
					this.oView.promptError();
					return;
				}

				// Login Failed
				if ( oResult.getStatus() == rda.login.LoginStatus.NOAUTH ) {
					this.oView.promptLoginFailed();
					return;
				}

				this.updateAutoLogin();

				// Login succeeded, but we have another active session, what should we do? (sess == 'exists')
				if ( oResult.getStatus() == rda.login.LoginStatus.EXISTS ) {
					this.oView.promptExisting();
					return;
				}

				// Authenticated, so initiate AuthModel load
				this.oAuthModel.load( oResult.getSession(), oResult.getName() );
				this.oView.promptLoginSuccess();

			} catch(e) {
				this.oView.promptError();
			}
		},

		doLogout: function()
		{
			try {
				// Grab Session
				var sSess = this.oAuthModel.getSession();

				// Logout
				this.oAuthHelper.doLogout( sSess );

				// Clear Model
				this.oAuthModel.reset();

				// Reset cookies
				this._removeCookie();

			} catch ( e ) {
				// Eat any exceptions since logout might be while trying to close
			}
		},

		updateAutoLogin: function()
		{
			if ( this.oView.isAutoChecked() ) {
				// Store user/pass as cookie
				var oUser = { "name": this.oView.getName(), "pass": this.oView.getPassword() };
				dojo.cookie( "userInfo", dojo.toJson( oUser ), { expires: 30 } );

			} else {
				// Delete cookie
				dojo.cookie( "userInfo", null, { expires: -1 } );

			}
		},

		autoLogin: function()
		{
			// Auto-login checkbox and user/pass is auto populated
			// already based on activate function getting called
			if ( ! this.oView.isAutoChecked() ) return;

			// Perform Auto-login now
			this.doLogin( false );
		}

	}
);
