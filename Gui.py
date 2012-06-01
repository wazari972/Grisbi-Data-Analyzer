#!/usr/bin/env python2

# comment out if not relevant
DEFAULT_ACCOUNT = "in/kevin.gsb"

import sys, os, random
import datetime
from collections import OrderedDict
import StringIO
import pickle
import calendar

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.collections import PolyCollection
from matplotlib.collections import LineCollection
from matplotlib import dates as mdates
import matplotlib.cm as cm

from GuiGrisbi import GrisbiDataProvider

WINDOW_NAME = 'Grisbi Data Plotter: %s'

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        
        self.create_menu()
        
        self.src = None
        try:
            path = DEFAULT_ACCOUNT
            self.src = GrisbiDataProvider(path)
            self.set_current_file(path)
        except NameError:
            while self.src is None:
                self.open_grisbi(initial=True)
        
        self.create_main_frame()
        #self.on_draw()
    
    def on_about(self):
        msg = """ A data plotter for Grisbi bank account files
        """
        QMessageBox.about(self, "About the plotter", msg.strip())
    
    def set_startD(self, dateTxt=None):
        return self.set_date(self.startD_lbl, dateTxt, is_start=True)
    
    def set_stopD(self, dateTxt=None):
        return self.set_date(self.stopD_lbl, dateTxt, is_start=False)
    
    def set_date(self, where_lbl, dateTxt=None, is_start=False):
        if dateTxt is not None:
            date = datetime.datetime.strptime(dateTxt, '%Y/%m/%d')
        else:
            date = self.cBoxDate.itemData(self.cBoxDate.currentIndex()).toPyObject()
            if date is None:
                return
        
        if is_start:
            self.startD = datetime.datetime(date.year, date.month, 1)
        else:
            last_day = calendar.monthrange(date.year, date.month)[1]
            self.stopD = datetime.datetime(date.year, date.month, last_day)
            
        where_lbl.setText((self.startD if is_start else self.stopD).strftime('%Y/%m/%d'))
        
    def set_startstop_dates(self):
        firstD, lastD = self.src.get_first_last_date()
        
        self.set_startD(str(firstD))
        self.set_stopD(str(lastD))
        
        self.cBoxDate.clear()
        
        add_item_to_cbox(self.cBoxDate, "Date", None)
        
        start_month = self.startD.month
        end_months = (self.stopD.year - self.startD.year) * 12 + self.stopD.month + 1
        for m in range(start_month, end_months):
            yr, mn = ((m - 1) / 12 + self.startD.year, (m - 1) % 12 + 1)
            d = datetime.datetime(year=yr, month=mn, day=1)
            add_item_to_cbox(self.cBoxDate, d.strftime("%B %Y"), d)
        
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
        
        if isPie:
            if not self.radioCategory.isChecked():
                self.radioCategory.setChecked(True)
                self.change_AccCat()
        
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
        self.radioCategory.setChecked(not self.radioAccount.isChecked())
        self.radioAccount.setChecked(not self.radioCategory.isChecked())
        
        self.listAcc.setDisabled(not self.radioAccount.isChecked())
        self.listCat.setDisabled(self.radioAccount.isChecked())
        
        self.radioMonth.setDisabled(self.radioAccount.isChecked())
        self.radioDay.setDisabled(self.radioAccount.isChecked())
        if not no_reset:
            self.radioAll.setChecked(True)
            
        self.invert_cb.setDisabled(self.radioAccount.isChecked())
        
        if not no_reset:
            self.listSelected.clear()
            
            if self.radioAccount.isChecked():
                to_unselect = self.listCat
            else:
                to_unselect = self.listAcc
            for item in to_unselect.selectedItems():
                to_unselect.setItemSelected(item, False)
        
    def dclick_listSelected(self, itemIndex):
        idx = itemIndex.row()
        if idx != 0:
            item = self.listSelected.takeItem(idx)
            self.listSelected.insertItem(idx - 1, item)
            self.listSelected.setCurrentItem(item)
            
    def showHideMaths(self):
        self.tableMath.setVisible(self.maths_cb.isChecked())
        
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
        
        count = self.listSelected.count()
        colors = get_next_qt_color(count)
        selected = OrderedDict()
        for item_idx in xrange(count):
            item = self.listSelected.item(item_idx)
            uid = item.data(Qt.UserRole).toPyObject()
            name = item.text()
            selected[str(uid)] = str(name)
            item.setData(Qt.BackgroundRole, colors.next())
            
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
        data = self.src.get_data(inverted, frequence, accu, datetime_to_datelist(self.startD), datetime_to_datelist(self.stopD), subcategories=subcategories, accounts=accounts)
        print "------------"
        
        graphData, mathData = data["graph"], data["maths"]
        
        self.tableMath.clearSpans()
        
        key = "All" if accu else selected.keys()[0]
        if len(mathData[key]) != 0:
            header = mathData[key][0].keys()
        else:
            header = []
        values = mathData
        
        tm = MyTableModel(values, header, selected.keys() if not accu else ["All"], frequence) 
        self.tableMath.setModel(tm)
        
        self.tableMath.setShowGrid(False)
        
        if frequence is None:
            self.tableMath.verticalHeader().setVisible(False)
        else:
            self.tableMath.verticalHeader().setVisible(True)
        self.tableMath.resizeColumnsToContents()
        self.tableMath.setSortingEnabled(False)
        
        # clear the axes and redraw the plot anew
        #
        self.axes.clear()
        
        plots = []
        previous = 0
        series = []
        
        if "pie" in gtype:
            pie_values = []
        
        dates = []
        for date in graphData.keys():
            dates.append(datetime.datetime.strptime(date, '%Y-%m-%d'))
        
        left = range(len(graphData.values()))
        
        maxVal = 0
        minVal = 0
        colors = get_next_color(len(selected.keys()))
        for key in selected.keys():
            plot = None
            print "Plot %s" % selected[key]
            current = [dct[key] for dct in graphData.values() if len(dct.values()) != 0]
            if "line" in gtype:
                color = colors.next()
                actual_current = current
                
                if accu and previous != 0:
                        actual_current = [k+j for k, j in zip(previous, current)]
                if fill:
                    self.axes.fill_between(dates, previous, actual_current, color=color)

                #plot = self.axes.plot_date(dates, actual_current, color=color, linestyle='-', marker="")
                plot = self.axes.plot_date(dates, actual_current, c=color, linestyle='-', marker="")
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
            xs = [float(x) for x in range(len(graphData.values()))]
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
            self.axes.set_xlim3d(0, len(graphData.values()))
            self.axes.set_zlim3d(minVal, maxVal)
            
        if legend and "line" in gtype:
            #Shink current axis by 20%
            box = self.axes.get_position()
            self.axes.set_position([box.x0, box.y0, box.width * 0.8, box.height])
            
            # Put a legend to the right of the current axis
            self.axes.legend(labels, loc='center left', bbox_to_anchor=(1, 0.5))
            
            #self.axes.legend(labels)
        
        self.canvas.draw()
        print "============"
    
    def populateAccCat(self):
        def add_item_to_list(lst, name, data):
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, data)
            lst.addItem(item)
            return item
        
        self.listCat.clear()
        for cat, name in self.src.get_categories().items():
            if cat == "0.0":
                continue
            add_item_to_list(self.listCat, name, {name:cat})
    
        self.listAcc.clear()
        for acc, name in self.src.get_accounts().items():
            add_item_to_list(self.listAcc, name, {name:acc})
            
        self.listSelected.clear()
    
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
        
        self.tableMath = QTableView()
        
        # Other GUI controls
        #         
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        self.accu_cb = QCheckBox("Accumulate ?")
        self.accu_cb.setChecked(False)
        
        self.fill_cb = QCheckBox("Fill ?")
        self.fill_cb.setChecked(False)
        
        self.legend_cb = QCheckBox("Legend ?")
        self.legend_cb.setChecked(False)
        
        self.maths_cb = QCheckBox("Maths ?")
        self.maths_cb.setChecked(True)
        self.connect(self.maths_cb, SIGNAL('stateChanged(int)'), self.showHideMaths)
        
        self.invert_cb = QCheckBox("Inverted ?")
        self.invert_cb.setChecked(False)
        
        self.grpFrequency = QGroupBox("Frequency")
        self.radioDay = QRadioButton("Daily", self.grpFrequency)
        self.radioMonth = QRadioButton("Monthly", self.grpFrequency)
        self.radioAll = QRadioButton("All", self.grpFrequency)
        self.radioAll.setChecked(True)
        
        vboxFrequency = QVBoxLayout()
        vboxFrequency.addWidget(self.radioDay)
        vboxFrequency.addWidget(self.radioMonth)
        vboxFrequency.addWidget(self.radioAll)
        self.grpFrequency.setLayout(vboxFrequency);
        
        self.startD = datetime.datetime.today()
        self.stopD = datetime.datetime.today()
        
        self.cBoxDate = QComboBox()
        self.startD_button = QPushButton("&Start date")
        self.connect(self.startD_button, SIGNAL('clicked()'), self.set_startD)
        self.startD_lbl = QLabel(self)
        
        self.stopD_button = QPushButton("&Stop date")
        self.connect(self.stopD_button, SIGNAL('clicked()'), self.set_stopD)
        self.stopD_lbl = QLabel(self)
        
        self.set_startstop_dates()
        
        self.cboxGType = QComboBox()
        add_item_to_cbox(self.cboxGType, "Line", "line")
        add_item_to_cbox(self.cboxGType, "Pie", "pie")
        add_item_to_cbox(self.cboxGType, "3D curves", "3d curves")
        self.connect(self.cboxGType, SIGNAL('currentIndexChanged(QString)'), self.change_GType)
        
        self.listCat = QListWidget()
        self.listCat.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.connect(self.listCat, SIGNAL('itemSelectionChanged()'), self.change_listCat)
        
        self.listAcc = QListWidget()
        self.listAcc.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        self.listAcc.setDisabled(True)
        self.connect(self.listAcc, SIGNAL('itemSelectionChanged()'), self.change_listAcc)
        
        self.listSelected = QListWidget()
        self.listSelected.doubleClicked.connect(self.dclick_listSelected)
        
        self.populateAccCat()
        
        self.grpCatAcc = QGroupBox("Data type")
        self.radioCategory = QRadioButton("Categories", self.grpCatAcc)
        self.radioCategory.setChecked(True)
        self.connect(self.radioCategory, SIGNAL('clicked()'), self.change_AccCat)
        self.radioAccount = QRadioButton("Accounts", self.grpCatAcc)
        self.connect(self.radioAccount, SIGNAL('clicked()'), self.change_AccCat)
        
        vboxRadio = QVBoxLayout()
        vboxRadio.addWidget(self.radioCategory)
        vboxRadio.addWidget(self.radioAccount);
        #vboxRadio.addStretch(1);
        self.grpCatAcc.setLayout(vboxRadio);
        
        #
        # Layout with box sizers
        
        vbox = QVBoxLayout()
        
        def add_box(elements, box_type=QHBoxLayout, do_add=True, is_widget=True):
            box = box_type()
            for w in elements:
                if is_widget:
                    box.addWidget(w)
                else:
                    box.addLayout(w)
                box.setAlignment(w, Qt.AlignVCenter)
            if do_add:
                vbox.addLayout(box)
            return box
        
        #box = add_box([self.canvas, self.tableMath])
        box = QHBoxLayout()
        self.canvas.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        self.tableMath.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.MinimumExpanding)
        
        box.addWidget(self.canvas)
        box.addWidget(self.tableMath)
        vbox.addLayout(box)
        
        opt_boxes = [add_box([self.cboxGType, self.maths_cb, self.legend_cb], box_type=QVBoxLayout, do_add=False),
                     add_box([self.grpFrequency], do_add=False),
                     add_box([self.accu_cb, self.fill_cb, self.invert_cb], box_type=QVBoxLayout, do_add=False)]
        
        add_box(opt_boxes, is_widget=False)
        
        add_box([self.startD_lbl, self.startD_button, self.cBoxDate,  self.stopD_button, self.stopD_lbl])
        box.setAlignment(self.radioAccount, Qt.AlignRight)
        
        add_box([self.grpCatAcc, self.listCat, self.listSelected, self.listAcc])
        add_box([self.draw_button])
        
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
        
    def create_menu(self):
        self.file_menu = self.menuBar().addMenu("&File")
        
        open_grisbi_action = self.create_action("&Open Grisbi File",
            shortcut="Ctrl+O", slot=self.open_grisbi)
        
        info_config_action = self.create_action("&Current Configuration",
            shortcut="Ctrl+C", slot=self.current_config)
        
        save_png_action = self.create_action("&Save plot",
            shortcut="Ctrl+S", slot=self.save_plot)
            
        save_config_action = self.create_action("&Save configuration",
            shortcut="Ctrl+Shift+S", slot=self.save_config)
        
        open_config_action = self.create_action("&Open configuration",
            shortcut="Ctrl+Shift+O", slot=self.open_config)
        
        quit_action = self.create_action("&Quit", slot=self.close, 
            shortcut="Ctrl+Q")
        
        QShortcut(QKeySequence("Ctrl+G"), self, self.on_draw)
        
        self.add_actions(self.file_menu, 
                            (open_grisbi_action, None, 
                            save_png_action, None, 
                            info_config_action, open_config_action, save_config_action, None, 
                            quit_action))
        
        self.help_menu = self.menuBar().addMenu("&Help")
        about_action = self.create_action("&About", 
            shortcut='F1', slot=self.on_about)
        
        self.add_actions(self.help_menu, (about_action,))
        
    def save_plot(self):
        file_choices = "PNG (*.png)"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save file', '', 
                        file_choices))
        if path:
            self.canvas.print_figure(path, dpi=self.dpi)
            
    def open_grisbi(self, initial=False):
        file_choices = "Grisbi Account (*.gsb)"
        path = unicode(QFileDialog.getOpenFileName(self, 
                        'Open file', '', 
                        file_choices))
        if path:
            self.src = GrisbiDataProvider(path)
            if not initial:
                self.populateAccCat()
                self.set_startstop_dates()
            self.set_current_file(path)
        return path
    
    def current_config(self):
        conf_str = str(self.create_config())
        Configuration.restore_from_string(conf_str, self)
        QMessageBox.information(self, "Current configuration", str(conf_str), "Thanks")
        
        
    def create_config(self):
        selected = []
        for item_idx in xrange(self.listSelected.count()):
            item = self.listSelected.item(item_idx)
            uid = item.data(Qt.UserRole).toPyObject()
            selected.append(uid)
        
        if self.radioAccount.isChecked():
            subcategories = None
            accounts = selected
        else:
            accounts = None
            subcategories = selected
        frequency = "month" if self.radioMonth.isChecked() else "day" if self.radioDay.isChecked() else "all"
        conf = Configuration(
            math=self.maths_cb.isChecked(),
            accu=self.accu_cb.isChecked(),
            fill=self.fill_cb.isChecked(),
            invert=self.invert_cb.isChecked(),
            legend=self.legend_cb.isChecked(),
            frequency=frequency,
            gtype=str(self.cboxGType.itemData(self.cboxGType.currentIndex()).toPyObject()),
            startD=self.startD,
            stopD=self.stopD,
            subcategories=subcategories,
            accounts=accounts)
        return conf
        
    def save_config(self):
        conf = self.create_config()
        
        file_choices = "Grisbi Graph Configuration (*.ggc)"
        
        path = unicode(QFileDialog.getSaveFileName(self, 
                        'Save configuration', '', 
                        file_choices))
        if path:
            with open(path, "w") as output:
                output.write(str(conf))

    def open_config(self):
        file_choices = "Grisbi Graph Configuration (*.ggc)"
        path = unicode(QFileDialog.getOpenFileName(self, 
            'Open file', '', 
            file_choices))
        if path:
            with open(path, "r") as inputfile:
                conf_str = inputfile.read()
                Configuration.restore_from_string(conf_str, self)
                
    def add_actions(self, target, actions):
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)

    def create_action(self, text, slot=None, shortcut=None, 
                      icon=None, checkable=False, 
                      signal="triggered()"):
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(":/%s.png" % icon))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if slot is not None:
            self.connect(action, SIGNAL(signal), slot)
        if checkable:
            action.setCheckable(True)
        return action
        
    def set_current_file(self, filename):
        filename = filename.split("/")[-1]
        self.setWindowTitle(WINDOW_NAME % filename)
        
