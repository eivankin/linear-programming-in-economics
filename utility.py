from PyQt5 import QtGui
import pyqtgraph as pg
import pyqtgraph.exporters
from scipy.optimize import linprog
import numpy as np


class Plotter(pg.PlotWidget):
    """Виджет для отрисовки решения"""
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


class Solver:
    """Класс для решения задачи линейного программирования и получения значений для построения.
    :param task: объект модели TaskModel."""
    def __init__(self, task):
        self.lim = task.target_func_lim
        self.coefs = np.fromstring(task.target_func_coefs, sep=',') * self.lim
        self.inequalities_coefs = np.fromstring(
            task.inequalities_coefs, sep=',').reshape(2, -1) * -self.lim
        self.inequalities_consts = np.fromstring(task.inequalities_consts, sep=',') * -self.lim
        self.points = (self.inequalities_consts / self.inequalities_coefs[:, ::-1].T).T

    def get_bounds(self, margin_top, margin_bottom):
        """:param margin_top: отступ сверху.
        :param margin_bottom: отступ снизу.
        :return [xMin, xMax, yMin, yMax]: координаты прямоугольника, ограничивающего поле зрения."""
        return np.min(self.points[:, ::2]) - margin_bottom, np.max(self.points[:, ::2]) + margin_top, \
            np.min(self.points[:, 1::2]) - margin_bottom, np.max(self.points[:, 1::2]) + margin_top

    def get_constraints(self):
        """:return [[[x1_1, y2_2], [x1_2, y1_2]], ...]: список пар точек для построения линейных ограничений."""
        return self.points

    def solve(self):
        """:returns [x1, x2], L(x1, x2): точка оптимального решения и значение целевой функции в ней."""
        result = linprog(self.coefs, self.inequalities_coefs,
                         self.inequalities_consts)
        return result.x, result.fun * self.lim
