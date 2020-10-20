from PyQt5 import QtGui
import pyqtgraph as pg
import pyqtgraph.exporters


class Plotter(pg.PlotWidget):
    def __init__(self, *args, **kwargs):
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        super().__init__(*args, **kwargs)
        grad = QtGui.QLinearGradient(0, 0, 0, 3)
        grad.setColorAt(0.1, pg.mkColor('w'))
        grad.setColorAt(0.9, pg.mkColor('g'))
        self.brush = QtGui.QBrush(grad)
        self.addLegend(offset=(-1, 1), pen=QtGui.QColor('grey'))

    def save(self, file_name):
        exporter = pg.exporters.ImageExporter(self.plotItem)
        exporter.export(file_name)


class TargetFunction:
    def __init__(self, a1, a2):
        self.a1 = a1
        self.a2 = a2

    def __call__(self, x1, x2):
        return self.a1 * x1 + self.a2 * x2
