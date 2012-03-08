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
      'num'           : 10,
    },options);
    // add event to search
    var searchdiv = $("<div>").addClass('search-div');
    searchdiv.hide()
    this.after(searchdiv);
    
    var contacts = [];
    $.getJSON(settings["server-url"], function(c) {
      //restructure json (the default django export does not suit my needs)
      for(var i in c){
        var con = c[i];
        con.fields["id"] = con.pk.toString();
        contacts.push(con.fields);
      }
     });
    this.focusin(function(){
      searchdiv.show()
      for(var key in settings.match_order ){
        key = settings.match_order[key];
        $("#" + settings.prefix + key ).val(null);
      }
    });
    this.focusout(function(){
      setTimeout(function(){searchdiv.hide();searchdiv.empty()},20);
    });
    this.keyup(function(){
      var reg = new RegExp(this.value,"i");
      var local_contact = contacts.slice(0); // take a copy
      var match = [];
      
      searchdiv.empty();
      
      breakout:
      for(var key in settings.match_order ){
        key = settings.match_order[key];
        for (var id = 0; id < local_contact.length; id++){
          var c = local_contact[id];
          if(c[key].match(reg)){
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
        for(var key in settings.match_order ){
          key = settings.match_order[key];
          $("#" + settings.prefix + key ).val(match[0][key]);
        }
        this.value = match[0].id;
        return
      }
      for(var i = 0; i < match.length; i++){
        //TODO: some fancy styling
        $("<div>").text(match[i].name).appendTo(searchdiv);
      }
    });
  };
})( jQuery );
