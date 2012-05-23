import sys, os, random
import datetime
from collections import OrderedDict

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import PolyCollection
from matplotlib.collections import LineCollection
from matplotlib import dates as mdates

from GuiGrisbi import GrisbiDataProvider

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Grisbi Data Plotter')
        
        self.src = GrisbiDataProvider()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        #self.on_draw()
        
    def save_plot(self):
        file_choices = "PNG (*.png)|*.png"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            self.statusBar().showMessage('Saved to %s' % path, 2000)
    
    def on_about(self):
        msg = """ A data plotter for Grisbi bank account files
        """
        QMessageBox.about(self, "About the plotter", msg.strip())
    
    def set_startD(self, dateTxt=None):
        def set_d(d): self.startD = d
        return self.set_date(set_d, self.startD_lbl, dateTxt)
    
    def set_stopD(self, dateTxt=None):
        def set_d(d): self.stopD = d
        return self.set_date(set_d, self.stopD_lbl, dateTxt)
    
    def set_date(self, set_d, where_lbl, dateTxt=None):
        if dateTxt is None:
            dateTxt = str(self.textDate.text())
            self.textDate.setText("")
        
        try:
            date = datetime.datetime.strptime(dateTxt, '%Y/%m/%d')
        except TypeError as e:
            print e
            self.textDate.setText("invalid date (%s), expected YYYY/MM/DD" % dateTxt)
            return
        
        where_lbl.setText(date.strftime('%Y/%m/%d'))
        
        set_d(date)
    
    def change_listAcc(self):
        return self.change_listCatAcc(self.listAcc)
    def change_listCat(self):
        return self.change_listCatAcc(self.listCat)
        
    def change_listCatAcc(self, fromList):
        current_uids = []
        for item_idx in xrange(self.listSelected.count()):
            item = self.listSelected.item(item_idx)
            current_uids.append(str(item.data(Qt.UserRole).toPyObject()))
        
        for item in fromList.selectedItems():
            name, uid = [str(x) for x in item.data(Qt.UserRole).toPyObject().items()[0]]
            
            if not uid in current_uids:
                item = QListWidgetItem(name)
                item.setData(Qt.UserRole, uid)
                self.listSelected.addItem(item)
            else:
                current_uids.remove(uid)
        
        if len(current_uids) != 0:
            to_remove = []
            for item_idx in range(self.listSelected.count()):
                item = self.listSelected.item(item_idx)
                uid = str(item.data(Qt.UserRole).toPyObject())
                if uid in current_uids:
                    to_remove.append(item_idx)
            
            for item_idx in sorted(to_remove)[::-1]:
                self.listSelected.takeItem(item_idx)
            
    def change_GType(self):
        gtype = str(self.cboxGType.itemData(self.cboxGType.currentIndex()).toPyObject())
        
        isPie = "pie" in gtype
        isLine = "line" in gtype
        
        is3d = "3d" in gtype
        
        no_reset = self.radioCategory.isChecked()
        if isPie:
            self.radioCategory.setChecked(True)
        self.change_AccCat(no_reset=no_reset)
        self.radioAccount.setDisabled(isPie)
        
        
        self.radioMonth.setDisabled(isPie)
        self.radioDay.setDisabled(isPie)
        if isPie:
            self.radioAll.setChecked(True)
            
        self.legend_cb.setDisabled(isPie or is3d)
        self.accu_cb.setDisabled(isPie or is3d)
        self.fill_cb.setDisabled(isPie)
        
        if is3d:
            from mpl_toolkits.mplot3d import Axes3D
            if not self.axes.name == "3d":
                self.axes = self.fig.gca(projection='3d')
        else:
            if not self.axes.name == "rectilinear":
                self.axes = self.fig.add_subplot(111)
    
    def change_AccCat(self, no_reset=False):
        self.listAcc.setDisabled(not self.radioAccount.isChecked())
        self.listCat.setDisabled(self.radioAccount.isChecked())
        
        self.radioMonth.setDisabled(self.radioAccount.isChecked())
        self.radioDay.setDisabled(self.radioAccount.isChecked())
        self.invert_cb.setDisabled(self.radioAccount.isChecked())
        
        if not no_reset:
            self.listSelected.clear()
        
    def dclick_listSelected(self, itemIndex):
        idx = itemIndex.row()
        if idx != 0:
            item = self.listSelected.takeItem(idx)
            self.listSelected.insertItem(idx - 1, item)
            self.listSelected.setCurrentItem(item)
    
    def on_draw(self):
        """ Redraws the figure
        """
        gtype = str(self.cboxGType.itemData(self.cboxGType.currentIndex()).toPyObject())
        
        legend = self.legend_cb.isChecked()
        inverted = self.invert_cb.isChecked()
        frequence = None
        if self.radioMonth.isChecked():
            frequence = "month"
        elif self.radioDay.isChecked():
            frequence = "day"
            
        accu = self.accu_cb.isChecked()
        fill = self.fill_cb.isChecked()
        
        if "pie" in gtype:
            frequence = None
        
        selected = OrderedDict()
        for item_idx in xrange(self.listSelected.count()):
            item = self.listSelected.item(item_idx)
            uid = item.data(Qt.UserRole).toPyObject()
            name = item.text()
            selected[str(uid)] = str(name)
        
        if self.radioAccount.isChecked():
            subcategories = None
            accounts = selected.keys()
        else:
            accounts = None
            subcategories = selected.keys()
        
        labels = [entry for entry in selected.values()]
        
        def datetime_to_datelist(date):
            return date.year, date.month, date.day
        
        print "Get the data"
        data = self.src.get_data(inverted, frequence, datetime_to_datelist(self.startD), datetime_to_datelist(self.stopD), subcategories=subcategories, accounts=accounts)
        print "------------"
        
        
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()
        
        plots = []
        previous = 0
        series = []
        
        if "pie" in gtype:
            pie_values = []
        
        dates = []
        for date in data.keys():
            dates.append(datetime.datetime.strptime(date, '%Y-%m-%d'))
        
        left = range(len(data.values()))
        colors = get_next_color()
        maxVal = 0
        minVal = 0
        for key in selected.keys():
            plot = None
            print "Plot %s" % selected[key]
            current = [dct[key] for dct in data.values() if len(dct.values()) != 0]
            if "line" in gtype:
                color = colors.next()
                actual_current = current
                
                if accu and previous != 0:
                        actual_current = [k+j for k, j in zip(previous, current)]
                if fill:
                    self.axes.fill_between(dates, previous, actual_current, color=color)
                    
                # format the ticks
                #self.axes.xaxis.set_major_locator(mdates.MonthLocator())
                #self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y %m'))
                #self.axes.xaxis.set_minor_locator(mdates.MonthLocator())
                plot = self.axes.plot_date(dates, actual_current, color=color, linestyle='-', marker="")
                self.fig.autofmt_xdate()
                
                if accu:
                    previous = actual_current
            elif "pie" in gtype:
                plot = pie_values.append(current[-1])
            elif "3d curves" in gtype:
                series.append(current)
                maxVal = max(current + [maxVal])
                minVal = min(current + [minVal])
            else:
                print "no mode selected ... "+gtype
            
            plots.append(plot)
            self.canvas.draw()
        
        if "pie" in gtype:
            self.axes.pie(pie_values, labels=labels, autopct='%1.0f%%', shadow=True)
        
        if "3d curves" in gtype:
            
            self.axes.mouse_init()
            xs = [float(x) for x in range(len(data.values()))]
            zs = [float(x) for x in range(len(series))]
                
            verts = []
            for seri in series:
                if fill:
                    seri[0], seri[-1] = 0, 0
                verts.append(zip(xs, seri))
            
            if fill:
                poly = PolyCollection(verts, facecolors=[colors.next() for x in range(len(series))])
            else:
                poly = LineCollection(verts, colors=[colors.next() for x in range(len(series))])
                
            poly.set_alpha(0.7)
            
            self.axes.add_collection3d(poly, zs=zs, zdir="y")
            
            self.axes.set_ylim3d(-1, len(series))
            self.axes.set_yticks(range(len(series)))
            self.axes.set_xlim3d(0, len(data.values()))
            self.axes.set_zlim3d(minVal, maxVal)
            
        if legend and "line" in gtype:
            self.axes.legend(labels)
        
        self.canvas.draw()
        print "============"
        
    def create_main_frame(self):
        self.main_frame = QWidget()
        
        # Create the mpl Figure and FigCanvas objects. 
        # 5x4 inches, 100 dots-per-inch
        #
        self.dpi = 100
        self.fig = Figure((5.0, 4.0), dpi=self.dpi)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        
        # Since we have only one plot, we can use add_axes 
        # instead of add_subplot, but then the subplot
        # configuration tool in the navigation toolbar wouldn't
        # work.
        #
        
        self.axes = self.fig.add_subplot(111)
        
        # Create the navigation toolbar, tied to the canvas
        #
        #self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        #         
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        self.accu_cb = QCheckBox("Accumulate ?")
        self.accu_cb.setChecked(False)
        self.connect(self.accu_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.fill_cb = QCheckBox("Fill ?")
        self.fill_cb.setChecked(False)
        self.connect(self.fill_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.legend_cb = QCheckBox("Legend ?")
        self.legend_cb.setChecked(False)
        self.connect(self.legend_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.invert_cb = QCheckBox("Inverted ?")
        self.invert_cb.setChecked(False)
        self.connect(self.invert_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        
        self.radioDay = QRadioButton("Daily")
        self.connect(self.radioDay, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.radioMonth = QRadioButton("Monthly")
        self.connect(self.radioMonth, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.radioAll = QRadioButton("All")
        self.connect(self.radioAll, SIGNAL('stateChanged(int)'), self.on_draw)
        self.radioAll.setChecked(True)
        
        self.startD = datetime.datetime.today()
        self.stopD = datetime.datetime.today()
        
        firstD, lastD = self.src.get_first_last_date()
        
        self.textDate = QLineEdit()
        self.startD_button = QPushButton("&Start date")
        self.connect(self.startD_button, SIGNAL('clicked()'), self.set_startD)
        self.startD_lbl = QLabel(self)
        #self.startD_lbl.move(130, 260)
        
        self.stopD_button = QPushButton("&Stop date")
        self.connect(self.stopD_button, SIGNAL('clicked()'), self.set_stopD)
        self.stopD_lbl = QLabel(self)
        
        self.set_startD(str(firstD))
        self.set_stopD(str(lastD))
        #self.stopD_lbl.move(130, 260)
        
        def add_item_to_cbox(cbox, name, data):
            cbox.addItem(name, QVariant(data))
        
        def add_item_to_list(lst, name, data):
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, data)
            lst.addItem(item)
            return item
        
        self.cboxGType = QComboBox()
        add_item_to_cbox(self.cboxGType, "Line", "line")
        add_item_to_cbox(self.cboxGType, "Pie", "pie")
        add_item_to_cbox(self.cboxGType, "3D curves", "3d curves")
        self.connect(self.cboxGType, SIGNAL('currentIndexChanged(QString)'), self.change_GType)
        
        self.listCat = QListWidget()
        self.listCat.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.connect(self.listCat, SIGNAL('itemSelectionChanged()'), self.change_listCat)
        
        for cat, name in self.src.get_categories().items():
            add_item_to_list(self.listCat, name, {name:cat})
            
        self.listAcc = QListWidget()
        self.listAcc.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        self.listAcc.setDisabled(True)
        self.connect(self.listAcc, SIGNAL('itemSelectionChanged()'), self.change_listAcc)
        
        for acc, name in self.src.get_accounts().items():
            add_item_to_list(self.listAcc, name, {name:acc})
        
        self.listSelected = QListWidget()
        self.listSelected.doubleClicked.connect(self.dclick_listSelected)
        
        self.radioCategory = QRadioButton("Categories")
        self.radioCategory.setChecked(True)
        self.connect(self.radioCategory, SIGNAL('clicked()'), self.change_AccCat)
        self.radioAccount = QRadioButton("Accounts")
        self.connect(self.radioAccount, SIGNAL('clicked()'), self.change_AccCat)
        
        #
        # Layout with box sizers
        
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        #vbox.addWidget(self.mpl_toolbar)
        
        def add_box(elements):
            box = QHBoxLayout()
            for w in elements:
                box.addWidget(w)
                box.setAlignment(w, Qt.AlignVCenter)
            
            vbox.addLayout(box)
            return box
        
        add_box([self.invert_cb, self.legend_cb])
        add_box([self.radioDay, self.radioMonth, self.radioAll])
        add_box([self.cboxGType])
        add_box([self.accu_cb, self.fill_cb])
        add_box([self.startD_lbl, self.startD_button, self.textDate,  self.stopD_button, self.stopD_lbl])
        add_box([self.radioCategory, self.radioAccount])
        add_box([self.listCat, self.listSelected, self.listAcc])
        add_box([self.draw_button])
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    
    def create_status_bar(self):
        self.status_text = QLabel("This is a demo")
        self.statusBar().addWidget(self.status_text, 1)
        
    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu("&File")
        
        load_file_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot, 
            tip="Save the plot")
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q", tip="Close the application")
        
        self.add_actions(self.file_menu, 
            (load_file_action, None, quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about, 
            tip='About the plotter')
        
        self.add_actions(self.help_menu, (about_action,))

    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, 
                      icon=None, tip=None, checkable=False, 
                      signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        #return action

def get_next_color():
    colors = ["blue", "green", "red", "cyan", "magenta", "yellow", "black"]
    i = 0
    while True:
        yield colors[i % len(colors)]
        i += 1

def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()
