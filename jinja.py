from jinja2 import Template

from Gui import *

PREFIX = "/tmp/grisbi/"
counter = 0

TEMPLATE = """\
Hello {{ name }} 

{% set first = build_graph("{math;month;line;cat[25.2/25.1/11.3];d1[2011/01/01];d2[2012/05/31];}") %}

Image: {{ first.img_path }}
Legend:
{% for entry in first.legend.values() %}
    {{ entry.name }} --> {{ entry.color }}
{% endfor %}

Maths:

 * Names
{% for name in first.maths.names %}
    {{ name }}

    * Dates
    {% for date in first.maths.dates %}
        {{ date }}
    
        * Uids
        {% for uid in first.maths.uids %}
            {{ uid }}
            --> {{first.maths.values[uid][date][name]}}
        {% endfor %}
    {% endfor %}
{% endfor %}
"""

var = ""
def months(startMonth, startYear, stopMonth, stopYear):
    month = startMonth
    year = startYear
    while not (month >= stopMonth and year == stopYear):
        yield month, year
        month += 1
        if month == 13:
            month = 1
            year += 1

def format_date((year, month, day), frmt):
    return "Not yet"
        
class Graph:
    def __init__(self, img_path, legend, maths):
        self.img_path = img_path
        self.legend = legend
        self.maths = maths
        pass

class Maths:
    def __init__(self, names, dates, uids, values):
        self.names = names
        self.dates = dates
        self.uids = uids
        self.values = values
        
def build_graph(conf_str):
    global counter
    counter += 1  
    form.load_config(conf_str)
    img_path = form.save_plot(PREFIX+"graph%d.png" % counter)
    
    legend = {}
    for item_idx in xrange(form.listSelected.count()):
        item = form.listSelected.item(item_idx)
        name = item.text()
        uid = str(item.data(Qt.UserRole).toPyObject())
        color = item.data(Qt.BackgroundRole).toPyObject().getRgb()
        legend[uid] = {"color":color, "name":name}
        print name, color, uid
    
    dates = dates=form.tableMathModel.dates
    values = {}
    for uid, uid_data in form.tableMathModel.values.items():
        values[uid] = dict(zip(dates, uid_data))
        
    maths = Maths(uids=legend.keys(), names=form.tableMathModel.header, dates=dates, values=values, format_date=format_date)
    
    return Graph(img_path, legend, maths)
    
def main():
    global form
    app = QApplication(sys.argv)
    form = AppForm()
    
    template = Template(TEMPLATE)
    final = template.render(build_graph=build_graph)
    print ">>> %s <<<" % final
    #form.show()
    #app.exec_()
    
if __name__ == "__main__":
    main()