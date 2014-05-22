/**
 *
 * Open / Load tickets by serial
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.TicketModel" );

dojo.require( "rda.config.Store" );

dojo.declare(
	"rda.backend.TicketModel",
	[],
	{
		_sSess: "",
		_oStore: null,

		constructor: function()
		{
			this._oStore = rda.config.Store.getInstance();

			this.reset();
		},

		/**
		 * Call backend to open ticket.
		 *
		 * @param bSerial
		 *   Serial of DVR to open ticket for
		 * @param sSummary
		 *   Summary of ticket
		 * @param sDesc
		 *   Description of ticket
		 *
		 * @return true/false bugzilla ticket status
		 */
		openTicket: function( bSerial, sSummary, sDesc )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				fResult = oServer.Query( "ticket.openTicket", this._sSess, bSerial, sSummary, sDesc );

				return fResult;

			} catch ( e ) {
				console.debug( "Ticket Model open [" + e + "]" );
				// bz webservice api slow and times out
				//return false;
				return true;
			}
		},

		/**
		 * Call backend to open maintenance ticket.
		 *
		 * @param bSerial
		 *   Serial of DVR to open ticket for
		 *
		 * @return true/false bugzilla ticket status
		 */
		openMaintTicket: function( bSerial )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				fResult = oServer.Query( "ticket.openMaintTicket", this._sSess, bSerial );

				return fResult;

			} catch ( e ) {
				console.debug( "Ticket Model open maint [" + e + "]" );
				return false;
			}
		},

		/**
		 * Get most recent 5 tickets for this Serial
		 *
		 * @param bSerial
		 *   Serial of DVR to open ticket for
		 *
		 * @return list of tickets
		 */
		getTickets: function( bSerial )
		{
			try {
				// Setup server backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from server
				rgoResult = oServer.Query( "ticket.getTickets", this._sSess, bSerial );

				return rgoResult;

			} catch ( e ) {
				console.debug( "Ticket Model get tickets [" + e + "]" );
				return new Array();
			}
		},

		/**
		 * Set Session
		 */
		setSession: function(sSess)
		{
			this._sSess = sSess;
		},

		/**
		 * Clear all config information
		 */
		reset: function()
		{
			this._sSess = "";
		}

	}
);
