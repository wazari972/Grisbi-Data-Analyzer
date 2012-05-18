import sys, os, random
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.figure import Figure


from GuiGrisbi import GrisbiDataProvider

class AppForm(QMainWindow):
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        self.setWindowTitle('Grisbi Data Plotter')
        
        self.src = GrisbiDataProvider()

        self.create_menu()
        self.create_main_frame()
        self.create_status_bar()
        
        self.on_draw()
        try:
            toto = self.startD
            toto = self.stopD
        except:
            print "init ##############"
            self.startD = None
            self.stopD = None
        
        
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
    
    def on_pick(self, event):
        box_points = event.artist.get_bbox().get_points()
        msg = "You've clicked on a bar with coords:\n %s" % box_points
        
        QMessageBox.information(self, "Click!", msg)
    
    def set_startD(self, minus_one=False):
        date = self.cal.selectedDate()
        
        if minus_one:
            date = date.addYears(-1)
        
        self.startD_lbl.setText(date.toString())
        self.startD = (date.year(), date.month(), date.day())
        
    def set_stopD(self):     
        date = self.cal.selectedDate()
        self.stopD_lbl.setText(date.toString())
        self.stopD = (date.year(), date.month(), date.day())
    
    def change_AccCat(self):
        self.listAcc.setDisabled(not self.radioAccount.isChecked())
        self.listCat.setDisabled(self.radioAccount.isChecked())
    def on_draw(self):
        """ Redraws the figure
        """

        # clear the axes and redraw the plot anew
        #
        self.axes.clear()        
        inverted = self.invert_cb.isChecked()
        monthly = self.month_cb.isChecked()
        
        accounts = None
        subcategories = None
        if self.radioAccount.isChecked():
            accounts = [str(item.data(Qt.UserRole).toPyObject()) for item in self.listAcc.selectedItems()]
        else:
            subcategories = [str(item.data(Qt.UserRole).toPyObject()) for item in self.listCat.selectedItems()]
        
        data = self.src.get_data(inverted, monthly, self.startD, self.stopD, subcategories=subcategories, accounts=accounts)
        x = range(len(data))
        self.axes.bar(
            left=x, 
            height=data, 
            width=1, 
            align='center', 
            alpha=0.44,
            picker=5)
        
        self.canvas.draw()
    
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
        
        # Bind the 'pick' event for clicking on one of the bars
        #
        self.canvas.mpl_connect('pick_event', self.on_pick)
        
        # Create the navigation toolbar, tied to the canvas
        #
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)
        
        # Other GUI controls
        #         
        self.draw_button = QPushButton("&Draw")
        self.connect(self.draw_button, SIGNAL('clicked()'), self.on_draw)
        
        self.invert_cb = QCheckBox("Inverted ?")
        self.invert_cb.setChecked(False)
        self.connect(self.invert_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.month_cb = QCheckBox("Monthly ?")
        self.month_cb.setChecked(False)
        self.connect(self.month_cb, SIGNAL('stateChanged(int)'), self.on_draw)
        
        self.cal = QCalendarWidget(self)
        self.cal.setGridVisible(True)
        self.cal.move(20, 20)
        
        self.startD_button = QPushButton("&Start date")
        self.connect(self.startD_button, SIGNAL('clicked()'), self.set_startD)
        self.startD_lbl = QLabel(self)
        self.set_startD(minus_one=True)
        
        self.startD_lbl.move(130, 260)
        
        self.stopD_button = QPushButton("&Stop date")
        self.connect(self.stopD_button, SIGNAL('clicked()'), self.set_stopD)
        self.stopD_lbl = QLabel(self)
        
        self.set_stopD()
        self.stopD_lbl.move(130, 260)
        
        self.listCat = QListWidget()
        self.listCat.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        
        for cat, name in self.src.get_categories().items():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, cat) 
            self.listCat.addItem(item)
            
        self.listAcc = QListWidget()
        self.listAcc.setSelectionMode(QAbstractItemView.ExtendedSelection) 
        self.listAcc.setDisabled(True)
        
        for acc, name in self.src.get_accounts().items():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, acc) 
            self.listAcc.addItem(item)
            
        self.radioCategory = QRadioButton("Categories")
        self.radioCategory.setChecked(True)
        self.connect(self.radioCategory, SIGNAL('clicked()'), self.change_AccCat)
        self.radioAccount = QRadioButton("Accounts")
        self.connect(self.radioAccount, SIGNAL('clicked()'), self.change_AccCat)
        
        #
        # Layout with box sizers
        # 
        
        def add_box(elements):
            box = QHBoxLayout()
            for w in elements:
                box.addWidget(w)
                box.setAlignment(w, Qt.AlignVCenter)
            vbox.addLayout(box)
            return box
            
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addWidget(self.mpl_toolbar)
        
        add_box([self.month_cb, self.invert_cb])
        add_box([self.startD_lbl, self.startD_button, self.cal,  self.stopD_button, self.stopD_lbl])
        add_box([self.radioCategory, self.radioAccount])
        add_box([self.listCat, self.listAcc])
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


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()


if __name__ == "__main__":
    main()

