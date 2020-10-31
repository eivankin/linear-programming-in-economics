from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, \
    QTableWidgetItem, QMessageBox, QDialog
from views import Ui_SolveViewer, Ui_TaskViewer, Ui_NewTaskDialog, \
    Ui_NewConstraintDialog, Ui_ExportDialog
import sys
from models import TaskModel, TagModel, CONNECTION
from utility import Solver, NoSolutionError, SolverException, save_csv, compress
from PyQt5.QtGui import QColor
import csv

TASKS = TaskModel()
TAGS = TagModel()


class SolutionViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def show_solution(self, task):
        """:param task: объект модели TaskModel"""
        self.plotter.plotItem.clear()
        self.coefs = task.inequalities_coefs.split(',')
        self.consts = task.inequalities_consts.split(',')
        try:
            solver = Solver(task)
        except AttributeError:
            QMessageBox.warning(self, 'Ошибка!',
                                'Похоже, у задачи заполнены не все данные. '
                                'Проверьте правильность входных данных.')
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
               f'{float(a1):.2g}x<sub>1</sub> + {float(a2):.2g}x<sub>2</sub> {self.mark} {float(const):.2g}</p>'


class NewConstraintDialog(QDialog, Ui_NewConstraintDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.check_form)
        self.coefs = []
        self.const = 0
        self.symbol = ''
        self.lim_type = None

    def get_new_constraint(self):
        ok = super().exec()
        return ok, self.coefs, self.const, self.symbol, self.lim_type

    def check_form(self):
        a1 = self.a1Coef.value()
        a2 = self.a2Coef.value()
        self.lim_type = TaskModel.LIM_INF if self.typeSelector.currentText() == '>=' else TaskModel.LIM_ZERO
        self.const = self.constant.value()
        self.symbol = self.typeSelector.currentText()
        if a1 or a2:
            self.coefs = [a1, a2]
            self.accept()
        else:
            QMessageBox.warning(self, 'Некорректное заполнение формы!', 'Оба коэффициента не могут равняться нулю.')


class NewTaskDialog(QDialog, Ui_NewTaskDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)
        self.constraints = {'coefs': [], 'consts': []}
        self.toolButton.clicked.connect(self.add_constraint)
        self.toolButton_2.clicked.connect(self.remove_constraint)

        self.pushButton.clicked.connect(self.check_form)
        self.result = []

    def get_new_task(self, mode='obj'):
        """:param mode: принимает два значения:
            'obj': метод возвращает объект модели;
            'row': метод возвращает список значений атрибутов объекта."""
        ok = super().exec()
        if mode == 'obj':
            return ok, TASKS.row_to_obj(self.result)
        elif mode == 'row':
            return ok, self.result

    def add_constraint(self):
        cd = NewConstraintDialog(self)
        ok, coefs, const, symbol, lim_type = cd.get_new_constraint()
        if ok:
            self.constraints['coefs'].extend([x * lim_type for x in coefs])
            self.constraints['consts'].append(const * lim_type)
            self.constraintsList.addItem(f'{coefs[0]:.2g}*x1+{coefs[1]:.2g}*x2 {symbol} {const:.2g}')

    def remove_constraint(self):
        selected = [x.row() for x in self.constraintsList.selectedIndexes()]
        if selected:
            for i in selected:
                self.constraintsList.takeItem(i)
                self.constraints['consts'].pop(i)
                self.constraints['coefs'].pop(i * 2)
                self.constraints['coefs'].pop(i * 2)
        else:
            QMessageBox.warning(self, 'Ошибка!', 'Не выбраны линейные ограничения для удаления!')

    def check_form(self):
        ps = self.problemSituation.toPlainText()
        dd = TaskModel.VERBOSE_VALS['target_func_lim']
        tf_opt_val = list(dd.keys())[list(dd.values()).index(self.optimalValue.currentText())]
        tf_coefs = self.a1Coef.value(), self.a2Coef.value()
        c_coefs = self.constraints['coefs']
        c_consts = self.constraints['consts']
        axis_coefs = [1, 0, 0, 1]
        axis_consts = [self.x1Gte.value() * tf_opt_val, self.x2Gte.value() * tf_opt_val]
        if tf_coefs[0] or tf_coefs[1]:
            self.result = [ps, tf_opt_val, compress(tf_coefs), compress(c_coefs),
                           compress(c_consts), compress(axis_coefs), compress(axis_consts)]
            self.accept()
        else:
            QMessageBox.warning(self, 'Ошибка!', 'Оба коэффициента ЦФ не могут быть нулевыми!')


