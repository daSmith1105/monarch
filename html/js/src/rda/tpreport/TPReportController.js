dojo.provide( "rda.tpreport.TPReportController" );

/********************************************************
 * Price List
 * This module contains list all products that have been
 * imported from Quickbooks.  We allow the user to change
 * the distributor pricing and we track that change.
 ********************************************************/

dojo.require( "rda.common.DController" );
dojo.require( "rda.common.Observer" );

dojo.declare(
	"rda.tpreport.TPReportController",
	[ rda.common.DController, rda.common.Observer ],
	{
		// Properties
		oAuthModel: null,
		oTPReportModel: null,
		oView: null,
		fBlockUpdate: false,

		_bReportCurr: 0,

		/**
     * Constructor
     *
     * @param oTPReportModel
     *   Model to hold all Categories
     * @param oView
     *   View for this module in MVC
     */
		constructor: function( oAuthModel, oTPReportModel, oView )
		{
			this.oView = oView;
			this.oAuthModel = oAuthModel;
			this.oTPReportModel = oTPReportModel;

			this.oView.addActionListener( this );
			this.oTPReportModel.addObserver( this );
		},

		/**
     * This function is called by Monarch.js when our
     * screen is selected and shown on the screen.  We
     * should initialize our state from this function.
     */
		activate: function()
		{
			if ( ! this.oTPReportModel.checkIsLoaded() )
				this.oTPReportModel.load();

			// Select Cameras category by default
			var oReport = this.oTPReportModel.getReport( "Inventory by Location" );
			this.oView.selectReport( oReport.getID() );
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
			console.debug( "TPReportController received action [" + sCommand + "]" );

			var rgs = sCommand.split( "-" );
			if ( ( rgs[ 0 ] == "screen" ) && ( rgs[ 1 ] == "change" ) )
				this.throwAction( sCommand );

			else if ( ( rgs[ 0 ] == "report" ) && ( rgs[ 1 ] == "change" ) )
				this.changeReport( parseInt( rgs[ 2 ] ) );

			else if ( sCommand == "run-report" )
				this.runReport();
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

			if ( oObj == this.oTPReportModel ) {
				this.oView.setReportList( this.oTPReportModel.getList() );

			}
		},

		/**
		 * Update selected category index to filter price list.
		 *
		 * @param bReport
		 *   ID of category to lookup in model
		 */
		changeReport: function( bReport )
		{
			this._bReportCurr = bReport;
			if ( this.fBlockUpdate ) return;

			//TODO: Change button parameters here based on what this report needs
			if ( this._bReportCurr == 3 || this._bReportCurr == 4 || this._bReportCurr == 6 ) {
				// Commission reports, need a date range
				this.oView.toggleDateWidgets( true );

			} else {
				// Inventory reports, do not need date range input
				this.oView.toggleDateWidgets( false );

			}
		},

		runReport: function()
		{
			// Lock down certain reports for security
			if ( this.oAuthModel.getName() != "rayers" && this.oAuthModel.getName() != "mlaplante" && this.oAuthModel.getName() != "sheila" && 
			     ( this._bReportCurr == 3 || this._bReportCurr == 4 || this._bReportCurr == 6 ) ) {
				alert( 'You do not have access to run this report.' );
				return;
			}

			var sDateFrom = this.oView.getDateFrom();
			var sDateTo = this.oView.getDateTo();
			if ( sDateFrom == '' ) sDateFrom = '2016-01-01';
			if ( sDateTo == '' ) sDateTo = '2016-01-01';

			if ( this._bReportCurr == 3 || this._bReportCurr == 4 || this._bReportCurr == 6 )
				var sHTML = this.oTPReportModel.runReport( this._bReportCurr, sDateFrom, sDateTo );
			else
				var sHTML = this.oTPReportModel.runReport( this._bReportCurr );
			this.oView.showReport( sHTML );
		}


	}
);
