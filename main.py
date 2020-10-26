from PyQt5.QtWidgets import (QApplication, QMainWindow, QFileDialog, QTableWidgetItem,
                             QMessageBox)
from views import Ui_SolveViewer, Ui_TaskViewer
import sys
from models import TaskModel, CONNECTION
from utility import Solver
from PyQt5.QtGui import QColor


TASKS = TaskModel()


class SolutionViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self, task):
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
                              pen=self.plotter.random_pen())
        self.plotter.plotItem.vb.setLimits(**solver.get_bounds(5, 0))
        point, value = solver.solve()
        print(point, value)
        p_points = solver.get_possible_points()
        print(p_points)
        self.plotter.plot(x=tuple(p_points.keys()), y=tuple(p_points.values()),
                          brush=QColor(0, 0, 255, 90), fillLevel=0, pen=None)
        self.action_4.triggered.connect(self.save_image)

    def render_constraint(self, number):
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

        self.action.triggered.connect(self.loadDB)
        self.action_2.triggered.connect(self.loadCSV)

        self.lineEdit.textChanged.connect(self.search)

        self.pushButton_2.clicked.connect(self.solveSelected)
        self.pushButton_3.clicked.connect(self.deleteSelected)
        self.pushButton_4.clicked.connect(self.appendTask)
        self.db = True
        self.loadDB()

    def loadDB(self):
        self.db = True
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(len(TASKS.ATTRS))
        self.comboBox.addItems(TASKS.get_title())
        self.tableWidget.setHorizontalHeaderLabels(TASKS.get_title())
        self.tableWidget.resizeColumnsToContents()
        for i, obj in enumerate(TASKS.all()):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, attr in enumerate(TASKS.ATTRS):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(obj.__dict__[attr])))
        self.statusbar.showMessage('База примеров упспешно загружена', msecs=5000)

    def loadCSV(self):  # TODO
        self.db = False
        self.tableWidget.setRowCount(0)

    def deleteSelected(self):
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

    def solveSelected(self):  # TODO
        selected = self.tableWidget.selectedIndexes()
        if selected:
            solution_viewer = SolutionViewer(self.__get_obj(selected[0]))
            solution_viewer.show()
        else:
            self.statusbar.showMessage('Ничего не выбрано!', msecs=5000)

    def appendTask(self):  # TODO
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
    task = TASKS.get(id=1)
    sv = SolutionViewer(task)
    sv.show()
    sys.exit(app.exec())
