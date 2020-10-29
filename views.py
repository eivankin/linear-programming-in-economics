from PyQt5 import QtCore, QtGui, QtWidgets
from utility import Plotter


"""В этом файле хранятся классы интерфейсов, созданных в QtDesigner"""
# TODO: export dialog, new task dialog


class Ui_SolveViewer:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.plotter = Plotter(MainWindow)
        self.plotter.setObjectName("plot")
        MainWindow.setCentralWidget(self.plotter)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 783, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.saveMenu = QtWidgets.QMenu(self.menubar)
        self.saveMenu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.saveReportAction = QtWidgets.QAction(MainWindow)
        self.saveReportAction.setObjectName("action")
        self.saveMenu.addAction(self.saveReportAction)
        self.menubar.addAction(self.saveMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Решение задачи"))
        self.saveMenu.setTitle(_translate("MainWindow", "Экспорт"))
        self.saveReportAction.setText(_translate("MainWindow", "Сохранить отчёт в виде изображения"))


class Ui_TaskViewer:
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(600, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.searchLine = QtWidgets.QLineEdit(self.centralwidget)
        self.searchLine.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.searchLine)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.horizontalLayout.addWidget(self.comboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setObjectName("horizontalLayout_2")
        self.deleteButton = QtWidgets.QPushButton(self.centralwidget)
        self.deleteButton.setObjectName("pushButton_2")
        self.solveButton = QtWidgets.QPushButton(self.centralwidget)
        self.solveButton.setObjectName("pushButton_2")
        self.exportButton = QtWidgets.QPushButton(self.centralwidget)
        self.exportButton.setObjectName("pushButton_3")
        self.buttonLayout.addWidget(self.solveButton)
        self.buttonLayout.addWidget(self.deleteButton)
        self.buttonLayout.addWidget(self.exportButton)
        self.verticalLayout.addLayout(self.buttonLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 509, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.menubar.setFont(font)
        self.menubar.setObjectName("menubar")
        self.loadMenu = QtWidgets.QMenu(self.menubar)
        self.loadMenu.setObjectName("menu")
        self.newTaskMenu = QtWidgets.QMenu(self.menubar)
        self.newTaskMenu.setObjectName("menu_2")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.loadDBAction = QtWidgets.QAction(MainWindow)
        self.loadDBAction.setObjectName("load_db_action")
        self.loadFileAction = QtWidgets.QAction(MainWindow)
        self.loadFileAction.setObjectName("action_2")
        self.loadMenu.addAction(self.loadDBAction)
        self.loadMenu.addAction(self.loadFileAction)
        self.addNewTaskAction = QtWidgets.QAction(MainWindow)
        self.addNewTaskAction.setObjectName("action_3")
        self.solveNewTaskAcion = QtWidgets.QAction(MainWindow)
        self.newTaskMenu.addAction(self.addNewTaskAction)
        self.newTaskMenu.addAction(self.solveNewTaskAcion)
        self.solveNewTaskAcion.setObjectName("action_4")
        self.menubar.addAction(self.loadMenu.menuAction())
        self.menubar.addAction(self.newTaskMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Просмотр списка задач"))
        self.label.setText(_translate("MainWindow", "Поиск"))
        self.comboBox.setItemText(0, _translate("MainWindow", "По всем параметрам"))
        self.solveButton.setText(_translate("MainWindow", "Решить"))
        self.deleteButton.setText(_translate("MainWindow", "Удалить"))
        self.exportButton.setText(_translate("MainWindow", "Экспортировать"))
        self.loadMenu.setTitle(_translate("MainWindow", "Открыть"))
        self.newTaskMenu.setTitle(_translate("MainWindow", "Новая задача"))
        self.loadDBAction.setText(_translate("MainWindow", "Базу примеров"))
        self.loadFileAction.setText(_translate("MainWindow", "Файл..."))
        self.addNewTaskAction.setText(_translate("MainWindow", "Добавить к текущей таблице"))
        self.solveNewTaskAcion.setText(_translate("MainWindow", "Ввести данные и решить"))
