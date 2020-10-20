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
