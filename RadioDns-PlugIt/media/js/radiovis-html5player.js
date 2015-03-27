var radiovisplayer_first_image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUAAAADwCAYAAABxLb1rAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAadEVYdFNvZnR3YXJlAFBhaW50Lk5FVCB2My41LjExR/NCNwAAKRlJREFUeF7tnQWwHlf5h8Mfd4INM8AMaQYbpAMUd9o0ULRYcC0SnEKRFC0anGLBnUBxCRSXUKClQIDiBClaCO66//ts9r197/nec779ZK9wfs/MO/e7u8d295zfHt91jRBCVIoEUAhRLRJAIUS1SACFENUiARRCVIsEUAhRLRJAIUS1SACFENUiARRCVIsEUAhRLRJAIUS1SACFENXSWwCvcpWryGRr2oRIkQDKqjEhUiSAsmpMiBQJ4Jztute9bnPjG984tBvc4Aahn/8V4xpvd7vbNY94xCOaxz72sa098pGPbG5/+9u35yI/y2lCpEgA52zHHntsd8dGefOb3zzi/hrXuEbz/Oc/v/n85z/ffOUrX2ne9a53Nbe61a1G3K1Gu/nNb9484xnPaD7+8Y83v/rVr5p//etf3ZWO8u9//7t1g1v84DcKc0gTImXuAsjb/mEPe1ibyV/72tc273//+1t797vfvWgf+MAHmp07dzbPfOYzm3ve857N1a9+9TCstWgf+chHujs2yhOf+MQlbq91rWs1X//617uzp/OHP/yhudnNbrbE7WqyRz3qUc0Xv/jF5j//+U+X4snBL2EcddRRzVWvetUwnnmbEClzE8A73OEOzT/+8Y/O9WT8/e9/b4XjXve6Vxj2WrJTTz21u6pReDl4ty95yUu6M6O8/vWvX+J2pe3KV75yK3w//OEPuxTG/Pe//21+97vfNXv37m3tt7/9bXusBGHSbD7ooIPCuOdlQqTMTQCf/OQndy6nh1rBxz72sTXbV3ajG90o2wz85z//OVLAv/zlL3dnRznppJOWuF1JozZ6wgkndClbCrXV448/vnnKU57S3OUud2muf/3rN9e85jWbK13pSq3xm2N3vetdm6c97Wmt2z/96U+d79NBJD/72c8O2jQWImVuAvjWt761czk71AgQkyie1Wz3uc99uisY5ZRTThlx/93vfrc7O8p73/veEfcrYUceeWQrch7E6mtf+1qzbdu25trXvnbor2QMFOH3q1/9ahfi6fz+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';
var radiovisplayer_websockets = new Array();

