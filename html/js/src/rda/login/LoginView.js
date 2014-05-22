dojo.provide( "rda.login.LoginView" );

dojo.require( "dijit._Widget" );
dojo.require( "dijit._Templated" );

dojo.declare(
	"rda.login.LoginView",
	[ dijit._Widget, dijit._Templated ],
	{
		// Template files
		templatePath: dojo.moduleUrl( "rda", "templates/LoginView.html"),

		// Properties
		_sCopyright: "",
		_imgLogo: dojo.moduleUrl( "rda", "themes/tundra/images/dt_logo.gif" ),
		_bHandlerId: 0,

		// our DOM nodes 
		frmLogin: null,
		btnLogin: null,
		btnForce: null,
		btnAuto: null,
		lblMessage: null,

		/*
		 * Widget functions
		 */
		postMixInProperties: function()
		{
			var oDate = new Date();
			var bYear = oDate.getYear();
			if ( bYear < 1000 ) bYear += 1900;
			this._sCopyright = '&copy;' + bYear + ' Dividia Technologies, LLC';
			dojo.connect( this.frmLogin, 'onsubmit', this, '_onSubmit' );
		},

		/*
		 * Public functions
		 */
		setVisible: function( fVisible )
		{
			if ( fVisible ) {
				this.frmLogin.sUser.focus();
				this._bHandlerId = dojo.connect( document, 'onkeypress', this, '_onKey' );

			} else {
				dojo.disconnect( this._bHandlerId );

			}
		},

		addListener: function( obj )
		{
			dojo.connect( this.btnLogin, "onclick", obj, function() { this.actionPerformed( "login" ); } );
			dojo.connect( this.btnForce, "onclick", obj, function() { this.actionPerformed( "force" ); } );
		},

		toggleAuto: function( fDisable )
		{
			this.btnAuto.disabled = fDisable;
		},

		getName: function()
		{
			return this.frmLogin.sUser.value;
		},

		setName: function( sName )
		{
			this.frmLogin.sUser.value = sName;
		},

		getPassword: function()
		{
			return this.frmLogin.sPass.value;
		},

		setPassword: function( sPass )
		{
			this.frmLogin.sPass.value = sPass;
		},

		isAutoChecked: function()
		{
			return this.btnAuto.checked;
		},

		setAuto: function( fCheck )
		{
			this.btnAuto.checked = fCheck;
		},

		promptLoginSuccess: function()
		{
			this.lblMessage.innerHTML = "&nbsp;";
			this.frmLogin.sUser.value = "";
			this.frmLogin.sPass.value = "";
			this.frmLogin.sUser.focus();
		},

		promptLoginAttempt: function()
		{
			this.lblMessage.innerHTML = "Please Wait";
			this.frmLogin.sUser.selectionStart = 0;
			this.frmLogin.sUser.selectionEnd = this.frmLogin.sUser.textLength;
			this.frmLogin.sUser.focus();
		},

		promptLoginFailed: function()
		{
			this.lblMessage.innerHTML = "Access Denied";
			this.frmLogin.sPass.value = "";
			this.frmLogin.sUser.selectionStart = 0;
			this.frmLogin.sUser.selectionEnd = this.frmLogin.sUser.textLength;
			this.frmLogin.sUser.focus();
		},

		promptExisting: function()
		{
			var fRet = confirm('You are already logged in.\nWould you like to terminate your other session?');
			if ( fRet ) {
				this.btnForce.click();
				return;
			}

			this.lblMessage.innerHTML = "Login Cancelled";
			this.frmLogin.sPass.value = "";
			this.frmLogin.sUser.selectionStart = 0;
			this.frmLogin.sUser.selectionEnd = this.frmLogin.sUser.textLength;
			this.frmLogin.sUser.focus();
		},

		promptError: function()
		{
			var sError = "An error occurred while attempting to login to the server. Please try again.\n" +
				"If this problem persists, please contact Dividia at 866-348-4342.";
			if ( arguments > 0 )
				sError = arguments[ 0 ];

			alert( sError );

			this.lblMessage.innerHTML = "&nbsp;";
			this.frmLogin.sPass.value = "";
			this.frmLogin.sUser.selectionStart = 0;
			this.frmLogin.sUser.selectionEnd = this.frmLogin.sUser.textLength;
			this.frmLogin.sUser.focus();
		},

		/*
		 * Private functions
		 */
		_onKey: function( e )
		{
			// summary: If the enter key is pressed, then move to the next field or submit login.

			try {
				if (e.keyCode == dojo.keys.ENTER) {
					if (e.target == this.frmLogin.sUser) {
						this.frmLogin.sPass.focus();
					} else if (e.target == this.frmLogin.sPass) {
						this.btnLogin.click();
					} else if (e.target == this.btnAuto) {
						this.btnLogin.click();
					}
					//e.preventDefault();
					dojo.stopEvent( e );
				}
			} catch(e) {
				console.debug( "Error handling key press [" + e + "]" );
				alert('Error handling key press');
			}
		},

		_onSubmit: function( e )
		{
			try {
				if (this.frmLogin.sPass.value == "") {
					this.frmLogin.sPass.focus();
				} else if (this.frmLogin.sPass != "") {
					this.btnLogin.click();
				}
				//e.preventDefault();
				dojo.stopEvent( e );
			} catch( e ) {
				console.debug( "Error handling submit [" + e + "]" );
				alert('Error handling submit');
			}
			return false;
		}

	}
);