def get_next_qt_color(count):
    for color in get_next_color(count):
        qcolor = QColor()
        qcolor.setRedF(color[0])
        qcolor.setGreenF(color[1])
        qcolor.setBlueF(color[2])
        qcolor.setAlphaF(0.5)
        
        yield qcolor

def get_next_color(count):
    cNorm  = matplotlib.colors.Normalize(vmin=0, vmax=count)
    scalarMap = cm.ScalarMappable(norm=cNorm, cmap=cm.jet)
    
    for i in range(count):
        yield scalarMap.to_rgba(i)

def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

class MyTableModel(QAbstractTableModel): 
    def __init__(self, values, header, groups, frequence): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QAbstractTableModel.__init__(self) 
        
        self.values = values
        self.header = header
        self.groups = groups
        self.dates = values["date"]
        self.nb_groups = len(groups)
        self.group_colors = [c for c in get_next_qt_color(self.nb_groups)]
        self.frequence = frequence
        self.nb_parts = len(self.values.values()[0])
        
    def columnCount(self, parent):
        return len(self.header)
 
    def rowCount(self, parent): 
        return self.nb_groups  * self.nb_parts
        
    def headerData(self, idx, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return QVariant(self.header[idx])
            else:
                which_group_idx = idx % self.nb_groups
                which_group = self.groups[which_group_idx]
                which_part = idx / self.nb_groups
                
                date = datetime.datetime(*self.dates[which_part])
                
                if which_group_idx == 0:
                    if self.frequence == "day":
                        date = date.strftime('%Y/%m/%d')
                    elif self.frequence == "month":
                        date = date.strftime('%Y %m')
                    else:
                        date = ""
                    return QVariant(date)
                else:
                    return QVariant()
        return QVariant()
        
    def data(self, index, role): 
        which_group_idx = index.row() % self.nb_groups
        which_group = self.groups[which_group_idx]
        which_part = index.row() / self.nb_groups
    
        if not index.isValid(): 
            return QVariant() 
        elif role == Qt.BackgroundRole:
            return self.group_colors[which_group_idx]
        elif role == Qt.TextAlignmentRole:
            return QVariant(Qt.AlignRight)
        elif role != Qt.DisplayRole: 
            return QVariant()
        
        key = self.header[index.column()]
        
        value = self.values[which_group][which_part][key]
        
        return QVariant(("%.1f" % value) if value is not None and int(value) != 0 else "")

class Configuration:
    PROPERTIES = ("math", "legend", "fill", "accu", "invert")
    
    def __init__(self, math=False, legend=False, frequency=False, accu=False, fill=False, invert=False, 
                       startD=None, stopD=None, gtype=None, accounts=None, subcategories=None):
        self.math = math
        self.legend = legend
        self.accu = accu
        self.fill = fill
        self.invert = invert
        
        self.startD = startD
        self.stopD = stopD
        
        self.frequency = frequency
        self.gtype = gtype
        
        self.accounts = accounts
        self.subcategories = subcategories
    
    def __str__(self):
        
        ret = ";".join([opt for opt in Configuration.PROPERTIES if getattr(self, opt)]) + ";"
        
        ret += self.frequency + ";"
        ret += self.gtype + ";"
        
        if self.accounts is not None:
            lst = self.accounts
            prefix = "acc"
        else:
          lst = self.subcategories
          prefix = "cat"
        ret += prefix + "[%s]" % "/".join([str(x) for x in lst]) + ";"
        
        ret += "d1[%s];" % self.startD.strftime('%Y/%m/%d')
        ret += "d2[%s];" % self.stopD.strftime('%Y/%m/%d') 
        
        return "{%s}" % ret
    
    @staticmethod
    def restore_from_string(string, target):
        conf = Configuration()
        
        string = string[1:-1] # {}
        
        for part in string.split(";"):
            print part
            if part in Configuration.PROPERTIES:
                setattr(conf, part, True)
            elif part in ("day", "month", "all"):
                conf.frequency = part
            elif part in ("pie", "line", "3d curves"):
                conf.gtype = part
            elif part[:3] in ("acc", "cat"):
                print part
                lst = part[4:-1].split("/")
                print ">>", lst
                if part[:3] == "acc":
                    conf.accounts = lst
                    conf.subcategories = None
                else:
                    conf.accounts = None
                    conf.subcategories = lst
                    
            elif part.startswith("d1[") or part.startswith("d2["):
                date = datetime.datetime.strptime(part[3:-1], '%Y/%m/%d')
                if part.startswith("d1["):
                    conf.startD = date
                else:
                    conf.stopD = date
        conf.restore(target)
        
    def restore(self, target):
        target.maths_cb.setChecked(self.math)
        target.accu_cb.setChecked(self.accu)
        target.fill_cb.setChecked(self.fill)
        target.invert_cb.setChecked(self.invert)
        target.legend_cb.setChecked(self.legend)
        
        idx = target.cboxGType.findData(QVariant(self.gtype), Qt.UserRole)
        target.cboxGType.setCurrentIndex(idx)
        target.change_GType()
        
        target.set_startD(self.startD.strftime('%Y/%m/%d'))
        target.set_stopD(self.stopD.strftime('%Y/%m/%d'))
        
        target.radioAccount.setChecked(self.accounts is not None)
        target.radioCategory.setChecked(self.subcategories is not None)
        selected = self.subcategories if self.subcategories is not None else self.accounts
        srcList = target.listCat if self.subcategories is not None else target.listAcc
        
        target.change_AccCat()
        
        if self.frequency == "all":
            to_select = target.radioAll
        elif self.frequency == "month":
            to_select = target.radioMonth
        else:
            to_select = target.radioDay
        
        to_select.setChecked(True)
        
        target.listSelected.clear()
        
        for uid in selected:
            for i in  range(srcList.count()):
                item = srcList.item(i)
                data = str(item.data(Qt.UserRole).toPyObject().values()[0])
                
                if data != uid:
                    item = None
                    continue
                item.setSelected(True)
                break
            if item is None:
                print "Couldn't find key '%s'" % uid
                continue
            
            name = item.text()
            
            new_item = QListWidgetItem(name)
            new_item.setData(Qt.UserRole, uid)
            target.listSelected.addItem(new_item)
                
        target.on_draw()
        
def add_item_to_cbox(cbox, name, data):
    cbox.addItem(name, QVariant(data))
    
if __name__ == "__main__":
    main()
