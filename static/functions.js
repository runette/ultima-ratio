//#MIT License

//#Copyright (c) 2019 Paul Harwood

//#Permission is hereby granted, free of charge, to any person obtaining a copy
//#of this software and associated documentation files (the "Software"), to deal
//#in the Software without restriction, including without limitation the rights
//#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
//#copies of the Software, and to permit persons to whom the Software is
//#furnished to do so, subject to the following conditions:

//#The above copyright notice and this permission notice shall be included in all
//#copies or substantial portions of the Software.

//#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
//#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
//#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
//#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
//#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
//#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
//#SOFTWARE.

var DISCOVERY_DOCS = ["https://sheets.googleapis.com/$discovery/rest?version=v4"];

      // Authorization scopes required by the API; multiple scopes can be
      // included, separated by spaces.
var SCOPES = "https://www.googleapis.com/auth/spreadsheets";
var CLIENT_ID = '927628257279-n6qtj2jk165emkona4hhac9bulgh4jke.apps.googleusercontent.com';
var API_KEY = 'AIzaSyDZcNCn8CzpdFG58rzRxQBORIWPN9LOVYg';

(function ($, callback) {
    if (typeof $ === 'function') {
        callback($)
    }
})(window.jQuery, function ($) {
    
    var $win = $(window);
    
     // Initialize fancybox
    function initFancybox(){
        $('[data-fancybox]').fancybox({
	    protect: true
        })}

	// Initialize Firebase
    function initFirebase(){
	var config = {
	  apiKey: API_KEY,
	  authDomain: "ultima-ratio-221014.firebaseapp.com",
	  databaseURL: "https://ultima-ratio-221014.firebaseio.com",
	  projectId: "ultima-ratio-221014",
	  storageBucket: "ultima-ratio-221014.appspot.com",
	  messagingSenderId: "927628257279",
	  clientId: CLIENT_ID,
	  scopes: [
	     "email",
	     "profile",
	    ],
	  discoveryDocs: DISCOVERY_DOCS
	};
	var app = firebase.initializeApp(config);
	let ui = new firebaseui.auth.AuthUI(firebase.auth(app));
	
	// FirebaseUI config.
		let uiConfig = {
		  callbacks:{
		  signInSuccessWithAuthResult: function(authResult, redirectUrl){
			let user=authResult.user;
			user.getIdToken().then(function (token) {
			    setCookie("token", token)
			    $('#login').text("Logout");
			    $('#login-modal').modal('hide')
			    if (window.location.pathname.includes('/database/entry')) {location.reload(true)} else {window.location.href ="/database"}
			    })
			    
			return false
		    },
		    signInFailure: function(error){
			return alert(stringify(error))
		    }
		    },
		    
		  signInOptions: [
		    // Comment out any lines corresponding to providers you did not check in
		    // the Firebase console.
		    {
			provider:firebase.auth.GoogleAuthProvider.PROVIDER_ID,
			scopes: config.scopes
			},
		    firebase.auth.EmailAuthProvider.PROVIDER_ID,
		    {
			provider: firebase.auth.FacebookAuthProvider.PROVIDER_ID,
			scopes: [
			    'public_profile',
			    'email',
			],
		    },
		    //firebase.auth.TwitterAuthProvider.PROVIDER_ID,
		    //firebase.auth.GithubAuthProvider.PROVIDER_ID,
		    //firebase.auth.PhoneAuthProvider.PROVIDER_ID,
		
	      
		  ],
		  // Terms of service url.
		  tosUrl: '/tor',
		  privacyPolicyUrl: '/privacy'
		};
	
	if (ui.isPendingRedirect()){
	    $('#firebaseui-auth-container').text("");
	    $('#login-modal').modal('show')
	    ui.start('#firebaseui-auth-container', uiConfig);
	    }
	
	firebase.auth().onAuthStateChanged(function (user) {
	    if (user) {
		      // User is signed in, so display the "sign out" button and login info.
		    user.getIdToken().then(function (token) {
			    setCookie("token", token)
			    });
		    console.log(`Signed in as ${user.displayName} (${user.email})`);
		    if ($('#login')[0].innerText === "Login") {
			sessionStorage.removeItem('database');
			window.location.href ="/" 
		    }
		    $('#login').click(function(){
		     firebase.auth().signOut()
		     clearCookie('token');
		     sessionStorage.removeItem('database');
		     $('#firebaseui-auth-container').text("You are now logged out");
		     $('[data-dismiss="modal"]').click(function(){window.location.href ="/" });
	    })} else {
		    $('#login').click(function(){
		    $('#firebaseui-auth-container').text("");
		     ui.start('#firebaseui-auth-container', uiConfig);
		     })};
	    }, function (error) {
		    console.log(error);
		    alert('Unable to log in: ' + error)
		  });
      }

    function initialize() {
	initFirebase();
        initFancybox();
        let update_list = $('.update-field');
        if (update_list) {
            for (var i = 0; i < update_list.length; i++) {
                let element = update_list[i];
                select_button(element.id,)
            }
        };
	$('.custom-file-input').on('change',function(){
		let fileName = ""
		let files = this.files;
		for (let file of files) { 
		    if ( fileName.length > 0){ fileName += ","}
		    fileName += file.name
		}
		$(this).next('.custom-file-label').addClass("selected").html(fileName); 
	});
	
    }
    $(initialize);
});
// Facebook API
//window.fbAsyncInit = function() {
    //FB.init({
        //appId      : '685963501504199',
        //xfbml      : true,
        //version    : 'v2.4'
    //});
