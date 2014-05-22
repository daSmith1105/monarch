dojo.provide( "rda.util.ComboBox" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.util.ComboBox",
	[ dijit._Widget, dijit._Templated ],
	{
		// The css class for this combo
		comboClass: "",

		// The fedds combo widget template
		templateString: "<select class=\"${comboClass}\" dojoAttachEvent=\"onchange:onSelectionChanged\"></select>",

		_bCount: 0,

		// Removes all existing options from the combo
		clean: function()
		{
			this.domNode.innerHTML = "";
			this._bCount = 0;
		},
		
		// Callback on change 
		onSelectionChanged: function( e )
		{
		},
	
		// Adds a new option to the combo
		addOption: function( label, value )
		{
			// create option node
			var optionNode = document.createElement( "option" );
			// add the new option to the select
			optionNode.appendChild( document.createTextNode( label ) );
			optionNode.value = value;
			this.domNode.appendChild( optionNode );
			this._bCount++;
		},
		
		// Returns currently selected value
		getSelectedValue: function()
		{
			return this.domNode.value;
		},
	
		// Returns total item count
		getItemCount: function()
		{
			return this._bCount;
		},
	
		// Set current selection
		setValue:function( value )
		{
			this.domNode.value = value;
			this.onSelectionChanged( { target: this.domNode } );	
		},

		// Set current selection (don't fire events)
		setValueQuiet: function( value )
		{
			this.domNode.value = value;
		}

	}
);
