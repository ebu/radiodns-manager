/**
* Purpose: Add toolbar to epiceditor
*/

var EPICEDITOR_TOOLBAR_LIST = {};


//Add selection functions. This part has been inspired from https://github.com/Gankro/EpicEditor/commit/7189c95019960573cc78622c00f2a3a3143a141b

  EpicEditor.prototype._getSelection = function () {
    return $(this.element).find('iframe')[0].contentDocument.getElementById('epiceditor-editor-frame').contentDocument.getSelection();
  };

  EpicEditor.prototype.prependSelection = function (text, htmlMode) {


  	var selection = this._getSelection();
  	var range = selection.getRangeAt(0);
  	var content = range.extractContents()

  	if (htmlMode) {
  		var div = document.createElement('span');
  		div.innerHTML = text;
  	} else {
  		var div = document.createTextNode(text);
  	}
  	content.insertBefore(div, content.firstChild);
  	range.insertNode(content);

  };

  EpicEditor.prototype.appendSelection = function (text, htmlMode) {


    var selection = this._getSelection();
  	var range = selection.getRangeAt(0);
  	var content = range.extractContents()

  	if (htmlMode) {
  		var div = document.createElement('span');
  		div.innerHTML = text;
  	} else {
  		var div = document.createTextNode(text);
  	}
  	content.appendChild(div);
  	range.insertNode(content);


  };

  EpicEditor.prototype.wrapSelection = function (startText, endText) {
    this.appendSelection(endText || startText);
    this.prependSelection(startText);
  };

  EpicEditor.prototype.getSelectedText = function () {
    return this._getSelection().toString();
  };

function epiceditor_hook(zeEditor) {

	if ($(zeEditor.element).attr('ebuio_toolbar'))
		return;
	$(zeEditor.element).attr('ebuio_toolbar', true)

	epic_id = $(zeEditor.element).attr('id');

	zeToolBar = '<div style="margin: 0; margin-bottom: 5px;" epic_id="' + epic_id + '" class="btn-toolbar">' +
      '<div class="btn-group">' +
      '  <span class="btn btn-default" act="h1">H1</span>' +
      '  <span class="btn btn-default" act="h2">H2</span>' +
      '  <span class="btn btn-default" act="h3">H3</span>' +
      '  <span class="btn btn-default" act="h4">H4</span>' +
      '</div>' +
      '<div class="btn-group">' +
      '  <span class="btn btn-default" act="b"><i class="fa fa-bold"></i></span>' +
      '  <span class="btn btn-default" act="i"><i class="fa fa-italic"></i></span>' +
      '  <span class="btn btn-default" act="bi"><i class="fa fa-bold"></i><i class="fa fa-italic"></i></span>' +
      '</div>' +
      '<div class="btn-group">' +
      '  <span class="btn btn-default" act="url"><i class="fa fa-link"></i></span>' +
      '  <span class="btn btn-default" act="img"><i class="fa fa-picture-o"></i></span>' +
      '</div>' +
      '<div class="btn-group">' +
      '  <span class="btn btn-default" act="ul"><i class="fa fa-list-ul"></i></span>' +
      '  <span class="btn btn-default" act="ol"><i class="fa fa-list-ol"></i></span>' +
      '  <span class="btn btn-default" act="code"><i class="fa fa-code"></i></span>' +
      '  <span class="btn btn-default" act="hr"><i class="fa fa-minus"></i></span>' +
      '</div>' +

     '</div>';

    //Append the toolbar
	$(zeEditor.element).before(zeToolBar);

	EPICEDITOR_TOOLBAR_LIST[epic_id] = zeEditor;

	//Hook mouse click
	$('div[epic_id="' + epic_id + '"] span').on('click',function(event) {

		editor = EPICEDITOR_TOOLBAR_LIST[$(event.target).parent().parent().attr('epic_id')];

		switch($(event.target).attr('act')) {
			case 'h1': editor.prependSelection('# ');
				break;
			case 'h2': editor.prependSelection('## ');
				break;
			case 'h3': editor.prependSelection('### ');
				break;
			case 'h4': editor.prependSelection('### ');
				break;
			case 'b': editor.wrapSelection('**');;
				break;
			case 'i': editor.wrapSelection('*');;
				break;
			case 'bi': editor.wrapSelection('***');;
				break;
			case 'ul': editor.prependSelection('* ');
				break;
			case 'ol': editor.prependSelection('1. ');
				break;
			case 'url': editor.wrapSelection('[', '](http://link)');
				break;
			case 'img': editor.wrapSelection('![', '](http://link)');
				break;
			case 'code': editor.wrapSelection('`');
				break;
			case 'hr': editor.prependSelection('<br>* * *<br>', true);
				break;

		}
	});

	$('div[epic_id="' + epic_id + '"] span i').on('click',function(event) {
		$(event.target).parent().click();
	});


}