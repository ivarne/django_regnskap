"""
A simple class to simplify formatting of tables in django
"""
class TableCell(object):
    def __init__(self, value, **kwargs):
        self.value = value
        self.properties = kwargs
    def render(self):
        v = self.value
        if self.properties.has_key('bold'):
            v = u"<b>%s</b>" % v
        if self.properties.has_key('italics'):
            v = u"<i>%s</i>" % v
        if self.properties.has_key('cssclass'):
            c = u" class=\"%s\"" % self.properties['cssclass']
        else: c = u""
        if self.properties.has_key('head'):
            v = u"\t\t<th%s>%s</th>\n" % (c, v)
        else:
            v = u"\t\t<td%s>%s</td>\n" % (c, v)
        return v

class TableRow(object):
    def __init__(self,*args):
        self.cells = list(args)
    def render(self):
        c = u"".join(cell.render() for cell in self.cells)
        return u"\t<tr>%s</tr>\n" % c

class Table(object):
    def __init__(self,numRows = 0):
        self.rows = []
        self.reset()
    def append_cell(self,cell):
        self.counter+=1
        if self.counter > len(self.rows):
            return self.rows.append(TableRow(cell))
        self.rows[self.counter-1].cells.append(cell)
    def reset(self):
        self.counter = 0
    def render(self):
        r = u"".join(row.render() for row in self.rows)
        return u"\n<table>\n%s</table>\n" % r