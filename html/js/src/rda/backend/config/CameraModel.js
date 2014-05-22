/**
 *
 * Store CameraModel settings.
 * Enabled, Name, etc.
 *
 * @author Ryan Ayers
 */

dojo.provide( "rda.backend.config.CameraModel" );

dojo.require( "rda.common.Observable" );
dojo.require( "rda.config.Store" );
dojo.require( "rda.backend.config.Camera" );

dojo.declare(
	"rda.backend.config.CameraModel",
	[ rda.common.Observable ],
	{
		_sSess: "",
		_oStore: null,
		_rgoCamera: null,

		_fLoaded: false,

		constructor: function()
		{
			this._oStore = rda.config.Store.getInstance();

			this.reset();
		},


		/**
		 * Load camera information from camera.
		 * This will load all config and rights information per camera.
		 */
		load: function()
		{
			try {
				// Setup camera backend
				var oServer = this._oStore.get( "oServer" );

				// Pull from camera
				rgsResult = oServer.Query( "config.camera.getAllCameras", this._sSess );
				this._rgoCamera = new Array();
				for ( var ix = 0; ix < rgsResult.length; ix++ )
					this._rgoCamera.push( new rda.backend.config.Camera( rgsResult[ ix ] ) );

				this._fLoaded = true;
				this.setChanged();
				this.notifyObservers();

			} catch ( e ) {
				console.debug( "Camera Model Load [" + e + "]" );
				alert( "Error querying camera list" );
				this._fLoaded = false;
				this.setChanged();
				this.notifyObservers();
			}
		},

		/**
		 * Check if we successfully loaded
		 */
		checkIsLoaded: function()
		{
			return this._fLoaded;
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
			this._rgoCamera = null;
			this._sSess = "";

			this._fLoaded = false;
			//this.setChanged();
			//this.notifyObservers();
		},

		/**
		 * Return a mixed camera list of (id/name) pairs.
		 *
		 * @return Camera List
		 */
		getList: function()
		{
			return this._rgoCamera;
		},

		/**
		 * Get a Camera Object by Serial
		 *
		 * @param bSerial
		 *  Serial of camera to get
		 *
		 * @return Camera
		 */
		getCamera: function( bSerial, bCamera )
		{
			for ( var ix = 0; ix < this._rgoCamera.length; ix++ )
				if ( this._rgoCamera[ ix ].getSerial() == bSerial && 
				     this._rgoCamera[ ix ].getCamera() == bCamera )
					return this._rgoCamera[ ix ];
			throw new Error( "unknown camera serial-[" + bSerial + "] camera-[" + bCamera + "]" );
		},

		/**
		 * Set a Camera Object
		 *
		 * @param oCamera
		 *  Camera object to replace (matches on ID)
		 */
		setCamera: function( oCamera )
		{
			try {
				for ( var ix = 0; ix < this._rgoCamera.length; ix++ ) {
					if ( this._rgoCamera[ ix ].getSerial() == oCamera.getSerial() &&
					     this._rgoCamera[ ix ].getCamera() == oCamera.getCamera() ) {
						// Setup camera backend
						var oServ = this._oStore.get( "oServer" );
						rgsResult = oServ.Query( "config.camera.setCamera", this._sSess, oCamera.freeze() );

						// Save locally
						this._rgoCamera[ ix ] = oCamera;
						this.setChanged();
						this.notifyObservers();
						return;
					}
				}

				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "Error updating camera information id-[" + oCamera.getSerial() + "]" );
			}
		},

		/**
		 * Delete camera object from server and our list.
		 *
		 * @param oCamera
		 *  Camera object to delete
		 *
		 * @return True/False if it worked
		 */
		delCamera: function( oCamera )
		{
			try {
				for ( var ix = 0; ix < this._rgoCamera.length; ix++ ) {
					if ( this._rgoCamera[ ix ].getSerial() == oCamera.getSerial() &&
					     this._rgoCamera[ ix ].getCamera() == oCamera.getCamera() ) {
						// Setup camera backend
						var oServ = this._oStore.get( "oServer" );
						fResult = oServ.Query( "config.camera.delCamera", this._sSess, oCamera.freeze() );

						if ( fResult ) {
							this._rgoCamera.splice( ix, 1 );
							this.setChanged();
							this.notifyObservers();
						}

						return fResult;
					}
				}

				throw new Error( "not found" );

			} catch ( e ) {
				throw new Error( "Error updating camera information id-[" + oCamera.getSerial() + "]" );
			}
		}

	}
);
