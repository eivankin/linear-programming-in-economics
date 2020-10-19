from PyQt5.QtWidgets import QApplication, QMainWindow
from views import Ui_SolveViewer
from utility import TeXRenderer
import numpy as np
import sys

TeX = TeXRenderer()


class SolveViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.mathModel.setPixmap(TeX.draw_formula(r'$x \geq 0;y\geq 0;$'))

        self.plotter.plot(y=3 + np.random.normal(size=50), brush=self.plotter.brush, fillLevel=0)
        self.plotter.plotItem.vb.setLimits(xMin=-1, xMax=51, yMin=-1, yMax=6)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SolveViewer()
    ex.show()
    sys.exit(app.exec())
