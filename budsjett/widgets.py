# imports copied from django.forms.widgets
from __future__ import absolute_import

import copy
import datetime
from itertools import chain
from urlparse import urljoin

from django.conf import settings
from django.forms.utils import flatatt, to_current_timezone
from django.utils.datastructures import MultiValueDict, MergeDict
from django.utils.html import escape, conditional_escape
from django.utils.translation import ugettext, ugettext_lazy
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils import datetime_safe, formats

from django import forms

class DynamicSelectMultiple(forms.SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):

        pre_selected = self.render_checkboxes(choices, value, attrs, name)
        
        options = u'<select onChange="dynamic_select_multiple(this)">%s</select>' % self.render_options(choices,())
        
        
        script = u"""
<script>
// javascript for dynamic_select_multiple
function dynamic_select_multiple(sel){
    var value = sel.options[sel.selectedIndex];
    var ul = sel.previousSibling;
    while(ul.nodeType!=1) ul = ul.previousSibling;
    for(var i = 0; i < ul.children.length; i++){
        var c = ul.children[i];
        if(c.attributes['value'].value == value.attributes['value'].value){
            c.style.display = "list-item";
            c.children[0].children[0].checked = true;
        }
    }
    // give default name if name is empty when konto is selected
    try{
        var name = document.getElementById(ul.attributes['name_id'].value)
        if(!name.value){
            name.value = value.innerText;
        }
    }catch(err){}
    sel.options.remove(sel.selectedIndex);
}
</script>
"""
        return mark_safe(pre_selected + options + script)

        
    def render_checkbox(self, has_id, final_attrs, attrs, i, str_values, name, option_value, option_label):
        # If an ID attribute was given, add a numeric index as a suffix,
        # so that the checkboxes don't all have the same ID attribute.
        if has_id:
            final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
            label_for = u' for="%s"' % final_attrs['id']
        else:
            label_for = ''
        
        option_value = force_unicode(option_value) 
        option_label = conditional_escape(force_unicode(option_label))
        if option_value in str_values:
            cb = forms.CheckboxInput(final_attrs)
            rendered_cb = cb.render(name, option_value)
            return u'<li value="%s"><label%s>%s %s</label></li>' % (option_value, label_for, rendered_cb, option_label)
        else:
            cb = forms.CheckboxInput(final_attrs, check_test=lambda value: False)
            rendered_cb = cb.render(name, option_value)
            return u'<li style="display:none" value="%s"><label%s>%s %s</label></li>' % (option_value, label_for, rendered_cb, option_label)
    
    def render_checkboxes(self, choices, value, attrs, name):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        if(has_id):
            pre_selected = [u'<ul name_id="%s">' % attrs['id'].replace('konto','name')]
        else:
            pre_selected = [u'<ul>']
        # Normalize to strings
        str_values = set([force_unicode(v) for v in value])
        i = 0;
        for (option_value, option_label) in chain(self.choices, choices):
            if isinstance(option_label, (list, tuple)):
                #do not uncomment. It breaks the javascript
#                pre_selected.append(u"<li>%s\n<ul>"% conditional_escape(option_value))
                for (sub_value, sub_label) in option_label:
                    pre_selected.append(self.render_checkbox(has_id, final_attrs, attrs, i, str_values, name, sub_value, sub_label))
#                pre_selected.append(u'</ul>')
            else:
                pre_selected.append(self.render_checkbox(has_id, final_attrs, attrs, i, str_values, name, option_value, option_label))
        pre_selected.append(u'</ul>')
        return u"\n".join(pre_selected)
    
    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_
