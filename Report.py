import os, errno

from jinja2 import Template, Environment, PackageLoader

from Gui import *

class Counter:
    def __init__(self):
        self.cnt = 0


class Env:
    def __init__(self, form, dir_prefix):
        self.form = form
        self.dir_prefix = dir_prefix
        self.counter = Counter()
        
    def months(self, start=None, stop=None):
        firstD, lastD = self.form.src.get_first_last_date()
        if start is not None:
            startMonth, startYear = start
        else:
            startMonth, startYear = self.form.firstD.month, self.form.firstD.year
        if stop is not None:
            stopMonth, stopYear = stop
        else:
            stopMonth, stopYear = self.form.lastD.month, self.form.lastD.year
        
        month = startMonth
        year = startYear
        while not (month >= stopMonth and year == stopYear):
            yield "%d/%d" % (year, month)
            month += 1
            if month == 13:
                month = 1
                year += 1

    def format_month(self, month, frmt):
        return datetime.datetime.strptime(month, '%Y/%m').strftime("%B %Y")
        
    def build_graph(self,conf_str, no_graph=False):
        self.counter.cnt += 1  
        self.form.load_config(conf_str)
        if not no_graph:
            img_path = self.form.save_plot(self.dir_prefix+"graph%d.png" % self.counter.cnt)
        else:
            img_path = "nop"
        
        legend = {}
        for item_idx in xrange(self.form.listSelected.count()):
            item = self.form.listSelected.item(item_idx)
            name = item.text()
            uid = str(item.data(Qt.UserRole).toPyObject())
            color = item.data(Qt.BackgroundRole).toPyObject().getRgb()
            legend[uid] = {"color":color, "name":name}
        
        dates = self.form.tableMathModel.dates
        
        values = {}
        for uid, uid_data in self.form.tableMathModel.values.items():
            values[uid] = dict(zip(dates, uid_data))
        
        if self.form.accu_cb.isChecked():
            uids = ["All"]
            legend["All"] = {"color":None, "name":"All"}
        else:
            uids = legend.keys()
        
        maths = Maths(uids=uids, names=self.form.tableMathModel.header, dates=dates, values=values)
        
        return Graph(img_path, legend, maths, conf_str)
        
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
    
def main():
    app = QApplication(sys.argv)
    form = AppForm()
    final = to_transform(form, "templates/first.html.jing", "/tmp/grisbi/first.html")

    
def to_transform(form, source_name, target_name):
    with open(source_name, "r") as innput:
        templ_src = innput.read()
        
    template = Template(templ_src)
    
    build_prefix = "%s_files/" % target_name
    
    mkdir_p(build_prefix)
    
    env = Env(form, build_prefix)
    
    final = template.render(build_graph=env.build_graph, months=env.months, format_month=env.format_month)
    with open(target_name, "w") as output:
        output.write(final)

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

if __name__ == "__main__":
    main()