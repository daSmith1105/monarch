/**
 * Monarch.js
 *
 * Monarch is the control center for Dividia.
 * This app let's you manager DVS registrations, review DVS reports,
 * generate quotes, etc.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.Monarch" );

dojo.require( "rda.common.Observer" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.RDAServer" );
dojo.require( "rda.backend.AuthModel" );
dojo.require( "rda.backend.KeyModel" );
dojo.require( "rda.backend.KeyModelV2" );
dojo.require( "rda.backend.TicketModel" );
dojo.require( "rda.backend.config.ServerModel" );
dojo.require( "rda.backend.config.Server" );
dojo.require( "rda.backend.config.CameraModel" );
dojo.require( "rda.backend.config.Camera" );
dojo.require( "rda.backend.config.PLCategoryModel" );
dojo.require( "rda.backend.config.PLCategory" );
dojo.require( "rda.backend.config.PLItemModel" );
dojo.require( "rda.backend.config.PLItem" );
dojo.require( "rda.backend.config.TPReportModel" );
dojo.require( "rda.backend.config.TPReport" );
dojo.require( "rda.login.LoginView" );
dojo.require( "rda.login.LoginController" );
dojo.require( "rda.welcome.WelcomeView" );
dojo.require( "rda.welcome.WelcomeController" );
dojo.require( "rda.registrations.RegistrationsView" );
dojo.require( "rda.registrations.RegistrationsController" );
dojo.require( "rda.camfail.CameraFailView" );
dojo.require( "rda.camfail.CameraFailController" );
dojo.require( "rda.pricelist.PriceListView" );
dojo.require( "rda.pricelist.PriceListController" );
dojo.require( "rda.tpreport.TPReportView" );
dojo.require( "rda.tpreport.TPReportController" );

dojo.declare(
	"rda.Monarch",
	[ rda.common.Observer ],
	{
		// Properties
		oScreenPrev: null,
		oAuthModel: null,
		oKeyModel: null,
		oKeyModelV2: null,
		oTicketModel: null,
		oServerModel: null,
		oCameraModel: null,
		oPLCategoryModel: null,
		oPLItemModel: null,
		oTPReportModel: null,
		oLoginView: null,
		oLoginController: null,
		oWelcomeView: null,
		oWelcomeController: null,
		oRegistrationsView: null,
		oRegistrationsController: null,
		oCameraFailView: null,
		oCameraFailController: null,
		oPriceListView: null,
		oPriceListController: null,
		oTPReportView: null,
		oTPReportController: null,
		divContent: null,
		bHandleResize: 0,

		init: function() {
			try {
				// Initialize Store and backend
				try {
					var oStore = rda.config.Store.getInstance();

				} catch ( e ) {
					console.debug( "Error initializing backend [" + e + "]" );
					alert( "Error initializing backend, aborting" );
				}

				this.divContent = dojo.byId( "content" );
				this.bHandleResize = dojo.connect( window, "onresize", this, "onResize" );

				this.oAuthHelper = new rda.login.AuthHelper();
				this.oAuthHelper.setServer( '' );
				this.oAuthHelper.storeServer();

				this.oAuthModel = new rda.backend.AuthModel();
				this.oKeyModel = new rda.backend.KeyModel();
				this.oKeyModelV2 = new rda.backend.KeyModelV2();
				this.oTicketModel = new rda.backend.TicketModel();
				this.oServerModel = new rda.backend.config.ServerModel();
				this.oCameraModel = new rda.backend.config.CameraModel();
				this.oPLCategoryModel = new rda.backend.config.PLCategoryModel();
				this.oPLItemModel = new rda.backend.config.PLItemModel();
				this.oTPReportModel = new rda.backend.config.TPReportModel();
				this.oAuthModel.addObserver( this );     // Used to load and reset all Models

				this.oLoginView = new rda.login.LoginView();
				this.oLoginController = new rda.login.LoginController( this.oAuthHelper, this.oAuthModel, this.oLoginView );
				this.oLoginController.addActionListener( this );

				this.oWelcomeView = new rda.welcome.WelcomeView();
				this.oWelcomeController = new rda.welcome.WelcomeController( this.oAuthHelper, this.oAuthModel, this.oWelcomeView );
				this.oWelcomeController.addActionListener( this );

				this.oRegistrationsView = new rda.registrations.RegistrationsView();
				this.oRegistrationsController = new rda.registrations.RegistrationsController( this.oAuthModel, this.oServerModel, this.oKeyModel, this.oKeyModelV2, this.oTicketModel, this.oRegistrationsView );
				this.oRegistrationsController.addActionListener( this );

				this.oCameraFailView = new rda.camfail.CameraFailView();
				this.oCameraFailController = new rda.camfail.CameraFailController( this.oCameraModel, this.oServerModel, this.oCameraFailView );
				this.oCameraFailController.addActionListener( this );

				this.oPriceListView = new rda.pricelist.PriceListView();
				this.oPriceListController = new rda.pricelist.PriceListController( this.oPLCategoryModel, this.oPLItemModel, this.oPriceListView );
				this.oPriceListController.addActionListener( this );

				this.oTPReportView = new rda.tpreport.TPReportView();
				this.oTPReportController = new rda.tpreport.TPReportController( this.oAuthModel, this.oTPReportModel, this.oTPReportView );
				this.oTPReportController.addActionListener( this );

				this.showScreen( new rda.Screen( this.oLoginController, this.oLoginView ) );

				this.oLoginController.autoLogin()

			} catch ( e ) {
				console.debug( "Error during initialization [" + e + "]" );
				alert( "Error during initialization" );
			}
		},

		destroy: function() {
			try {
				dojo.disconnect( this.bHandleResize );

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
					this.oKeyModel.setSession( sSess );
					this.oKeyModelV2.setSession( sSess );
					this.oTicketModel.setSession( sSess );
					this.oServerModel.setSession( sSess );
					this.oCameraModel.setSession( sSess );
					this.oPLCategoryModel.setSession( sSess );
					this.oPLItemModel.setSession( sSess );
					this.oTPReportModel.setSession( sSess );

				} else {
					// No longer authenticated
					//  Unloaded any modules that are in memory
					this.oKeyModel.reset();
					this.oKeyModelV2.reset();
					this.oTicketModel.reset();
					this.oServerModel.reset();
					this.oCameraModel.reset();
					this.oPLCategoryModel.reset();
					this.oPLItemModel.reset();
					this.oTPReportModel.reset();

				}
			}
		},

		actionPerformed: function( sCommand )
		{
			console.debug( "Monarch received action [" + sCommand + "]" );

			if ( sCommand == "backend-failed" ) {
				this.backendFailed();

			} else if ( sCommand == "screen-change-logout" ) {
				this.showScreen( new rda.Screen( this.oLoginController, this.oLoginView ) );

			} else if ( sCommand == "screen-change-welcome" ) {
				this.showScreen( new rda.Screen( this.oWelcomeController, this.oWelcomeView ) );

			} else if ( sCommand == "screen-change-registrations" ) {
				this.showScreen( new rda.Screen( this.oRegistrationsController, this.oRegistrationsView ) );

			} else if ( sCommand == "screen-change-camfail" ) {
				this.showScreen( new rda.Screen( this.oCameraFailController, this.oCameraFailView ) );

			} else if ( sCommand == "screen-change-pricelist" ) {
				this.showScreen( new rda.Screen( this.oPriceListController, this.oPriceListView ) );

			} else if ( sCommand == "screen-change-tpreport" ) {
				this.showScreen( new rda.Screen( this.oTPReportController, this.oTPReportView ) );

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
			this.oScreenPrev = oScreenCurr;

			this.divContent.appendChild( oScreenCurr.getView().domNode );
			//oScreenCurr.getView().requestFocus();
			oScreenCurr.getController().activate();
			oScreenCurr.getView().setVisible( true );
			this.onResize();
		},

		onResize: function()
		{
			try {
				var oViewport = dijit.getViewport();
				if ( ( this.oScreenPrev != null ) && ( this.oScreenPrev.getView().onResize ) )
					this.oScreenPrev.getView().onResize( oViewport );
			} catch ( e ) {
				console.debug( "Error during resize [" + e + "]" );
			}
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
