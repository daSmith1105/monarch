dojo.provide( "rda.pricelist.PriceListController" );

/********************************************************
 * Price List
 * This module contains list all products that have been
 * imported from Quickbooks.  We allow the user to change
 * the distributor pricing and we track that change.
 ********************************************************/

dojo.require( "rda.common.DController" );
dojo.require( "rda.common.Observer" );

dojo.declare(
	"rda.pricelist.PriceListController",
	[ rda.common.DController, rda.common.Observer ],
	{
		// Properties
		oView: null,
		oPLCategoryModel: null,
		oPLItemModel: null,
		fBlockUpdate: false,

		_bCategoryCurr: 0,

		/**
     * Constructor
     *
     * @param oPLCategoryModel
     *   Model to hold all Categories
     * @param oPLItemModel
     *   Model to hold all Price List Items
     * @param oView
     *   View for this module in MVC
     */
		constructor: function( oPLCategoryModel, oPLItemModel, oView )
		{
			this.oView = oView;
			this.oPLCategoryModel = oPLCategoryModel;
			this.oPLItemModel = oPLItemModel;

			this.oView.addActionListener( this );
			this.oPLCategoryModel.addObserver( this );
			this.oPLItemModel.addObserver( this );
		},

		/**
     * This function is called by Monarch.js when our
     * screen is selected and shown on the screen.  We
     * should initialize our state from this function.
     */
		activate: function()
		{
			if ( this.oPLItemModel.checkIsLoaded() ) return;
			this.oView.startLoading();
			this.oPLCategoryModel.load();
			this.oPLItemModel.load();
			this.oView.finishLoading();
			if ( ! this.oPLItemModel.checkIsLoaded() )
				this.throwAction( "backend-failed" );

			// Select Cameras category by default
			var oCategory = this.oPLCategoryModel.getCategory( "CAMERAS" );
			this.oView.selectCategory( oCategory.getID() );
		},

		/**
     * If we need to do any deactivation, like clearing
     * Models to free memory, etc.  It should be done here.
     */
		deactivate: function()
		{
		},

		/**
     * We receive any callbacks from Views here and dispatch
     * accordingly.  Should be screen changes, tab changes, etc.
     *
     * @param sCommand
     *   String parameter to determine what action to take
     */
		actionPerformed: function( sCommand )
		{
			console.debug( "PriceListController received action [" + sCommand + "]" );

			var rgs = sCommand.split( "-" );
			if ( ( rgs[ 0 ] == "screen" ) && ( rgs[ 1 ] == "change" ) )
				this.throwAction( sCommand );

			else if ( ( rgs[ 0 ] == "category" ) && ( rgs[ 1 ] == "change" ) )
				this.changeCategory( parseInt( rgs[ 2 ] ) );

			else if ( sCommand == "filter-search" )
				this.filterSearch();

			else if ( sCommand == "print-request" )
				this.oView.printList();

			else if ( ( rgs[ 0 ] == "cell" ) && ( rgs[ 1 ] == "change" ) )
				this.setItemDiscount( rgs[ 2 ], parseInt( rgs[ 3 ] ) );
		},

		/**
     * This function is called from any Model objects we are "observing".
     * This implements the Observer pattern.
     *
     * @param oObj
     *   Model object that has been updated.
     */
		update: function( oObj )
		{
			if ( this.fBlockUpdate ) return;
			if ( ! oObj.checkIsLoaded() ) return;

			if ( oObj == this.oPLCategoryModel ) {
				this.oView.setCategoryList( this.oPLCategoryModel.getList() );

			} else if ( oObj == this.oPLItemModel ) {
				this.setItemList();

			}
		},

		/**
		 * Filter search requested
		 * Switch to "All Categories", then perform regex search
		 */
		filterSearch: function()
		{
			this.fBlockUpdate = true;
			this.oView.selectCategory( 0 );
			this.fBlockUpdate = false;

			this.setItemList( this.oView.getSearch() );
		},

		/**
		 * Update selected category index to filter price list.
		 *
		 * @param bCategory
		 *   ID of category to lookup in model
		 */
		changeCategory: function( bCategory )
		{
			this._bCategoryCurr = bCategory;
			if ( this.fBlockUpdate ) return;

			this.setItemList();
		},

		/**
		 * Update item list (filter)
		 */
		setItemList: function( sFilter )
		{
			if ( ! this.oPLCategoryModel.checkIsLoaded() ) {
				console.log( "PriceListController: category model should be loaded before the item model" );
				return;
			}
			if ( ! this.oPLItemModel.checkIsLoaded() ) return;

			rgoFilter1 = [];
			rgoItem = this.oPLItemModel.getList();
			for ( var ix = 0; ix < rgoItem.length; ix++ )
				if ( ( this._bCategoryCurr == 0 ) || ( this._bCategoryCurr == rgoItem[ ix ].getCategory() ) )
					rgoFilter1.push( rgoItem[ ix ] );

			if ( sFilter == null ) {
				this.oView.setItemList( rgoFilter1, this.oPLItemModel.getDiscount() );
				return;
			}

			// Filter by text as well
			var oMatch = new RegExp( sFilter, "i" );
			var rgoFilter2 = [];
			for ( var ix = 0; ix < rgoFilter1.length; ix++ )
				if ( oMatch.test( rgoFilter1[ ix ].getName() ) ||
				     oMatch.test( rgoFilter1[ ix ].getDescription() ) ||
				     oMatch.test( this.oPLCategoryModel.getCategory( rgoFilter1[ ix ].getCategory() ).getName() ) )
					rgoFilter2.push( rgoFilter1[ ix ] );

			this.oView.setItemList( rgoFilter2, this.oPLItemModel.getDiscount() );
		},

		/**
		 * Calculate distributor discount percentage based on
		 * dollar amounts.
		 *
		 * @param bDist
		 *   Distributor discount price in dollars
		 * @param bRetail
		 *   Retail price in dollars
		 *
		 * @return Distributor discount as a percentage off retail
		 */
		_calcDiscount: function( bDist, bRetail )
		{
			return ( bRetail - bDist ) / bRetail * 100;
		},

		/**
		 * The user changed the Distributor price, so calculate a new discount percentage
		 * and save it to the backend database.
		 *
		 * @param sField
		 *   Field that has been changed
		 * @param ixRow
		 *   Row in table that changed
		 */
		setItemDiscount: function( sField, ixRow )
		{
			var bItem = parseInt( this.oView.getCellValue( "id", ixRow ) );
			var bDist = parseFloat( this.oView.getCellValue( sField, ixRow ) );
			var bRetail = parseFloat( this.oView.getCellValue( "retail", ixRow ) );

			var bDiscount = this._calcDiscount( bDist, bRetail );

			this.fBlockUpdate = true;
			this.oPLItemModel.setItemDiscount( bItem, bDiscount );
			this.fBlockUpdate = false;
		}

	}
);
