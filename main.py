from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QFileDialog, QTableWidgetItem,
                             QMessageBox)
from views import Ui_SolveViewer, Ui_TaskViewer
import numpy as np
import sys
from models import SettingsModel, TaskModel, CONNECTION
from utility import TargetFunction


class SolveViewer(QMainWindow, Ui_SolveViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.plotter.plot(
            y=3 + np.random.normal(size=50), brush=self.plotter.brush, fillLevel=0,
            name='<p style="font-size: 12pt; font-family:Georgia, \'Times New Roman\', Times, serif">x &ge; y</p>'
        )
        self.plotter.plotItem.vb.setLimits(xMin=-1, xMax=51, yMin=-1, yMax=10)
        self.action_4.triggered.connect(self.saveImage)

    def saveImage(self):
        file_name, ok = QFileDialog.getSaveFileName(self, 'Сохранить отчёт',
                                                    'Решение.png', 'Images (*.png *.jpg *.tiff)')
        if ok:
            self.plotter.save(file_name)


class TaskViewer(QMainWindow, Ui_TaskViewer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tasks = TaskModel()

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
        self.tableWidget.setColumnCount(len(self.tasks.ATTRS))
        self.comboBox.addItems(self.tasks.get_title())
        self.tableWidget.setHorizontalHeaderLabels(self.tasks.get_title())
        self.tableWidget.resizeColumnsToContents()
        for i, obj in enumerate(self.tasks.all()):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, attr in enumerate(self.tasks.ATTRS):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(obj.__dict__[attr])))
        self.statusbar.showMessage('База примеров упспешно загружена', msecs=5000)

    def loadCSV(self):  # TODO
        self.db = False
        self.tableWidget.setRowCount(0)

    def deleteSelected(self):
        selected = self.tableWidget.selectedIndexes()
        if selected:
            ok = QMessageBox.question(
                self, '', 'Вы действительно хотите удалить выбранные элементы?',
                QMessageBox.Yes, QMessageBox.No)
            if ok == QMessageBox.Yes:
                for index in selected:
                    self.tableWidget.removeRow(index)
                    if self.db:
                        obj = self.tasks.get(id=index)
                        if obj:
                            obj.delete()
        else:
            self.statusbar.showMessage('Ничего не выбрано!', msecs=5000)

    def solveSelected(self):  # TODO
        selected = self.tableWidget.selectedIndexes()
        if selected:
            pass
        else:
            self.statusbar.showMessage('Ничего не выбрано!', msecs=5000)

    def appendTask(self):  # TODO
        pass

    def search(self, text):  # TODO
        pass

    def closeEvent(self, event):
        CONNECTION.close()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    tv = TaskViewer()
    tv.show()
    sys.exit(app.exec())
