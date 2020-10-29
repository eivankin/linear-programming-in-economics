from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidgetItem,
                             QMessageBox)
from views import Ui_SolveViewer, Ui_TaskViewer
import sys
from models import TaskModel, TagModel, CONNECTION
from utility import Solver, NoSolutionError, SolverException
from PyQt5.QtGui import QColor
import csv

TASKS = TaskModel()
TAGS = TagModel()


class SolutionViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.saveReportAction.triggered.connect(self.save_image)

    def show_solution(self, task):
        """:param task: объект модели TaskModel"""
        self.plotter.plotItem.clear()
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
        except NoSolutionError:
            QMessageBox.warning(self, 'Ошибка!',
                                'Похоже, у задачи нет решения. Проверьте правильность входных данных.')
            return
        except SolverException as e:
            QMessageBox.warning(self, 'Ошибка!',
                                f'К сожалению, задачу решить не удалось.\nПричина: {e}')
            return
        except Exception as e:
            QMessageBox.warning(self, 'Непредвиденная ошибка!',
                                f'В ходе решения произошла непредвиденная ошибка {e}')
            return
        if solver.lim == TaskModel.LIM_INF:
            p_points = solver.get_possible_points()
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
        super().show()

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

        self.loadDBAction.triggered.connect(self.load_db)
        self.loadFileAction.triggered.connect(self.load_csv)
        self.addNewTaskAction.triggered.connect(self.append_task)
        self.solveNewTaskAcion.triggered.connect(self.solve_new_task)

        self.searchLine.textChanged.connect(self.search)

        self.solveButton.clicked.connect(self.solve_selected)
        self.deleteButton.clicked.connect(self.delete_selected)
        self.exportButton.clicked.connect(self.export)
        self.load_db()
        self.solution_viewer = SolutionViewer()

    def load_db(self):
        self.db = True
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(TASKS.ATTRS))
        self.comboBox.addItems(TASKS.get_title())
        self.tableWidget.setHorizontalHeaderLabels(TASKS.get_title())
        self.tableWidget.resizeColumnsToContents()
        for i, obj in enumerate(TASKS.all()):
            self.tableWidget.setRowCount(i + 1)
            for j, attr in enumerate(TASKS.ATTRS):
                self.tableWidget.setItem(
                    i, j, QTableWidgetItem(TASKS.VERBOSE_VALS[attr].get(
                        obj.__dict__[attr], str(obj.__dict__[attr]))))
        self.statusbar.showMessage('База примеров упспешно загружена', msecs=5000)

    def load_csv(self):
        file_name, ok = QFileDialog.getOpenFileName(self, 'Выберите таблицу', '', 'CSV-таблица (*.csv)')
        if ok:
            with open(file_name, encoding='utf8') as csv_file:
                table = csv.reader(csv_file, delimiter=';', quotechar='"')
                title = next(table)
                if title == TASKS.ATTRS[1:]:
                    self.db = False
                    self.tableWidget.setRowCount(0)
                    for i, row in enumerate(table, start=1):
                        self.tableWidget.setRowCount(i)
                        for j, val in enumerate([i] + row):
                            current = TASKS.VERBOSE_VALS[TASKS.ATTRS[j]]
                            self.tableWidget.setItem(i - 1, j, QTableWidgetItem(
                                current.get(type(list(current)[0] if current else '')(val), str(val))
                            ))
                else:
                    self.statusbar.showMessage('Некорректная структура таблицы', msecs=5000)
            self.statusbar.showMessage('Задачи из файла успешно загржены', msecs=5000)

    def delete_selected(self):
        selected = [i.row() for i in self.tableWidget.selectedItems()]
        if selected:
            ok = QMessageBox.question(
                self, 'Удаление элементов',
                (f'Вы точно хотите удалить выбранные элементы в строках {", ".join(selected)}? '
                 'Они будут безвозвратно удалены из базы данных' if self.db else
                 'Выбранные задачи будут просто скрыты из таблицы. '
                 'Для их удаления необходимо будет перезаписать файл через опцию "Сохранить".'),
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

    def solve_selected(self):
        selected = [[self.tableWidget.item(i.row(), j).text() for j in range(len(TASKS.ATTRS))]
                    for i in self.tableWidget.selectedItems()]
        if selected:
            self.solution_viewer.show_solution(TASKS.row_to_obj(selected[0]))
        else:
            self.statusbar.showMessage('Ничего не выбрано!', msecs=5000)

    def append_task(self):  # TODO
        pass

    def solve_new_task(self):  # TODO
        pass

    def search(self, text):  # TODO
        pass

    def export(self):  # TODO
        pass

    def closeEvent(self, event):
        CONNECTION.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tv = TaskViewer()
    tv.show()
    sys.exit(app.exec())
