dojo.provide( "rda.util.Table" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.util.Table",
	[ dijit._Widget, dijit._Templated ],
	{
		// The fedds combo widget template
		templateString: "<table cellspacing=\"0\"><thead></thead><tbody></tbody></table>",

		classTag: 'rdaTable sortable',

		_tblHead: null,
		_tblBody: null,
		_rgoField: [],
		_oCellEdit: null,

		/**
		 * Called after widget is created.  Like a constructor.
		 */
		postCreate: function()
		{
			this._tblHead = this.domNode.childNodes[ 0 ]
			this._tblBody = this.domNode.childNodes[ 1 ];

			this.setClassTag( this.classTag );
		},

		/**
		 * Called when widget is destroyed.  Destructor.
		 */
		destroy: function()
		{
			while ( this._tblBody.childNodes.length )
				this._tblBody.removeChild( this._tblBody.childNodes[ 0 ] );
			this._tblBody = null;

			this.inherited( arguments );
		},

		/**
		 * Set the name of the class to pull CSS information from
		 *
		 * @param sTag
		 *   Name of CSS class
		 */
		setClassTag: function( sTag )
		{
			this.classTag = sTag;
			this.domNode.className = sTag;
		},

		/**
		 * Return the row count of the table.
		 *
		 * @return Row count of table.
		 */
		size: function()
		{
			return this._tblBody.childNodes.length;
		},

		/**
		 * Clear all rows from the table (not the header)
		 */
		clear: function()
		{
			while ( this.size() )
				this.delRow( 0 );
			this._cancelSort();
		},

		/**
		 * Setup fields that will display in table.
		 * This also will create the Table header.
		 *
		 * @param rgoField
		 *   Associative array of fields to add to the table
		 */
		addFields: function( rgoField )
		{
			if ( this._rgoField.length != 0 )
				throw new Error( "table already has fields configured" );
			this._rgoField = rgoField;

			// Alright, add a new row for these columns
			var oRow = document.createElement( "tr" );

			// Add a new hidden row for indexing purposes
			this._rgoField.splice( 0, 0, { field: "_id", name: "InternalID", hidden: true } );

			for ( var ix = 0; ix < this._rgoField.length; ix++ ) {
				var oField = this._rgoField[ ix ];
				var oCol = document.createElement( "th" );
				oCol.className = "header";
				if ( oField.hidden )
					oCol.style.display = "none";
				if ( oField.type )
					oCol.className += " sorttable_" + oField.type;
				oCol.appendChild( document.createTextNode( ( oField.name ) ? oField.name : "" ) );
				oRow.appendChild( oCol );
			}

			this._tblHead.appendChild( oRow );

			sorttable.makeSortable( this.domNode );
		},

		/**
		 * Sort table by field
		 *
		 * @param sField
		 *   Field to sort by
		 */
		sortTable: function( sField )
		{
			var ix = 0;
			while ( ix < this._rgoField.length ) {
				if ( sField == this._rgoField[ ix ].field )
					break;
				ix++;
			}
			if ( ix >= this._rgoField.length ) return;

			var oElement = this._tblHead.childNodes[ 0 ].childNodes[ ix ];

			if ( document.createEventObject ) {
				// dispatch for IE
				var evt = document.createEventObject();
				return oElement.fireEvent( 'onclick' );

			} else {
				// dispatch for firefox + others
				var evt = document.createEvent( "HTMLEvents" );
				evt.initEvent( 'click', true, true ); // event type, bubbling, cancelable
				return ! oElement.dispatchEvent( evt );
			}
		},

		/**
		 * Add a new row to the end of the table.
		 *
		 * @param rgoRow
		 *   Associative array of fields (cols) to add to this
		 */
		addRow: function( rgoRow )
		{
			// Alright, add a new row for these columns
			var oRow = document.createElement( "tr" );
			oRow.className = "row";
			if ( this.size() & 1 )
				dojo.addClass( oRow, "row-alt" );

			oRow.onmouseover = function() {
				dojo.addClass( this, "row-highlight" );
			};
			oRow.onmouseout = function() {
				dojo.removeClass( this, "row-highlight" );
			};

			for ( var ix = 0; ix < this._rgoField.length; ix++ ) {
				var oField = this._rgoField[ ix ];
				// Handle internal ID separately
				if ( ix == 0 )
					var oColValue = this.size();
				else
					var oColValue = ( rgoRow[ oField.field ] ) ? rgoRow[ oField.field ] : "";

				var oCol = document.createElement( "td" );
				oCol.className = "row-td";
				var sStyle = "";
				if ( oField.styles )
					sStyle += oField.styles;
				if ( oField.hidden )
					sStyle += "display: none;";
				if ( sStyle != "" )
					this._setStyleText( oCol, sStyle );

				if ( ( typeof( oColValue ) == "object" ) && ( oColValue.domNode != null ) )
					oCol.appendChild( oColValue.domNode );
				else if ( typeof( oColValue ) == "object" )
					oCol.appendChild( oColValue );
				else {
					oCol.appendChild( document.createTextNode( oColValue ) );
					dojo.connect( oCol, "onclick", dojo.hitch( this, this._onClick, oField.field, this.size() ) );
				}
				oRow.appendChild( oCol );
			}

			this._tblBody.appendChild( oRow );
		},

		/**
		 * Delete a row from our table by index.
		 *
		 * @param ixRow
		 *   Zero based index of row to delete.
		 */
		delRow: function( ixRow )
		{
			if ( ( ixRow >= this.size() ) ||
			     ( ixRow < 0 && ixRow != -1 ) ||
			     ( ixRow == -1 && this.size() == 0 ) )
				throw new Error( "ixRow is out of range" );
			if ( ixRow == -1 )
				ixRow = this.size() - 1;

			this._tblBody.removeChild( this._tblBody.childNodes[ ixRow ] );
		},

		/**
		 * Public onClick handler to attach to
		 */
		onClick: function( sField, ixRow )
		{
		},

		/**
		 * A Cell was clicked, so fire onClick event.
		 * Also, if this field is editable, then start the
		 * edit process and fire an onApplyCellEdit event
		 * when finished.
		 *
		 * @param sField
		 *   Name of field (column) to grab
		 * @param ixRow
		 *   Zero index of row to grab cell from
		 */
		_onClick: function( sField, ixRow )
		{
			// Cell was clicked, see if we can edit this field?
			try {
				var ixField = this._getFieldIndex( sField );
				if ( ! this._rgoField[ ixField ].editable ) {
					this.onClick( sField, ixRow );
					return;
				}

				if ( this._oCellEdit != null )
					return;

				// Alright, grab value, convert it to a text box with this value in it
				for ( var ix = 0; ix < this._tblBody.childNodes.length; ix++ ) {
					var oRow = this._tblBody.childNodes[ ix ];
					if ( oRow.childNodes[ 0 ].childNodes[ 0 ].nodeValue == ixRow ) {
						var oCol = oRow.childNodes[ ixField ];

						var sValue = this.getValue( sField, ixRow );

						// Remove text node
						oCol.removeChild( oCol.childNodes[ 0 ] );
						// Create new Text box
						var oTextBox = document.createElement( "input" );
						dojo.attr( oTextBox, "type", "text" );
						dojo.attr( oTextBox, "size", "9" );
						dojo.attr( oTextBox, "maxlength", "9" );
						dojo.attr( oTextBox, "value", sValue );
						oCol.appendChild( oTextBox );

						var bHandlerBlur = dojo.connect( oTextBox, "onblur", dojo.hitch( this, this._onApplyCellEdit, sField, ixRow ) );
						var bHandlerKey = dojo.connect( oTextBox, "onkeypress", this, "_onKey" );

						this._oCellEdit = { field: sField, row: ixRow, hdlrBlur: bHandlerBlur, hdlrKey: bHandlerKey, cell: oTextBox };

						oTextBox.focus();

						this.onClick( sField, ixRow );
						return;
					}
				}
				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "cannot edit field [" + e + "]" );
			}
		},

		/**
		 * Public onApplyCellEdit handler to attach to
		 */
		onApplyCellEdit: function( sField, ixRow )
		{
		},

		/**
		 * When a cell has finished being edited, this event is fired.
		 *
		 * @param sField
		 *   Name of field (column) being edited
		 * @param ixRow
		 *   Zero based index of row to grab cell from
		 */
		_onApplyCellEdit: function( sField, ixRow )
		{
			try {
				if ( this._oCellEdit == null )
					return;

				// Disconnect blur event for cell
				dojo.disconnect( this._oCellEdit.hdlrBlur );
				dojo.disconnect( this._oCellEdit.hdlrKey );

				var ixField = this._getFieldIndex( sField );
				for ( var ix = 0; ix < this._tblBody.childNodes.length; ix++ ) {
					var oRow = this._tblBody.childNodes[ ix ];
					if ( oRow.childNodes[ 0 ].childNodes[ 0 ].nodeValue == ixRow ) {
						var oCol = oRow.childNodes[ ixField ];

						var sValue = oCol.childNodes[ 0 ].value;

						// Remove text box
						oCol.removeChild( oCol.childNodes[ 0 ] );
						// Add new text node
						oCol.appendChild( document.createTextNode( sValue ) );

						this._oCellEdit = null;

						this.onApplyCellEdit( sField, ixRow );
						return;
					}
				}
				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "cannot apply cell edit [" + e + "]" );
			}
		},

		/**
		 * Detect enter key pressed, so we can force an apply
		 * on cell editing.
		 */
		_onKey: function( e )
		{
			try {
				if ( this._oCellEdit == null ) return;
				if ( e.target != this._oCellEdit.cell ) return;
				if ( e.keyCode != dojo.keys.ENTER ) return;

				this._onApplyCellEdit( this._oCellEdit.field, this._oCellEdit.row );

			} catch ( e ) {
				console.debug( "On Key Press Error [" + e + "]" );
			}
		},

		/**
		 * Get text value from a given cell by field/row id.
		 *
		 * @param sField
		 *   Name of field (column) to grab
		 * @param ixRow
		 *   Zero index of row to grab cell from
		 *
		 * @return Text value of cell
		 */
		getValue: function( sField, ixRow )
		{
			try {
				for ( var ix = 0; ix < this._tblBody.childNodes.length; ix++ ) {
					var oRow = this._tblBody.childNodes[ ix ];
					if ( oRow.childNodes[ 0 ].childNodes[ 0 ].nodeValue == ixRow ) {
						var ixField = this._getFieldIndex( sField );
						return oRow.childNodes[ ixField ].childNodes[ 0 ].nodeValue;
					}
				}
				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "cannot get value from table [" + e + "]" );
			}
		},

		/**
		 * Set new text value for cell
		 *
		 * @pararm sField
		 *   Name of field (column) to change
		 * @param ixRow
		 *   Zero index of row to change cell
		 * @param oColValue
		 *   Value to change in cell
		 */
		setValue: function( sField, ixRow, oColValue )
		{
			try {
				if ( this._oCellEdit != null ) return;

				for ( var ix = 0; ix < this._tblBody.childNodes.length; ix++ ) {
					var oRow = this._tblBody.childNodes[ ix ];
					if ( oRow.childNodes[ 0 ].childNodes[ 0 ].nodeValue == ixRow ) {
						var ixField = this._getFieldIndex( sField );
						oCol = oRow.childNodes[ ixField ];
						oCol.removeChild( oCol.childNodes[ 0 ] );

						if ( ( typeof( oColValue ) == "object" ) && ( oColValue.domNode != null ) )
							oCol.appendChild( oColValue.domNode );
						else if ( typeof( oColValue ) == "object" )
							oCol.appendChild( oColValue );
						else
							oCol.appendChild( document.createTextNode( oColValue ) );
						return;
					}
				}
				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "cannot set value in table [" + e + "]" );
			}
		},

		/**
		 * Set the style for this node
		 *
		 * @param o
		 *   HTML object
		 * @param s
		 *   Style string to set
		 */
		_setStyleText: function( o, s )
		{
			if ( o.style.cssText == undefined )
				dojo.attr( o, "style", s );
			else
				o.style.cssText = s;
		},

		/**
		 * Get index of field in _rgoField by field name.
		 *
		 * @param sField
		 *   Name of field to lookup
		 *
		 * @return Zero based index of field in array
		 */
		_getFieldIndex: function( sField )
		{
			try {
				for ( var ix = 0; ix < this._rgoField.length; ix++ )
					if ( sField == this._rgoField[ ix ].field )
						return ix;

				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "cannot find field index [" + e + "]" );
			}
		},

		/**
		 * Reset table back to default "no sort" state
		 */
		_cancelSort: function()
		{
			// remove sorttable_sorted classes
			for ( var ix = 0; ix < this._tblHead.childNodes[ 0 ].childNodes.length; ix++ ) {
				var cell = this._tblHead.childNodes[ 0 ].childNodes[ ix ];
				if (cell.nodeType == 1) { // an element
					cell.className = cell.className.replace('sorttable_sorted_reverse','');
					cell.className = cell.className.replace('sorttable_sorted','');
				}
			}
			sortfwdind = document.getElementById('sorttable_sortfwdind');
			if (sortfwdind) { sortfwdind.parentNode.removeChild(sortfwdind); }
			sortrevind = document.getElementById('sorttable_sortrevind');
			if (sortrevind) { sortrevind.parentNode.removeChild(sortrevind); }
		}

	}
);
