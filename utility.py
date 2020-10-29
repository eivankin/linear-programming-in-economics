from PyQt5 import QtGui
import pyqtgraph as pg
import pyqtgraph.exporters
from scipy.optimize import linprog
import numpy as np
from random import randint
from collections import OrderedDict
from models import TaskModel


class SolverException(Exception):
    pass


class NoSolutionError(SolverException):
    pass


class Plotter(pg.PlotWidget):
    """Виджет для отрисовки решения"""

    def __init__(self, *args, **kwargs):
        pg.setConfigOptions(antialias=True)
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        super().__init__(*args, **kwargs)
        grad = QtGui.QLinearGradient(0, 0, 0, 3)
        grad.setColorAt(0.1, pg.mkColor('w'))
        grad.setColorAt(0.9, pg.mkColor('b'))
        self.plotItem.showGrid(x=True, y=True)
        self.gradient = QtGui.QBrush(grad)
        self.addLegend(offset=(-1, 1), pen=QtGui.QColor('grey'), brush='w')

    def save(self, file_name):
        exporter = pg.exporters.ImageExporter(self.plotItem)
        exporter.export(file_name)

    def pen(self, color=None, width=3):
        if not color:
            return pg.mkPen(randint(0, 255), randint(0, 255), randint(0, 255), width=2)
        return pg.mkPen(color, width=width)


class Solver:
    """Класс для решения задачи линейного программирования и получения значений для построения.
    :param task: объект модели TaskModel."""

    def __init__(self, task):
        if type(task.target_func_lim) == str:
            dd = TaskModel.VERBOSE_VALS['target_func_lim']
            self.lim = list(dd.keys())[list(dd.values()).index(task.target_func_lim)]
        else:
            self.lim = task.target_func_lim
        self.coefs = np.fromstring(task.target_func_coefs, sep=',') * self.lim
        self.inequalities_coefs = np.fromstring(
            task.inequalities_coefs, sep=',').reshape(-1, 2) * -self.lim
        self.inequalities_consts = np.fromstring(task.inequalities_consts, sep=',') * -self.lim
        self.axis_coefs = np.fromstring(task.axis_coefs, sep=',').reshape(-1, 2) * -1
        self.axis_consts = np.fromstring(task.axis_consts, sep=',')
        self.points = (self.inequalities_consts / self.inequalities_coefs[:, ::-1].T).T
        self.possible_points = {}

    def get_bounds(self, margin_top, margin_bottom):
        """:param margin_top: отступ сверху.
        :param margin_bottom: отступ снизу.
        :returns dictionary('xMin', 'xMax', 'yMin', 'yMax'): координаты прямоугольника, ограничивающего поле зрения."""
        return {'xMin': self.axis_consts[0] - margin_bottom,
                'xMax': np.max(self.points[:, ::2]) + margin_top,
                'yMin': self.axis_consts[1] - margin_bottom,
                'yMax': np.max(self.points[:, 1::2]) + margin_top}

    def get_constraints(self):
        """:returns [[[x1_1, y2_2], [x1_2, y1_2]], ...]: список пар точек для построения линейных ограничений."""
        c = self.points.copy()[:, :, np.newaxis]
        p = np.zeros(c.shape[:2] + (2,))
        p[:, ::2] = np.append(c[:, ::2], np.zeros(c[:, ::2].shape), 2)
        p[:, 1::2] = np.append(np.zeros(c[:, 1::2].shape), c[:, 1::2], 2)
        return p

    def solve(self):
        """:returns [x1, x2], L(x1, x2): точка оптимального решения и значение целевой функции в ней."""
        result = linprog(
            self.coefs, np.append(self.inequalities_coefs, self.axis_coefs, 0),
            np.append(self.inequalities_consts, self.axis_consts), method='revised simplex',
            callback=self.__logging)

        if result.status != 0:
            if result.status == 2:
                raise NoSolutionError
            raise SolverException(result.message)

        linprog(
            self.coefs, np.append(self.inequalities_coefs, self.axis_coefs, 0),
            np.append(self.inequalities_consts, self.axis_consts), method='revised simplex',
            callback=self.__logging, options={'pivot': 'bland'})
        return result.x, result.fun * self.lim

    def __logging(self, res):
        self.possible_points[res.x[0]] = max(self.possible_points.get(res.x[0], res.x[1] - 1), res.x[1])

    def get_possible_points(self):
        """WARNING: works strange if self.lim == Task.Model.LIM_ZERO, use it only if self.lim == TaskModel.LIM_INF
        :returns possible_points: границы области допустимых решений."""
        return OrderedDict(sorted(self.possible_points.items()))
