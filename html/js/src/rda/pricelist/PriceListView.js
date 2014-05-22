dojo.provide( "rda.pricelist.PriceListView" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.require( "dijit.Dialog" );

dojo.require( "rda.util.Table" );

dojo.declare(
	"rda.pricelist.PriceListView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/PriceListView.html"),

		// Properties
		_sCopyright: "",
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),
		_rgoListener: [],
		_dlgLoading: null,
		_fVisible: false,
		_bHandlerId: 0,

		_tblPriceList: null,
		_rgoCategory: [],
		_rgoItem: [],
		_bDiscount: 0,

		// our DOM nodes 
		tblHeader: null,
		tdMenu: null,
		btnMenuHome: null,
		btnLogout: null,

		cbxCategory: null,
		entSearch: null,
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
			this._tblPriceList = new rda.util.Table();
      this._tblPriceList.addFields( [
				{ field: "id", name: "ID", hidden: true },
				{ field: "category", name: "Category" },
				{ field: "item", name: "Item", styles: "font-weight: bold;" },
				{ field: "description", name: "Description" },
				{ field: "cost", name: "Cost", styles: "text-align: right;", type: "numeric" },
				{ field: "dist", name: "Dist", styles: "text-align: right;", editable: true, type: "numeric" },
				{ field: "retail", name: "Retail", styles: "font-weight: bold; text-align: right;", type: "numeric" }
			] );
			dojo.attr( this._tblPriceList.domNode, "align", "center" );

      this.divPrice.appendChild( this._tblPriceList.domNode );

			this._dlgLoading = new dijit.Dialog( {
				title     : "Loading...",
				content   : "Please wait while we retrieve data from the server.",
				style     : "width: 200px",
				draggable : false
			} );

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
      this.divPrice.removeChild( this._tblPriceList.domNode );
      this.setItemList( [], 0 );
			this.setCategoryList( [] );

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
			(function(btn,sCommand){dojo.connect(btn,"onclick",null,function(e){oListener.actionPerformed(sCommand);});})(this.btnPrint,"print-request");
			dojo.connect( this.cbxCategory, "onchange", this, "_onChange" );
			dojo.connect( this._tblPriceList, "onApplyCellEdit", this, "_onApplyCellEdit" );

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

			this.setupTabFocus();
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

		/**
		 * Handle anything special with keypresses and focus for the different tabs.
		 */
		setupTabFocus: function()
		{
			if ( this._fVisible ) {
				if ( this._bHandlerId == 0 )
					this._bHandlerId = dojo.connect( document, 'onkeypress', this, '_onKey' );

			} else {
				if ( this._bHandlerId != 0 ) {
					dojo.disconnect( this._bHandlerId );
					this._bHandlerId = 0;
				}

			}
		},

		/************************************************
     * Main Tab functions
     ************************************************/

		/**
     * Display all of these cameras in our Table.
     *
     * @param rgoCategory
     *   All categories to match name with item record category number
		 */
		setCategoryList: function( rgoCategory )
		{
			this._rgoCategory = rgoCategory;

			// Clear box
			while ( this.cbxCategory.childNodes.length > 0 )
				this.cbxCategory.removeChild( this.cbxCategory.childNodes[ 0 ] );

			// Add select all
			var o = document.createElement( "option" );
			dojo.attr( o, "value", 0 );
			o.appendChild( document.createTextNode( "All Categories" ) );
			this.cbxCategory.appendChild( o );
			var o = document.createElement( "option" );
			dojo.attr( o, "value", 0 );
			o.appendChild( document.createTextNode( "--------------" ) );
			this.cbxCategory.appendChild( o );

			for ( var ix = 0; ix < rgoCategory.length; ix++ ) {
				var o = document.createElement( "option" );
				dojo.attr( o, "value", rgoCategory[ ix ].getID() );
				o.appendChild( document.createTextNode( rgoCategory[ ix ].getName() ) );
				this.cbxCategory.appendChild( o );
			}
		},

		/**
		 * Select a category to filter by.
		 *
		 * @param bCategory
		 *   Filter list by category ID
		 */
		selectCategory: function( bCategory )
		{
			for ( var ix = 0; ix < this.cbxCategory.childNodes.length; ix++ ) {
				if ( this.cbxCategory.childNodes[ ix ].value == bCategory ) {
					dojo.attr( this.cbxCategory.childNodes[ ix ], "selected", true );
					this._onChange();
					return;
				}
			}
		},

		/**
     * Display all of these cameras in our Table.
     *
     * @param rgoItem
     *   List of Price List Item objects to display
     * @param bDiscount
     *   Discount percentage off retail to calc Distributor price
     */
		setItemList: function( rgoItem, bDiscount )
		{
			this._rgoItem = rgoItem;
			this._bDiscount = bDiscount;

			this._tblPriceList.clear();

      for ( var ix = 0; ix < rgoItem.length; ix++ ) {
        var oItem = rgoItem[ ix ];

        this._tblPriceList.addRow( {
          "id": oItem.getID(),
          "category": this._getCategory( oItem.getCategory() ),
          "item": oItem.getName(),
          "description": oItem.getDescription(),
          "cost": this._formatCurrency( oItem.getCost() ),
          "dist": this._formatCurrency( this._calcDist( bDiscount, oItem.getDiscount(), oItem.getCost(), oItem.getRetail() ) ),
          "retail": this._formatCurrency( oItem.getRetail() )
        } );

      }
		},

		/**
		 * Open new print window
		 */
		printList: function()
		{
			var tblPrint = new rda.util.Table();
      tblPrint.addFields( [
				{ field: "id", name: "ID", hidden: true },
				{ field: "category", name: "Category" },
				{ field: "item", name: "Item", styles: "font-weight: bold;" },
				{ field: "description", name: "Description" },
				{ field: "cost", name: "Cost", styles: "text-align: right;", type: "numeric" },
				{ field: "dist", name: "Dist", styles: "text-align: right;", type: "numeric" },
				{ field: "retail", name: "Retail", styles: "font-weight: bold; text-align: right;", type: "numeric" }
			] );
			dojo.attr( tblPrint.domNode, "align", "center" );

			var sCategoryPrev = sCategoryCur = "";
      for ( var ix = 0; ix < this._rgoItem.length; ix++ ) {
        var oItem = this._rgoItem[ ix ];

				var sCategory = this._getCategory( oItem.getCategory() );
				if ( sCategoryPrev != sCategory )
					sCategoryPrev = sCategoryCurr = sCategory;
				else
					sCategoryCurr = "";

        tblPrint.addRow( {
          "id": oItem.getID(),
          "category": sCategoryCurr,
          "item": oItem.getName(),
          "description": oItem.getDescription(),
          "cost": this._formatCurrency( oItem.getCost() ),
          "dist": this._formatCurrency( this._calcDist( this._bDiscount, oItem.getDiscount(), oItem.getCost(), oItem.getRetail() ) ),
          "retail": this._formatCurrency( oItem.getRetail() )
        } );

      }

			var oDate = new Date();
			var bMonth = oDate.getMonth() + 1;
			if ( bMonth < 10 ) bMonth = "0" + bMonth;
			var bDay = oDate.getDate();
			if ( bDay < 10 ) bDay = "0" + bDay;
			var bYear = oDate.getYear();
			if ( bYear < 1000 ) bYear += 1900;
			var bDate = bMonth + "/" + bDay + "/" + bYear;

			var winPrint = window.open( "", "winPrint", "toolbar=no,titlebar=no,width=800,height=600" );
			var sDoc = '<html><head><title>Dividia Price List</title>' +
				'<style type="text/css">' +
				'@import "js/dojo/rda/themes/tundra/Table.css";' +
				'@import "js/dojo/rda/themes/tundra/WelcomeView.css";' +
				'</style>' +
				'</head><body>' +
				'<h1>Dividia Price List</h1>' +
				'<h2>' + bDate + '</h2>' +
				'</body></html>';
			winPrint.document.write( sDoc );
			winPrint.document.close();
			winPrint.document.body.appendChild( tblPrint.domNode );
			winPrint.print();
			winPrint.close();
		},

		/**
		 * Get value of new distributor price
		 */
		getCellValue: function( sField, ixRow )
		{
			return this._tblPriceList.getValue( sField, ixRow );
		},

		/**
		 * Handle all keypresses for ServerList Tab
		 * This should detect a 't' keypress and give focus
		 * to our search box.  Then, when enter is pressed
		 * it should perform the search
		 */
		_onKey: function( e )
		{
			try {
				if ( e.target == this.entSearch ) {
					if ( e.keyCode == dojo.keys.ENTER )
						this.throwAction( "filter-search" );
				} else {
					if ( String.fromCharCode( e.which ) == 't' )
						this.entSearch.focus();
				}
			} catch ( e ) {
				console.debug( "Error handling key press [" + e + "]" );
			}
		},

		getSearch: function()
		{
			var s = this.entSearch.value;
			this.entSearch.value = "";
			return s;
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
		 * Get a category name for this item record category number
		 *
		 * @param bCategory
		 *   Category ID to lookup name for
		 *
		 * @return Name of Category
		 */
		_getCategory: function( bCategory )
		{
			try {
				for ( var ix = 0; ix < this._rgoCategory.length; ix++ )
					if ( this._rgoCategory[ ix ].getID() == bCategory )
						return this._rgoCategory[ ix ].getName();
				throw new Error();
			} catch ( e ) {
				return "unknown";
			}
		},

		/**
		 * Format number as currency (comma, decimal, etc)
		 *
		 * @param s
		 *   String representing number to format
		 *
		 * @return String with comma and decimal interjected
		 */
		_formatCurrency: function( s )
		{
			// Add decimal, etc
			var b = parseFloat( s );
			if ( isNaN( b ) ) b = 0.00;
			var sMinus = '';
			if ( b < 0 ) sMinus = '-';
			b = Math.abs( b );
			b = parseInt( ( b + 0.005 ) * 100 );
			b = b / 100;
			s = new String( b );
			if ( s.indexOf( '.' ) < 0 ) s += '.00';
			if ( s.indexOf( '.' ) == ( s.length - 2 ) ) s += '0';
			s = sMinus + s;

			// Add commas
			var delimiter = ","; // replace comma if desired
			var a = s.split('.',2)
			var d = a[1];
			var i = parseInt(a[0]);
			if(isNaN(i)) { return ''; }
			var minus = '';
			if(i < 0) { minus = '-'; }
			i = Math.abs(i);
			var n = new String(i);
			var a = [];
			while(n.length > 3)
			{
			var nn = n.substr(n.length-3);
			a.unshift(nn);
			n = n.substr(0,n.length-3);
			}
			if(n.length > 0) { a.unshift(n); }
			n = a.join(delimiter);
			if(d.length < 1) { amount = n; }
			else { amount = n + '.' + d; }
			amount = minus + amount;

			return amount;
		},

		/**
		 * Calculate Distributor price based on discount percentage.
		 *
		 * @param bDiscountDefault
		 *   Global discount percentage for all items
		 * @param bDiscount
		 *   Special discount percentage for this item only
		 * @param bCost
		 *   Cost of this item
		 * @param bRetail
		 *   Retail price of this item
		 *
		 * @return Dollar amount to charge for Distributor
		 */
		_calcDist: function( bDiscountDefault, bDiscount, bCost, bRetail )
		{
			var bAmount;
			// Automatic Discount
			if ( bDiscount == 0 ) {
				bDiscount = bDiscountDefault;
				bAmount = bRetail * bDiscount / 100;

				// Make sure we make as much as distributor on automatic discounts
				var bDiff = ( bRetail - bCost ) / 2;
				if ( bAmount > bDiff )
					bAmount = bDiff;

			// Manual override discount
			} else {
				bAmount = bRetail * bDiscount / 100;

			}

			return bRetail - bAmount;
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
		 * Category selection box has changed.
		 *
		 * @param e
		 *   HTML event object
		 */
		_onChange: function()
		{
			this.throwAction( "category-change-" + this.cbxCategory.value );
		},

		/**
		 * A cell has just been changed, so let's notify our controller
		 *
		 * @param sField
		 *   Field that was changed
		 * @param ixRow
		 *   Zero-based row index
		 */
		_onApplyCellEdit: function( sField, ixRow )
		{
			var sValue = this._tblPriceList.getValue( sField, ixRow );
			sValue = this._formatCurrency( sValue );
			this._tblPriceList.setValue( sField, ixRow, sValue );
			this.throwAction( "cell-change-" + sField + "-" + ixRow );
		},

		/**
		 * Helper function to throwActions manually to our Controller
		 */
		throwAction: function( sCommand )
		{
			for ( var ix = this._rgoListener.length - 1; ix >= 0; ix-- )
				this._rgoListener[ ix ].actionPerformed( sCommand );
		}

	}
);
