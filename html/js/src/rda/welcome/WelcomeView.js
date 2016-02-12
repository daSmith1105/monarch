dojo.provide( "rda.welcome.WelcomeView" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.welcome.WelcomeView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/WelcomeView.html"),

		// Properties
		_sCopyright: "",
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),

		// our DOM nodes 
		tblHeader: null,
		btnLogout: null,
		btnRegistrations: null,
		btnCamera: null,
		btnPriceList: null,
		btnReport: null,
		btnCustomers: null,
		btnEvents: null,
		btnQuotes: null,
		btnMaintenance: null,

		/*
		 * Widget functions
		 */
		postMixInProperties: function()
		{
			var oDate = new Date();
			var bYear = oDate.getYear();
			if ( bYear < 1000 ) bYear += 1900;
			this._sCopyright = 'Copyright &copy;' + bYear + ' Dividia Technologies, LLC';
		},

		onResize: function( oViewport )
		{
			var bWidth = oViewport.w - 20;
			this.tblHeader.style.width = bWidth;
		},

		/*
		 * Public functions
		 */
		addActionListener: function( oListener )
		{
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnLogout,"screen-change-logout");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnRegistrations,"screen-change-registrations");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnCamera,"screen-change-camfail");
			//(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnPriceList,"screen-change-pricelist");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnReport,"screen-change-tpreport");
			//(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnCustomers,"screen-change-customers");
			//(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnEvents,"screen-change-events");
			//(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnQuotes,"screen-change-quotes");
			//(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnMaintenance,"screen-change-maintenance");
		},

		setVisible: function( fVisible )
		{
		}

	}
);
