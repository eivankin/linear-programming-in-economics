# from PyQt5 import QtCore, QtGui, QtWidgets
# import pyqtgraph as pg
# import numpy as np
#
# win = pg.GraphicsWindow()
# pg.setConfigOptions(antialias=True)
#
# grad = QtGui.QLinearGradient(0, 0, 0, 3)
# grad.setColorAt(0.1, pg.mkColor('#000000'))
# grad.setColorAt(0.9, pg.mkColor('b'))
# brush = QtGui.QBrush(grad)
#
# p = win.addPlot(y=3 + np.random.normal(size=50), brush=brush, fillLevel=0)
#
#
# import sys
# if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#     QtWidgets.QApplication.instance().exec_()
from PyQt5.QtWidgets import QApplication, QMainWindow
from .views import Ui_SolveViewer
import numpy as np
import sys


class SolveViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.plotter.addItem(y=3 + np.random.normal(size=50), brush=self.plotter.brush, fillLevel=0)
        self.plotter.vb.setLimits(xMin=0, xMax=50, yMin=0, yMax=10)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SolveViewer()
    ex.show()
    sys.exit(app.exec())
