from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidgetItem,
                             QMessageBox)
from views import Ui_SolveViewer, Ui_TaskViewer
import sys
from models import TaskModel, TagModel, CONNECTION
from utility import Solver, NoSolutionError, SolverException
from PyQt5.QtGui import QColor

DEBUG = True
TASKS = TaskModel()
TAGS = TagModel()


class SolutionViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self, task):
        """:param task: объект модели TaskModel"""
        super().__init__()
        self.setupUi(self)
        self.coefs = task.inequalities_coefs.split(',')
        self.consts = task.inequalities_consts.split(',')
        solver = Solver(task)
        self.mark = '&ge;' if solver.lim == TaskModel.LIM_ZERO else '&le;'
        for i, constraint in enumerate(solver.get_constraints()[:, :, ::-1]):
            self.plotter.plot(x=constraint[:, ::2].ravel(),
                              y=constraint[:, 1::2].ravel(),
                              name=self.render_constraint(i),
                              pen=self.plotter.pen())
        bounds = solver.get_bounds(5, 0)
        self.plotter.plotItem.vb.setLimits(**bounds)
        try:
            point, opt_value = solver.solve()
            if DEBUG:
                print(point, opt_value)
        except NoSolutionError:
            QMessageBox.warning(self, 'Ошибка!',
                                'Похоже, у задачи нет решения. Проверьте правильность входных данных.')
            self.close()
        except SolverException as e:
            QMessageBox.warning(self, 'Ошибка!',
                                f'К сожалению, задачу решить не удалось.\nПричина: {e}')
            self.close()
        except Exception as e:
            QMessageBox.warning(self, 'Непредвиденная ошибка!',
                                f'В ходе решения произошла непредвиденная ошибка {e}')
            self.close()
        if solver.lim == TaskModel.LIM_INF:
            p_points = solver.get_possible_points()
            if DEBUG:
                print(p_points)
            self.plotter.plot(
                x=tuple(p_points.keys()), y=tuple(p_points.values()),
                brush=QColor(0, 0, 255, 90), pen=None,
                fillLevel=bounds['xMin'] if solver.lim == TaskModel.LIM_INF else bounds['xMax']
            )
        self.plotter.plot(
            x=[0, opt_value / solver.coefs[0] * solver.lim], y=[opt_value / solver.coefs[1] * solver.lim, 0],
            pen=self.plotter.pen('r'), name='<p style="font-size: 12pt; font-family:Georgia, \'Times New Roman\', '
                                            'Times, serif">Целевая функция</p>')
        self.plotter.plot(
            x=[point[0]], y=[point[1]], symbol='+', symbolSize=20,
            symbolBrush='b', symbolPen=None, pen=None,
            name='<p style="font-size: 12pt; font-family:Georgia, \'Times New Roman\', '
                 'Times, serif">Оптимальное значение ЦФ</p>'
        )
        self.menu.triggered.connect(self.save_image)

    def render_constraint(self, number):
        """:param number: порядковый номер ограничения, начиная с 0."""
        a1, a2 = self.coefs[number * 2:number * 2 + 2]
        const = self.consts[number]
        return f'<p style="font-size: 12pt; font-family:Georgia, \'Times New Roman\', Times, serif">' \
               f'{a1}x<sub>1</sub> + {a2}x<sub>2</sub> {self.mark} {const}</p>'

    def save_image(self):
        file_name, ok = QFileDialog.getSaveFileName(self, 'Сохранить отчёт',
                                                    'Решение.png', 'Images (*.png *.jpg *.tiff)')
        if ok:
            self.plotter.save(file_name)


class TaskViewer(QMainWindow, Ui_TaskViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.action.triggered.connect(self.load_db)
        self.action_2.triggered.connect(self.load_csv)

        self.lineEdit.textChanged.connect(self.search)

        self.pushButton_2.clicked.connect(self.solve_selected)
        self.pushButton_3.clicked.connect(self.delete_selected)
        self.pushButton_4.clicked.connect(self.appendTask)
        self.db = True
        self.load_db()

    def load_db(self):
        self.db = True
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(TASKS.ATTRS))
        self.comboBox.addItems(TASKS.get_title())
        self.tableWidget.setHorizontalHeaderLabels(TASKS.get_title())
        self.tableWidget.resizeColumnsToContents()
        for i, obj in enumerate(TASKS.all()):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, attr in enumerate(TASKS.ATTRS):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(TASKS.VERBOSE_VALS[attr].get(
                        obj.__dict__[attr], str(obj.__dict__[attr]))))
        self.statusbar.showMessage('База примеров упспешно загружена', msecs=5000)

    def load_csv(self):  # TODO
        self.db = False
        self.tableWidget.setRowCount(0)

    def delete_selected(self):
        selected = self.tableWidget.selectedIndexes()  # TODO: indexes to ids
        if selected:
            ok = QMessageBox.question(
                self, '', 'Вы действительно хотите удалить выбранные элементы?',
                QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                for index in selected:
                    self.tableWidget.removeRow(index)
                    if self.db:
                        obj = TASKS.get(id=index)
                        if obj:
                            obj.delete()
        else:
            self.statusbar.showMessage('Ничего не выбрано!', msecs=5000)

    def solve_selected(self):  # TODO
        selected = self.tableWidget.selectedIndexes()
        if selected:
            solution_viewer = SolutionViewer(TASKS.row_to_obj(selected[0]))
            solution_viewer.show()
        else:
            self.statusbar.showMessage('Ничего не выбрано!', msecs=5000)

    def append_task(self):  # TODO
        pass

    def search(self, text):  # TODO
        pass

    def __get_obj(self, selected):  # TODO
        pass

    def closeEvent(self, event):
        CONNECTION.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # tv = TaskViewer()
    # tv.show()
    task = TASKS.get(id=2)
    sv = SolutionViewer(task)
    sv.show()
    sys.exit(app.exec())
