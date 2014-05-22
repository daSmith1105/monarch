/**
 * iMonarch.js
 *
 * Monarch is the control center for Dividia.
 * This app let's you manager DVS registrations, review DVS reports,
 * generate quotes, etc.
 *
 * This is the iPhone specific version.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.iMonarch" );

dojo.require( "rda.common.Observer" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.RDAServer" );
dojo.require( "rda.backend.AuthModel" );
dojo.require( "rda.backend.config.ServerModel" );
dojo.require( "rda.backend.config.Server" );
dojo.require( "rda.login.LoginView" );
dojo.require( "rda.login.LoginController" );

dojo.declare(
	"rda.iMonarch",
	[ rda.common.Observer ],
	{
		// Properties
		oScreenPrev: null,
		oAuthModel: null,
		oServerModel: null,
		oLoginView: null,
		oLoginController: null,
		divContent: null,
		bHandleResize: null,

		init: function() {
			try {
				// Initialize Store and backend
				try {
					var oStore = rda.config.Store.getInstance();

				} catch ( e ) {
					console.debug( "Error initializing backend" );
					alert( "Error initializing backend, aborting" );
				}

				this.divContent = dojo.byId( "content" );
				//this.bHandleResize = dojo.connect( window, "onresize", this, "HdlrResize" );

				this.oAuthHelper = new rda.login.AuthHelper();
				this.oAuthHelper.setServer( '' );
				this.oAuthHelper.storeServer();

				this.oAuthModel = new rda.backend.AuthModel();
				this.oServerModel = new rda.backend.config.ServerModel();

				this.oLoginView = new rda.login.LoginView();
				this.oLoginController = new rda.login.LoginController( this.oAuthHelper, this.oAuthModel, this.oLoginView );
				this.oLoginController.addActionListener( this );

				this.showScreen( new rda.Screen( this.oLoginController, this.oLoginView ) );

				this.oAuthModel.addObserver( this );     // Used to load and reset all Models
				this.oCameraModel.addObserver( this );   // Used to update CameraConfModel when CameraModel changes

				this.oLoginController.autoLogin()

			} catch ( e ) {
				console.debug( "Error during initialization [" + e + "]" );
				alert( "Error during initialization" );
			}
		},

		destroy: function() {
			try {
				//dojo.disconnect( this.bHandleResize );

				if ( this.oAuthModel.checkIsLoaded() )
					this.oLoginController.doLogout();

				// Handle disabling auto-login from here
				if ( this.oScreenPrev.getController() != this.oLoginController ) return;
				if ( this.oLoginView.isAutoChecked() ) return;
				this.oLoginController.updateAutoLogin();

			} catch(e) {
				alert('Error occurred during destruction ['+e+']');
			}
		},

		update: function( oObj )
		{
			if ( oObj == this.oAuthModel ) {
				if ( this.oAuthModel.checkIsLoaded() ) {
					// Successfully authenticated
					//  Load any models that need to be loaded for the
					//  duration of this login session
					var sSess = this.oAuthModel.getSession();
					this.oServerModel.setSession( sSess );
					this.oServerModel.load();
					if ( ! this.oServerModel.checkIsLoaded() )
						this.backendFailed();

				} else {
					// No longer authenticated
					//  Unloaded any modules that are in memory
					this.oServerModel.reset();

				}
			}
		},

		actionPerformed: function( sCommand )
		{
			console.debug( "iMonarch received action [" + sCommand + "]" );

			if ( sCommand == "screen-change-logout" ) {
				this.showScreen( new rda.Screen( this.oLoginController, this.oLoginView ) );

			} else {
				console.log( "screen change [" + sCommand + "] not implemented" );

			}
		},

		backendFailed: function()
		{
			this.showScreen( new rda.Screen( this.oLoginController, this.oLoginView ) );

			var sError = "An error occurred while gathering information from the server.  Please try again.\n" +
				"If this problem persists, please contact Dividia at 866-348-4342";
			this.oLoginController.promptError( sError );
		},

		showScreen: function( oScreenCurr )
		{
			if ( this.oScreenPrev ) {
				this.oScreenPrev.getController().deactivate();
				this.oScreenPrev.getView().setVisible( false );
				this.divContent.removeChild( this.oScreenPrev.getView().domNode );
			}

			this.divContent.appendChild( oScreenCurr.getView().domNode );
			//oScreenCurr.getView().requestFocus();
			oScreenCurr.getController().activate();
			oScreenCurr.getView().setVisible( true );

			this.oScreenPrev = oScreenCurr;
		}

	}
);

dojo.declare(
	"rda.Screen",
	null,
	{
		oController: null,
		oView: null,

		constructor: function( oController, oView )
		{
			this.oController = oController;
			this.oView = oView;
		},

		getController: function()
		{
			return this.oController;
		},

		getView: function()
		{
			return this.oView;
		}
	}
);