function radiovisplayer_initsocket(topic, host, port) {

	ws = new WebSocket("ws://" + host + ":" + port + topic);

	// Save data for reconnection
	ws.radiovis_topic = topic;
	ws.radiovis_host = host;
	ws.radiovis_port = port;

	var elem = $('.radiovis-main[radiovis-topic="' + topic + '"]');
	elem.find('.radiovis-innertext').html('Connecting to ' + topic + '...');

	var radiovisplayer_connected_message = 'Connected, waiting for the first message !';

	ws.onmessage = function (evt) 
	{ 
		var elem = $('.radiovis-main[radiovis-topic="' + evt.target.radiovis_topic + '"]');
		

		message = evt.data;
		splited_message = message.split(':');

		if (splited_message[0] == 'RADIOVISWEBSOCKET') {  // Internal message
			if (splited_message[1] == 'HELLO\x00') {
				elem.find('.radiovis-innertext').html(radiovisplayer_connected_message);
				return;
			}
			if (splited_message[1] == 'ERROR') {
				elem.find('.radiovis-innertext').html('<span style="color: red;">Error: ' + splited_message[2] + '</span>');
				return;
			}

			elem.find('.radiovis-innertext').html('<span style="color: red;">Unexcepted reply: ' + splited_message[1] + '</span>');
		} else {
			command = '';
			headers = new Array();
			body = '';
			headerMode = true;

			data = evt.data.split('\n');
			if (data[0] != '') {
				command = data[0];
				start = 1;
			} else {
				command = data[1];
				start = 2;
			}

			for(var i = start; i < data.length; i++) {
				if (data[i] == '' && headerMode) {  // Switch from headers to body
					headerMode = false;
				} else if (headerMode) {  // Add header to the list
					sdata = data[i].split(':', 1);
					headers[sdata[0]] = data[i].substr(sdata[0].length+1);
				} else {  // Compute the body
					body += data[i] + '\n';
				}
			}

			// Remove the last \n
			body = body.substr(0, body.length-1);

			//Is it a message ?
			if (command == 'MESSAGE') {

				//Is it for text ?
				if (headers['destination']  == evt.target.radiovis_topic + '/text') {
					//Do we have to show text ?
					if (body.substr(0, 5) == 'TEXT ') {
						newText = body.substr(5);

						elem.find('.radiovis-innertext').text(newText);
					}
				}

				//Is it for images ?
				if (headers['destination']  == evt.target.radiovis_topic + '/image') {
					//Do we have to show an image ?
					if (body.substr(0, 5) == 'SHOW ') {

						//FInd the image to use						
						if (elem.attr('lastImageShown'))
							lastShow = elem.attr('lastImageShown');
						else 
							lastShow = '1';

						toShow = 1 - lastShow;

						//Set the src
						elem.find('.radiovis-I' + toShow).attr('src', body.substr(5));

						//Nice effect
						if(toShow == 1) {
							elem.find('.radiovis-I0').hide();
							elem.find('.radiovis-I1').fadeIn(1000);
						}
						else {
							elem.find('.radiovis-I0').fadeIn(1000);
							elem.find('.radiovis-I1').hide();
						}

						elem.attr('lastImageShown', toShow);

						//Some radio dosen't send text. If we're still on the default message, remove it
						if (elem.find('.radiovis-innertext').html() == radiovisplayer_connected_message)
							elem.find('.radiovis-innertext').html('');

						//Update link
						if (headers['link'])
							elem.find('a').attr('href', headers['link']);
						else
							elem.find('a').attr('href', '#');
					}
				}
			}

		}

		
	};
	ws.onclose = function(evt)
	{ 
		var elem = $('.radiovis-main[radiovis-topic="' + evt.target.radiovis_topic + '"]');
		elem.find('.radiovis-textframe').html('Connexion lost, reconnecting...');

		setTimeout("radiovisplayer_initsocket('" + evt.target.radiovis_topic + "', '" + evt.target.radiovis_host + "', " + evt.target.radiovis_port + ");", 1000)
	};

	radiovisplayer_websockets[topic] = ws;
}

(function( $ ) {
	$.fn.radiovisplayer = function(topic, host, port) {

		if (host == undefined)
			host = window.location.hostname;
		if (port == undefined)
			port = 8777;

		var frame = '<div class="radiovis-mainframe">';
		frame +=    '    <div class="radiovis-slideframe"';
		frame +=    '        <div class="radiovis-P1"><a href="" class="radiovis-LI"><img class="radiovis-I1" src="' + radiovisplayer_first_image + '"></a></div>';
		frame +=    '        <div class="radiovis-P0"><a href="" class="radiovis-LI"><img class="radiovis-I0" src="' + radiovisplayer_first_image + '"></a></div>';
		frame +=    '    </div>';
		frame +=    '</div>';
		frame +=    '<div class="radiovis-outtertext"><div class="radiovis-innertext">Initlialization...</div></div>';

		//Add the frame
		this.html(frame);

		//Add properties
		this.attr('radiovis-topic', topic);
		this.addClass('radiovis-main');

		//Scroll text
		this.find('.radiovis-outtertext').bind('scrollage', function() {
			var boxWidth = $(this).width();
			var textWidth = $(this).find('.radiovis-innertext').width();

			var finalPos =  textWidth - boxWidth;

			if (finalPos < 0)
				finalPos = 0;

			var animSpeed = finalPos * 20;

			if (animSpeed == 0)
				animSpeed = 1000;

			$(this)
				.animate({scrollLeft: finalPos}, {duration : animSpeed})
				.animate({scrollLeft: 0}, {duration : animSpeed, queue: true, complete: function() {
					$(this).trigger('scrollage');
				}
			});
		}).trigger('scrollage');

		radiovisplayer_initsocket(topic, host, port);		
		
		return this;
	};
}( jQuery ));