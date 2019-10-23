//simple jquery plugin for making an autocomplete box and filling out a
//relation table set on the fly.

(function( $ ){
  $.fn.varenummerUpdate = function(options) {
    // set defaults for settings
    var settings = $.extend({
      'varer' : {},
    },options);
    
    var vareList = settings['varer'];
    var varer = {};// oppslag på varer med varenummer
    for(var i in vareList){
      varer[vareList[i]['id']] = vareList[i];
    }
    var setVare = function(vare, child_of_row){
      var row = child_of_row.closest('tr');
      row.find('.vare-id').val(vare.id);
      row.find('.vare-text').val(vare.name);
      row.find('.vare-antall').val('1');
      row.find('.vare-pris').val(vare.price);
      row.change();
    };
    
    // add event to search
    var sd = $("<div>").addClass('search-div');
    sd.hide()
    sd.mousedown(function(e){
      setVare( varer[ e.target.attributes['ext_id'] ], $(e.target));
    });
    this.after(sd);
    
    this.focusin(function(){
      $(this).closest('tr').find('input').val(null).change();
      $(this.nextSibling).show();
      
    });
    
    this.focusout(function(){
      var searchdiv = $(this.nextSibling);
      setTimeout(function(){
        searchdiv.hide();
        searchdiv.empty();
      },80);
      var v = parseInt(this.value);
      if(v && varer[v] !== undefined){
        setVare(varer[v],searchdiv);
        this.value = v;
      }else{
        // clare row
        $(this).closest('tr').find('input').val(null).change();
      }
    });
    
    
    this.keyup(function(){
      if (this.value.length == 0){
        return // empty string should not match anything
      }
      
      var searchdiv = $(this.nextSibling);
      var reg = new RegExp(this.value,"i");
      var match = [];
      
      if(parseInt(this.value)){
        return; // do not search for numeric values (wait untill focusout)
      }
      searchdiv.empty();
      for(var i = 0; i < vareList.length; i++){
        var vare = vareList[i];
        if (vare.name.toString().match(reg)){
          //TODO: some fancy styling
          var tmp = $("<div>").text('('+vare.id + ') ' + vare.name);
          tmp[0].attributes['ext_id'] = vare.id;
          tmp.appendTo(searchdiv);
        }
      }
      // now I have an orderd list of matches
      if(searchdiv[0].children.length == 1){
        this.blur();
        searchdiv.hide();
        setVare( varer[ searchdiv[0].children[0].attributes['ext_id'] ], searchdiv);
      }

    });
  };
})( jQuery );
