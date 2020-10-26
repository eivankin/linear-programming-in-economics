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
        self.axis_coefs = np.fromstring(task.axis_coefs, sep=',').reshape(2, -1) * -self.lim
        self.axis_consts = np.fromstring(task.axis_consts, sep=',') * -self.lim
        self.points = ((self.inequalities_consts - self.inequalities_coefs * self.axis_consts)
                       / self.inequalities_coefs[:, ::-1].T).T
        self.possible_points = {}

    def get_bounds(self, margin_top, margin_bottom):
        """:param margin_top: отступ сверху.
        :param margin_bottom: отступ снизу.
        :returns [xMin, xMax, yMin, yMax]: координаты прямоугольника, ограничивающего поле зрения."""
        return self.axis_consts[0] - margin_bottom, np.max(self.points[:, ::2]) + margin_top, \
            self.axis_consts[1] - margin_bottom, np.max(self.points[:, 1::2]) + margin_top

    def get_constraints(self):
        """:returns [[[x1_1, y2_2], [x1_2, y1_2]], ...]: список пар точек для построения линейных ограничений."""
        c = self.points.copy()[:, :, np.newaxis]
        p = np.zeros(c.shape[:2] + (2,))
        p[:, ::2] = np.append(c[:, ::2], np.full(c[:, ::2].shape, self.axis_consts[1]), 2)
        p[:, 1::2] = np.append(np.full(c[:, 1::2].shape, self.axis_consts[0]), c[:, 1::2], 2)
        return p

    def solve(self):
        """:returns [x1, x2], L(x1, x2): точка оптимального решения и значение целевой функции в ней."""
        result = linprog(self.coefs, np.append(self.inequalities_coefs, self.axis_coefs, 0),
                         np.append(self.inequalities_consts, self.axis_consts),
                         method='revised simplex', callback=self.__logging)
        return result.x, result.fun * self.lim

    def __logging(self, res):
        self.possible_points[res.x[0]] = max(self.possible_points.get(res.x[0], res.x[1] - 1), res.x[1])

    def get_possible_points(self):
        """:returns possible_points: границы области допустимых решений."""
        return self.possible_points