//};

function select_button ( cl) {
        let action = "hide";
        let button = $('#' + cl);
        if (button.is(':checked')) {
            action = 'show'
        }
        if (action === "show") {
            $('.' + cl).show()
        }
        else {
            $('.' + cl).hide()
        }
    }

    function radio_button ( name ) {
        let elements = $("input[name=" + name + "]");
        let action;
        for (let i = 0; i < elements.length; i++) {
            let button = $('#' + elements[i].id ) ;
            if (button.is(':checked')) {
                $('.' + button[0].id).show()
            }
            else {
                $('.' + button[0].id).hide()
            }
        }
    }

//(function(d, s, id){
    //var js, fjs = d.getElementsByTagName(s)[0];
    //if (d.getElementById(id)) {return;}
    //js = d.createElement(s); js.id = id;
    //js.src = "//connect.facebook.net/en_US/sdk.js";
    //fjs.parentNode.insertBefore(js, fjs);
//}(document, 'script', 'facebook-jssdk'));


    //from https://stackoverflow.com/a/16808048/9652221
    async function send_file_worker(folder, callback) {
	    $('#file-upload').prop('disabled', true);
	    let imageRef, root
	    let storage = firebase.storage();
	    if (dev) {
		root="dev"
	    }
	    else {
		root="prod"
	    }
	    let files = $('.custom-file-input')[0].files;
	    if (! files) {return}
	    $('.progress').removeClass('hidden');
	    let number_files = Object.keys(files).length
	    let count = 0
	    for (let file of files) {
		let file_name = file.name;
		imageRef = storage.ref().child(root).child(folder).child(file_name + "/original");
		console.log ("uploading " + imageRef.fullPath);
		let uploadTask = imageRef.put(file);
		uploadTask.on('state_changed', function(snapshot){
			let progress = (Math.floor(snapshot.bytesTransferred / snapshot.totalBytes * 10) * 10 / number_files) + (100/number_files*count);
			$('.progress-bar').css('width', progress + '%')
			})
		let snapshot = await uploadTask
		console.log('Uploaded a blob or file!');
		$('#status-message').html('<p>Your image is being processed and you will be taken to the new record shortly.</p><p> If this does not happen, your record will almost certainly have been created. Go to the Database screen using the BACK button and check the last record.</p>')
		let payload = JSON.stringify(snapshot.metadata)
		let addphoto = $.ajax({
			    url: "/add_photo?id=" + folder,
			    contentType: "application/json",
			    method: "POST",
			    data: payload
			});
		addphoto.done(function (data, textStatus, jqXHR) {
			    data = JSON.parse(data);
			    $("#imgs").append(
				`<a href="${data.original}" data-fancybox="image-gallery" data-caption="cannon photo">
				<img src="${data.s200}" alt="" />`);
			    console.log(data);
			    if (callback) {callback(folder)};
			    $('.custom-file-input').val(null);
			    $('#file-upload').prop('disabled', false);
			})
		count += 1;
		}
		$('.custom-file-label').removeClass("selected").html("");
		$('.progress').addClass('hidden');
		$('.progress-bar').css('width', '0%')
	}
	
    function send_file() {
	if ($('.custom-file-input')[0].files.length > 0) {
	    let folder = $('#id').val().toString();
	    send_file_worker(folder, null)
	} else {
		$('#file-upload').prop('disabled', false);
	}
	
    };

    function BNG_convert(form) {
        let data = $('form').serializeArray();
        let index = jQuery.grep(data, function(n,i) { return n['name'] === "eastings" });
        let eastings = index[0]['value'];
        index = jQuery.grep(data, function(n,i) { return n['name'] === "northings" });
        let northings = index[0]['value'];
        let convert = $.post("/bng_convert?eastings=" + eastings + "&northings=" + northings);
        convert.done(function (data, textStatus, jqXHR) {
            let json_data = JSON.parse(data);
            $('#lat').val(json_data['LATITUDE']);
            $('#lon').val(json_data['LONGITUDE']);
            reset_map()
        });
        convert.fail (function (jqXHR, textStatus) {
            alert('conversion failed : ' + textStatus)}
        );

    }
    function LL_convert(form) {
        let data = $(form).serializeArray();
        let index = jQuery.grep(data, function(n,i) { return n['name'] === "lat" });
        let lat = index[0]['value'];
        index = jQuery.grep(data, function(n,i) { return n['name'] === "lon" });
        let lon = index[0]['value'];
        let convert = $.post("/ll_convert?lat=" + lat + "&lon=" + lon);
        convert.done(function (data, textStatus, jqXHR) {
            let json_data = JSON.parse(data);
            $('#eastings').val(json_data['EASTING']);
            $('#northings').val(json_data['NORTHING']);
        });
        convert.fail (function (jqXHR, textStatus) {
            alert('conversion failed : ' + textStatus)}
        );
        radio_button('geolocation','bng')
    }
    function reset_map(location) {
	if (! location) {
	location = {
	    lat: parseFloat($('#lat').val()),
	    lng: parseFloat($('#lon').val())
	};}
        map.setCenter(location);
        if (marker != null) {
            marker.setMap(null);
            marker = null;
        }
        marker = new google.maps.Marker({
                            position: location,
                            map: map,
                            icon: map_icons[marker_quality],
                            draggable:true,
                        });
        google.maps.event.addListener(marker, 'dragend', function(){
            let location = marker.getPosition();
            $('#lat').val(location.lat);
            $('#lon').val(location.lng);
	    form_changed();
        });

    }
    function getLocation() {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition, showError);
      } else {
            alert("Geolocation is not supported by this browser.");
      }
    }

    function showPosition(position) {
      $('#lat').val(position.coords.latitude);
      $('#lon').val(position.coords.longitude);
      reset_map()
    }

    function showError(error) {
        switch (error.code) {
            case error.PERMISSION_DENIED:
                alert( "User denied the request for Geolocation.");
                break;
            case error.POSITION_UNAVAILABLE:
                alert( "Location information is unavailable.");
                break;
            case error.TIMEOUT:
                alert("The request to get user location timed out.");
                break;
            case error.UNKNOWN_ERROR:
                alert("An unknown error occurred.");
                break;
        }
    }
    
    function locate_action(name) {
	getLocation();
	radio_button(name);
    }
    //from https://www.quirksmode.org/js/cookies.html
    function setCookie(name,value){
	createCookie(name, value, 0.1)
	}
	
    function createCookie(name,value, days) {
	if (days) {
	    var date = new Date();
	    date.setTime(date.getTime()+(days*24*60*60*1000));
	    var expires = "; expires="+date.toGMTString();
	    }
	else var expires = "";
	document.cookie = name + "="+value + expires + "; path=/";
	}
	
    function clearCookie(name){
	createCookie(name,"",-1);
    }
    
    function readCookie(name) {
	var nameEQ = name + "=";
	var ca = document.cookie.split(';');
	for(var i=0;i < ca.length;i++) {
	    var c = ca[i];
	    while (c.charAt(0)==' ') c = c.substring(1,c.length);
	    if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length,c.length);
	    }
	return null;
	}
	
    function makeApiCall() {
	gapi.load('client:auth2', initClient);
	}
		
    function onReady() {
      let spreadsheetBody = {
	"properties":{
	    "title": Date()
	}
      };
      let request = gapi.client.sheets.spreadsheets.create({}, spreadsheetBody);
      let spreadsheetUrl;
      let spreadsheetId;
      request.then(response => {
	spreadsheetId = response.result.spreadsheetId;
	spreadsheetUrl = response.result.spreadsheetUrl;
	let params = {
	    spreadsheetId: '1cv6qL_VukZUef9zEKDMNZOf9knUFRzfzydkx5DI1ndo',
	    sheetId: 0,
	};
	let body = {
	    destinationSpreadsheetId: spreadsheetId,   
	};
	request = gapi.client.sheets.spreadsheets.sheets.copyTo(params, body)
	request.then( response => {
	    let win = window.open(spreadsheetUrl, '_blank');
	    win.focus();
	}, function(reason){
	console.error('error: ' + reason.result.error.message);
	})
	
      }, function(reason) {
	console.error('error: ' + reason.result.error.message);
      });
    }

      /**
       *  Initializes the API client library and sets up sign-in state
       *  listeners.
       */
      function initClient() {
	gapi.client.init({
	  clientId: CLIENT_ID,
	  discoveryDocs: DISCOVERY_DOCS,
	  scope:SCOPES,
	}).then( function() {
	    let options = new gapi.auth2.SigninOptionsBuilder(
		{'scope': SCOPES},
		);
	    let auth = gapi.auth2.getAuthInstance();
	    let googleUser = auth.currentUser.get();
	    googleUser.grant(options).then(
		auth => {
		  onReady();
		}, function(error) {
		  console.error(JSON.stringify(error, null, 2));
		}
	    )}
	);
      };
    












