var SelectSearchBox = {};

SelectSearchBox.prototype = function(searchBox, select, jumpto){
    var d = {};
    d.elementlist = []
    
    d.pick = function(element){
        select.val(element.id);
        select.change();
        searchBox.value = "";
        jumpto.focus();
        }

    d.filteredElements = function(searchString){
        var reg = new RegExp(searchString,"i");
        var filtered = [];
        for(e in d.elementlist){
            if(d.elementlist[e].label.match(reg)){filtered.push(d.elementlist[e])}
            }
        return filtered;
        }
        
    d.search = function(){
        var activeElements = d.filteredElements(searchBox.val());
        if (activeElements.length == 1){
            d.pick(activeElements[0]);
            return;
        }else{
            d._renderOptionList(activeElements);
        }
    }

    d.startsearch = function(){
      searchBox.value = "";
      d._renderOptionList(d.elementlist);
    }
    

    d._optionList = null;
    d._renderOptionList = function(elements){
        if(d._optionList == null){
            d._optionList = $('<div></div>').css({
                    position: "absolute",
                    top: searchBox.position().top + "px",
                    left: (searchBox.position().left + searchBox.outerWidth()) + "px",
                    border: "1px solid black",
                    background: "#CCCCCC"
                });
            d._optionList.appendTo(searchBox.parent()).show();
        }else{
            d._optionList.children().remove();
            d._optionList.show();
        }
        
        for(var i in elements){
            var e = elements[i]
            $($('<div></div>').text(e.label)).mousedown(function(){d.pick(e);d.endsearch();}).appendTo(d._optionList);
        }
    };

    d._hideOptionList = function(){
        if(d._optionList != null){
            d._optionList.hide();
        }
    }
    
    d.endsearch = function(){searchBox.val(''); setTimeout(d._hideOptionList,20)};
    
    return d;
 }

SelectSearchBox.init = function(searchBox, select, jumpto){
    dynamics = SelectSearchBox.prototype($(searchBox), $(select), $(jumpto));

    $(select).find('option').each(function(){
        var a = {};
        a.id = this.value;
        a.label = this.text;
        dynamics.elementlist.push(a);
    });
  $(searchBox).keyup(dynamics.search);
  $(searchBox).focusin(dynamics.startsearch);
  $(searchBox).focusout(dynamics.endsearch);
}