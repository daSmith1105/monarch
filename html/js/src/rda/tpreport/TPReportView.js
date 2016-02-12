dojo.provide( "rda.tpreport.TPReportView" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.require( "dijit.Dialog" );

dojo.require( "rda.util.Table" );

dojo.declare(
	"rda.tpreport.TPReportView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/TPReportView.html"),

		// Properties
		_sCopyright: "",
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),
		_rgoListener: [],
		_dlgLoading: null,
		_fVisible: false,
		_bHandlerId: 0,

		_rgoReport: [],

		// our DOM nodes 
		tblHeader: null,
		tdMenu: null,
		btnMenuHome: null,
		btnLogout: null,

		cbxReport: null,
		entDateFrom: null,
		entDateTo: null,
		btnPrint: null,
		divPrice: null,

		/************************************************
     * Widget functions
     ************************************************/

    /**
     * Constructor
     * This is called after dojo creates this widget as part
     * of an initializer.
     */
		postCreate: function()
		{
			// Create Menu buttons
      this.btnMenuHome = this._createLink( "Home" );

      this._createMenu( this.divPrice );
		},

		/**
     * Destructor
     * We should free up any DOM objects/widgets we've created.
     */
    destroy: function()
    {
			this.setReportList( [] );

      this.inherited( arguments );
    },

    /**
     * This is called after dojo creates this widgets but before
     * the template is created.  This fills the template variables in.
     */
		postMixInProperties: function()
		{
			var oDate = new Date();
			var bYear = oDate.getYear();
			if ( bYear < 1000 ) bYear += 1900;
			this._sCopyright = 'Copyright &copy;' + bYear + ' Dividia Technologies, LLC';
		},

		/**
     * Our view has been resized, so redraw anything that depends on it.
     *
     * @param oViewport
     *   Viewport object that contains our new dimensions.
     */
		onResize: function( oViewport )
		{
			var bWidth = oViewport.w - 20;
			this.tblHeader.style.width = bWidth;
			this.divPrice.style.width = bWidth;

			var oPosition = this._findPosition( this.divPrice );
			this.divPrice.style.height = oViewport.h - 10 - oPosition.t;
		},

		/************************************************
     * Global functions
     ************************************************/

    /**
     * Register new ActionListeners.  This will call the actionPerformed
     * function usually residing on the Controller.
     *
     * @param oListener
     *   The listener is usually just the Controller object.
     */
		addActionListener: function( oListener )
		{
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnMenuHome,"screen-change-welcome");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnLogout,"screen-change-logout");
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnRun,"run-report");
			dojo.connect( this.cbxReport, "onchange", this, "_onChange" );

			this._rgoListener.push( oListener );
		},

		/**
     * When our "screen" is switched to/away from this function
     * is called with a true for Show and a false for Hide.
     *
     * @param fVisible
     *   Is our view currently visible in the browser?
     */
		setVisible: function( fVisible )
		{
			this._fVisible = fVisible;
		},

		/**
     * Show a dialog when we are querying the server and it is going
     * to take some time to get the data.  This is just feedback to
     * show the user we are doing something.
     */
		startLoading: function()
		{
			this._dlgLoading.show();
		},

		/**
     * Hide dialog when we are querying the server and it is going
     * to take some time to get the data.  This is just feedback to
     * show the user we are doing something.
     */
		finishLoading: function()
		{
			this._dlgLoading.hide();
		},

		/************************************************
     * Main Tab functions
     ************************************************/

		/**
     * Display all of these cameras in our Table.
     *
     * @param rgoReport
     *   All categories to match name with item record report number
		 */
		setReportList: function( rgoReport )
		{
			this._rgoReport = rgoReport;

			// Clear box
			while ( this.cbxReport.childNodes.length > 0 )
				this.cbxReport.removeChild( this.cbxReport.childNodes[ 0 ] );

			for ( var ix = 0; ix < rgoReport.length; ix++ ) {
				var o = document.createElement( "option" );
				dojo.attr( o, "value", rgoReport[ ix ].getID() );
				o.appendChild( document.createTextNode( rgoReport[ ix ].getName() ) );
				this.cbxReport.appendChild( o );
			}
		},

		/**
		 * Select a report to filter by.
		 *
		 * @param bReport
		 *   Filter list by report ID
		 */
		selectReport: function( bReport )
		{
			for ( var ix = 0; ix < this.cbxReport.childNodes.length; ix++ ) {
				if ( this.cbxReport.childNodes[ ix ].value == bReport ) {
					dojo.attr( this.cbxReport.childNodes[ ix ], "selected", true );
					this._onChange();
					return;
				}
			}
		},

		/**
		 * Open new window
		 */
		showReport: function( sDoc )
		{
			//var winPrint = window.open( "", "winPrint", "toolbar=no,titlebar=no,width=800,height=600" );
			var winPrint = window.open();
			winPrint.document.write( sDoc );
			winPrint.document.close();
			//winPrint.print();
			//winPrint.close();
		},

		/************************************************
     * Helper functions
     ************************************************/

		/**
     * Find our absolute position on the screen.
     * This works even if we are nested.
     *
     * @param o
     *   Object we want to locate
     */
		_findPosition: function( o )
		{
			var bTop = bLeft = 0;
			if ( o.offsetParent ) {
				do {
					bTop += o.offsetTop;
					bLeft += o.offsetLeft;
				} while ( o = o.offsetParent );
			}

			return { t: bTop, l: bLeft };
		},

		/**
		 * Create an <a> HTML link to display to the user.
		 * This is used when making our navigation list, etc.
		 *
		 * @param sName
		 *   Text that should show for this link (label)
		 */
		_createLink: function( sName )
		{
			var a = document.createElement( "a" );
			dojo.attr( a, "href", "#" );
			a.appendChild( document.createTextNode( sName ) );
			return a;
		},

		/**
		 * Create links to navigate within module (bread crumbs)
		 *
		 * @param o
		 *   DOM object of tab we are displaying
		 */
		_createMenu: function( o )
		{
			// Remove old menu entries
			while ( this.tdMenu.childNodes.length )
				this.tdMenu.removeChild( this.tdMenu.childNodes[ 0 ] );

			if ( o == this.divPrice ) {
				this.tdMenu.appendChild( this.btnMenuHome );

			}
		},

		/**
		 * Report selection box has changed.
		 *
		 * @param e
		 *   HTML event object
		 */
		_onChange: function()
		{
			this.throwAction( "report-change-" + this.cbxReport.value );
		},

		/**
		 * Helper function to throwActions manually to our Controller
		 */
		throwAction: function( sCommand )
		{
			for ( var ix = this._rgoListener.length - 1; ix >= 0; ix-- )
				this._rgoListener[ ix ].actionPerformed( sCommand );
		},

		toggleDateWidgets: function( fVisible )
		{
			if ( fVisible ) {
				this.entDateFrom.style.display = "";
				this.entDateTo.style.display = "";
			} else {
				this.entDateFrom.style.display = "none";
				this.entDateTo.style.display = "none";
			}
		},

		getDateFrom: function()
		{
			return this.entDateFrom.value;
		},

		getDateTo: function()
		{
			return this.entDateTo.value;
		}

	}
);
