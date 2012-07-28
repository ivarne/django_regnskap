//simple jquery plugin for adding days from a input field to get a valid range
//requires jquery ui datepicker

(function( $ ){
  $.fn.dateAdd = function(options) {
    // set defaults for settings
    var settings = $.extend({
      'dateField' : null, // if set to a property
      'addField'  : null,
      'format'    : 'yy-mm-dd',
    },options);
    var date = settings['dateField'];
    var add = settings['addField'];
    var disp = this;
    var update = function(){
      var d = new Date(date[0].value);
      var a = parseInt(add[0].value);
      // add a days + 1/2 day to ensure propper roundoff
      d.setTime(d.getTime() + (a *24*60*60*1000) + (12*60*60*1000));
      disp[0].value = $.datepicker.formatDate(settings['format'],d);
    };
    update();
    date.change(update);
    add.change(update);
    var update_add = function(){
      var start = new Date(date[0].value);
      var end   = new Date(disp[0].value);
      var diff  = (end.getTime() - start.getTime()) / (24*60*60*1000);
      if(add[0].value != diff.toString()){
        add[0].value = diff;
      }
    };
    disp.change(update_add);
    return this;
  };
})( jQuery );
