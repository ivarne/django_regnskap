//simple jquery plugin for making an autocomplete box and filling out a
//relation table set on the fly.

(function( $ ){
  $.fn.autocompleteFill = function(options) {
    // set defaults for settings
    var settings = $.extend({
      'prefix'        : '',    // to use to find form elements
      'server-search' : false, // if set to a property
      'server-url'    : null,
      'match_order'   : null,
      'num'           : 10
    },options);
    // add event to search
    var searchdiv = $("<div>").addClass('search-div');
    searchdiv.hide()
    this.after(searchdiv);
    var searchField = this;
    var contacts = {};
    var contactList = [];
    $.getJSON(settings["server-url"], function(c) {
      contactList = c;
      for(var key in c){
          contacts[c[key]['id']] = c[key];
      }
    });
    var setExternal = function(id){
      for(var key in settings.match_order ){
        key = settings.match_order[key];
        $("#" + settings.prefix + key ).val(contacts[id][key]);
      }
    };
    
    this.focusin(function(){
      searchdiv.show()
      var table = $(this).closest('table');
      table.find('input').val(null);
      table.find('textarea').val(null)
    });
    
    this.focusout(function(){
      setTimeout(function(){
        searchdiv.hide();
        searchdiv.empty();
      },80);
      var v = parseInt(this.value);
      if(isNaN(v)){
        v = "";
      }
      this.value = v;
    });
    
    searchdiv.mousedown(function(e){
      setExternal( e.target.attributes['ext_id']);
    });
    this.keyup(function(){
      searchdiv.empty();
      if (this.value.length == 0){
        return // empty string should not match anything
      }
      var reg = new RegExp(this.value,"i");
      var local_contact = contactList.slice(0); // take a copy
      var match = [];
      
      
      
      breakout:
      for(var key in settings.match_order ){
        key = settings.match_order[key];
        for (var id = 0; id < local_contact.length; id++){
          var c = local_contact[id];
          if(c[key].toString().match(reg)){
            match.push(c);
            local_contact.splice(id,1);
            id--;
            if(match.length > settings.num){
              break breakout;
            }
          }
        }
      }
      // now I have an orderd list of matches
      if(match.length == 1){
        $(this).blur();
        return setExternal(match[0]['id']);
      }
      for(var i = 0; i < match.length; i++){
        //TODO: some fancy styling
        var tmp = $("<div>").text(match[i].name);
        tmp[0].attributes['ext_id'] = match[i].id;
        tmp.appendTo(searchdiv);
      }
    });
  };
})( jQuery );