class ExportDialog(QDialog, Ui_ExportDialog):  # TODO
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

    def get_export_options(self):
        ok = super().exec()
        return ok, '', {}


class TaskViewer(QMainWindow, Ui_TaskViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.loadDBAction.triggered.connect(self.load_db)
        self.loadFileAction.triggered.connect(self.load_csv)
        self.addNewTaskAction.triggered.connect(self.append_task)
        self.solveNewTaskAcion.triggered.connect(self.solve_new_task)

        self.searchLine.textChanged.connect(self.search)

        self.saveButton.clicked.connect(self.save_changes)
        self.solveButton.clicked.connect(self.solve_selected)
        self.deleteButton.clicked.connect(self.delete_selected)
        self.exportButton.clicked.connect(self.export)
        self.load_db()
        self.solution_viewer = SolutionViewer()
        self.current_file = None

    def load_db(self):
        self.current_file = None
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

    def load_csv(self, file_name=None):
        ok = True
        if not file_name:
            file_name, ok = QFileDialog.getOpenFileName(self, 'Выберите таблицу', '',
                                                        'CSV-таблица с разделителем ";" (*.csv)')
        if ok:
            with open(file_name, encoding='utf8') as csv_file:
                table = csv.reader(csv_file, delimiter=';', quotechar='"')
                title = next(table)
                if title == TASKS.ATTRS[1:]:
                    self.current_file = file_name
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
        selected = sorted(set([i.row() for i in self.tableWidget.selectedItems()]))
        ids = [self.tableWidget.item(i, 0).text() for i in selected]
        if selected:
            ok = QMessageBox.question(
                self, 'Удаление элементов',
                (f'Вы точно хотите удалить выбранные элементы с ИД {", ".join(ids)}? '
                 'Они будут безвозвратно удалены из базы данных' if not self.current_file else
                 'Выбранные задачи будут просто скрыты из таблицы. '
                 'Для их удаления необходимо будет перезаписать файл через опцию "Сохранить".'),
                QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                for i, row in enumerate(selected):
                    self.tableWidget.removeRow(row)
                    if not self.current_file:
                        obj = TASKS.get(id=ids[i])
                        if obj._saved:
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

    def append_task(self):
        td = NewTaskDialog(self)
        ok, task = td.get_new_task('row' if self.current_file else 'obj')
        if ok:
            if self.current_file:
                i = self.tableWidget.rowCount()
                self.tableWidget.setRowCount(i + 1)
                for j, elem in enumerate(task):
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
                self.statusbar.showMessage('Задача добавлена в таблицу, для сохранения файла с ней нажмите конпку '
                                           '"Сохранить изменения"', msecs=5000)
            else:
                task.save()
                self.load_db()
                self.statusbar.showMessage('Задача успешно добавлена в базу данных', msecs=5000)

    def solve_new_task(self):
        td = NewTaskDialog(self)
        ok, task = td.get_new_task()
        if ok:
            self.solution_viewer.show_solution(task)

    def search(self, text):  # TODO
        pass

    def export(self):  # TODO
        ed = ExportDialog(self)
        ok, file_name, options = ed.get_export_options()
        if ok:
            table = []
            save_csv(file_name, table, options['delimiter'])

    def save_changes(self):  # TODO
        if not self.current_file:
            pass  # saving db objects with update method
        else:
            table = []
            save_csv(self.current_file, table, ';')

    def closeEvent(self, event):
        CONNECTION.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tv = TaskViewer()
    tv.show()
    sys.exit(app.exec())
