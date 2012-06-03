from jinja2 import Template

from Gui import *

PREFIX = "/tmp/grisbi/"
counter = 0

TEMPLATE = """\
{% for month in months() %}
    <div>
        <h1> {{ format_month(month, "%b %Y") }}</h1>
        {% set graph = build_graph("{fill;line;all;accu;invert;cat[6.12/6.9/6.5/6.11];dm[%s];}" % month) %}
        {% set graph2 = build_graph("{fill;line;day;invert;cat[6.12/6.9/6.5/6.11];dm[%s];}" % month) %}
        {% set graph3 = build_graph("{fill;line;all;invert;cat[6.12/6.9/6.5/6.11];dm[%s];}" % month, no_graph=True) %}
        
        <table>
            <tr><td><img src="{{ graph.img_path }}" title="{{ graph.src }}" /><td>
                <td><img src="{{ graph2.img_path }}" title="{{ graph2.src }}" /><td>
                <td>
                    <div>
                        <table style="text-align:left;">
                        {% for entry in graph.legend.values() %}
                            {% if entry.color is not none %}
                                <tr><th>{{ entry.name }}</th><td style="background-color:rgb{{ entry.color[0], entry.color[1], entry.color[2] }}">&nbsp;&nbsp;&nbsp;&nbsp;</td></tr> 
                            {% endif %}
                        {% endfor %}
                        </table>
                    </div>
                </td>
            </tr>
        </table>
        
        <div>
            <table>
            <tr>
                {% for uid in graph3.maths.uids %}
                  <td>
                    <h3> {{ graph3.legend[uid].name }}</h3>
                    <table style="text-align:right;">
                    {% for name in graph3.maths.names %}
                        <tr>
                            <th>{{ name }}</th>
                            {% for date in graph3.maths.dates %}
                                <td> {{ "%.2f" % graph3.maths.values[uid][date][name]}}</td>
                            {% endfor %}
                        </tr>
                        {% endfor %}
                    </table>
                  </td>
                {% endfor %}
            </tr>
            </table>
        </div>
    </div>
{% endfor %}
"""

var = ""
def months(start=None, stop=None):
    firstD, lastD = form.src.get_first_last_date()
    if start is not None:
        startMonth, startYear = start
    else:
        startMonth, startYear = form.firstD.month, form.firstD.year
    if stop is not None:
        stopMonth, stopYear = stop
    else:
        stopMonth, stopYear = form.lastD.month, form.lastD.year
    
    month = startMonth
    year = startYear
    while not (month >= stopMonth and year == stopYear):
        yield "%d/%d" % (year, month)
        month += 1
        if month == 13:
            month = 1
            year += 1

def format_month(month, frmt):
    return datetime.datetime.strptime(month, '%Y/%m').strftime("%B %Y")
        
class Graph:
    def __init__(self, img_path, legend, maths, src):
        self.img_path = img_path
        self.legend = legend
        self.maths = maths
        self.src = src

class Maths:
    def __init__(self, names, dates, uids, values):
        self.names = names
        self.dates = dates
        self.uids = uids
        self.values = values
        
def build_graph(conf_str, no_graph=False):
    global counter
    counter += 1  
    form.load_config(conf_str)
    if not no_graph:
        img_path = form.save_plot(PREFIX+"graph%d.png" % counter)
    else:
        img_path = "nop"
    
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
    
    if form.accu_cb.isChecked():
        uids = ["All"]
        legend["All"] = {"color":None, "name":"All"}
    else:
        uids = legend.keys()
    
    maths = Maths(uids=uids, names=form.tableMathModel.header, dates=dates, values=values)
    
    return Graph(img_path, legend, maths, conf_str)
    
def main():
    global form
    app = QApplication(sys.argv)
    form = AppForm()
    #form.show()
    template = Template(TEMPLATE)
    final = template.render(build_graph=build_graph, months=months, format_month=format_month)
    with open("%s/grisbi-report.html" % PREFIX, "w") as output:
        output.write(final)
    #form.show()
    #app.exec_()
    
if __name__ == "__main__":
    main()