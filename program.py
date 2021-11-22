from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread
from funktions import *
# Импортируем наш файл
from programs import Ui_Window
from login import Ui_MainWindow
import sys

class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.ui.pushButton.clicked.connect(self.win)
        self.ui.lineEdit.setText('user')


    def win(self):
        log = self.ui.lineEdit.text()
        pas = self.ui.lineEdit_2.text()
        if log == 'user' and pas == 'test':
            application.show()
            login.close()
        else:
            self.ui.label_4.setText('Неверный логин/пароль')

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Enter or e.key() == QtCore.Qt.Key_Return:
            self.win()



class UpdateProgressBar(QThread):
    def __init__(self, mainwindow, parent=None):
        super().__init__()
        self.mainwindow = mainwindow





    def run(self):
        while True:
            if self.mainwindow.valueProcent < 100:
                if self.mainwindow.valueProcent == 0:
                    self.mainwindow.ui.label_3.setText('Начинаю обработку....')
                else:
                    self.mainwindow.ui.label_3.setText(self.mainwindow.file)
                self.mainwindow.ui.progressBar.setValue(self.mainwindow.valueProcent)
            else:
                self.mainwindow.ui.label_3.setText(self.mainwindow.file)
                self.mainwindow.ui.progressBar.setValue(self.mainwindow.valueProcent)
                self.mainwindow.valueProcent = 0
                break





class window(QtWidgets.QMainWindow):
    valueProcent = 0
    file = ''
    listUrl = {}
    listValue = {"Артикул": "article", "Производитель": "brand", "Наименование": "name", "Цена": "price", "N/A": "False"}
    def __init__(self):
        super(window, self).__init__()
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.open_file)
        self.ui.listWidget.itemClicked.connect(self.getListItem)
        self.ui.pushButton_2.clicked.connect(self.pressObrabotka)
        self.progressBarUpdate = UpdateProgressBar(mainwindow=self)
        self.ui.Left.setChecked(True)
        self.ui.comboBox.activated.connect(self.sortList)
        self.ui.lineEdit.setText('compareFile')

    def sortList(self):
        try:
            tekValue = self.ui.comboBox.currentText()
            bbb = self.ui.listWidget.findItems(tekValue, QtCore.Qt.MatchFixedString)
            if len(bbb) > 0:
                for item in bbb:
                    items = self.ui.listWidget.row(item)
                    self.ui.listWidget.takeItem(items)
            self.ui.listWidget.insertItem(0, tekValue)
            self.updateList()
        except Exception as err:
            self.returnErrorAll(err)

    def returnErrorAll(self, err):
        self.ui.progressBar.setValue(0)
        self.ui.label_3.clear()
        self.ui.label_3.setText('Произошла исключительная ситуация\n' + str(err))


    def updateList(self, drop=False):
        try:
            listUrl2 = {}
            countList = self.ui.listWidget.count()
            for val in range(countList):
                if drop == True:
                    valueList = self.ui.listWidget.item(val).text()
                    listUrl2[valueList] = self.listUrl[valueList]
                    self.ui.comboBox.addItem(valueList)
                else:
                    valueList = self.ui.listWidget.item(val).text()
                    listUrl2[valueList] = self.listUrl[valueList]
            self.listUrl.clear()
            self.listUrl = listUrl2
        except Exception as err:
            self.returnErrorAll(err)






    def returnJoin(self):
        if self.ui.Left.isChecked():
            return 'left'
        elif self.ui.Inner.isChecked():
            return 'inner'

    def pressObrabotka(self):
        try:
            if self.ui.listWidget.count() <= 1:
                self.ui.label_3.setText('Для сравнение необходимо минимут 2 файла!!!')
                self.ui.label_3.setStyleSheet('color: red')
            else:
                self.valueProcent = 0
                self.ui.label_3.clear()
                obrab = get_param_for_files(self.listUrl)
                try:
                    if obrab[0] == 'Пустой список':
                        self.ui.label_3.setText('Список пуст')
                        self.ui.label_3.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    elif obrab[0] == 'param':
                        self.ui.label_3.setText(obrab[1])
                        self.ui.label_3.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                except Exception:
                    self.ui.label_3.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.returnDataFrameEnd(obrab)
        except Exception as err:
            self.returnErrorAll(err)

    def returnDataFrameEnd(self, listData):
        try:
            if self.ui.lineEdit.text() == '':
                nameFileForSave = 'compareFile'
            else:
                nameFileForSave = self.ui.lineEdit.text()
            self.progressBarUpdate.start()
            self.ui.label_3.setText('Начал обработку....')
            join = self.returnJoin()
            lengList = len(listData) - 1
            url = list(listData[-1].values())
            urlForSave = url[0][:url[0].rfind('/') + 1]
            nameFile = list(listData[-1].keys())
            newData = None
            for val in range(lengList):
                f = returnData(listData[val + 1])
                if val == 0:
                    newData = returnNewDate(listData[val], f, nameFile[val], nameFile[val + 1], val, join)
                else:
                    newData = returnNewDate(newData, f, nameFile[val], nameFile[val + 1], val, join)
                self.file = nameFile[val + 1]
                try:
                    self.valueProcent = int(val / (lengList - 2) * 100)
                except ZeroDivisionError:
                    self.valueProcent = 100

                if val == lengList - 2:
                    try:
                        if lengList % 2 == 1:
                            newData = renameColumns(newData, nameFile[val + 1])
                        try:
                            saveToCsv(newData, urlForSave, nameFileForSave)
                            self.ui.label_3.setText('Файл сохранен : \n' + urlForSave + nameFileForSave + '.csv')
                            self.ui.label_3.setStyleSheet('color: rgb(0, 170, 255)')
                        except PermissionError:
                            self.ui.label_3.setText('Закройте файл \"' + nameFileForSave + '\"\nили укажите другое имя для сохранения \nи нажмите снова \"Обработать\"')
                            self.ui.label_3.setStyleSheet('color: red')
                    except UnicodeEncodeError:
                        self.ui.label_3.setText('Файл сохранен : \n' + urlForSave + nameFileForSave + '.csv' + '\nНекоторый текс кирилицей переобразован в символы')
                        self.ui.label_3.setStyleSheet('color: rgb(0, 170, 255)')
                    break
        except Exception as err:
            self.returnErrorAll(err)






    def open_file(self):
        try:
            self.valueProcent = 0
            self.ui.label_3.clear()
            self.listUrl.clear()
            self.ui.comboBox.clear()
            self.ui.listWidget.clear()
            self.ui.progressBar.setValue(0)
            opened = QtWidgets.QFileDialog.getOpenFileNames(self, 'Выберете несколько файлов', '', 'Files (*.csv *.xls *.xlsx)')
            self.ui.listWidget.clear()
            for items in opened[0]:
                posList = items.rfind('/')
                fileName = items[posList + 1:]
                self.listUrl[fileName] = items
                self.ui.listWidget.addItem(fileName)
                self.ui.comboBox.addItem(fileName)
        except Exception as err:
            self.returnErrorAll(err)

    def getListRow(self):
        aaa = self.ui.listWidget.currentRow()
        return aaa

    def getListItem(self):
        try:
            self.ui.tableWidget.clear()
            bbb = self.ui.listWidget.currentItem()
            urlFile = self.listUrl[bbb.text()]
            listForTable = getTable(urlFile)
            count_col = listForTable.shape[1]
            count_row = listForTable.shape[0]
            self.ui.tableWidget.setColumnCount(count_col)
            self.ui.tableWidget.setRowCount(count_row)
            listItem = getNameColumn(urlFile)
            self.ui.label_2.setText("<html><head/><body><p align=\"center\"><span style=\" font-size:12pt;\">{0}</span></p></body></html>".format(self.ui.listWidget.currentItem().text()))

            row = 0
            while row < count_row:
                col = 0
                for en in listForTable.loc[row]:
                    stt = str(en)
                    cellinfo = QtWidgets.QTableWidgetItem(stt)
                    if row == 0:
                        combo = QtWidgets.QComboBox()
                        combo.addItem("Артикул")
                        combo.addItem("Производитель")
                        combo.addItem("Наименование")
                        combo.addItem("Цена")
                        combo.addItem("N/A")
                        combo.setProperty('col', col)
                        combo.setStyleSheet("color: rgb(0, 0, 0);font: 75 10pt \"Tahoma\";")
                        try:
                            if listItem[2] == str(col):
                                combo.setCurrentIndex(0)
                                combo.setStyleSheet("color: rgb(0, 170, 0);font: 75 10pt \"Tahoma\";")
                            elif listItem[3] == str(col):
                                combo.setCurrentIndex(1)
                                combo.setStyleSheet("color: rgb(0, 170, 0);font: 75 10pt \"Tahoma\";")
                            elif listItem[4] == str(col):
                                combo.setCurrentIndex(2)
                                combo.setStyleSheet("color: rgb(0, 170, 0);font: 75 10pt \"Tahoma\";")
                            elif listItem[5] == str(col):
                                combo.setCurrentIndex(3)
                                combo.setStyleSheet("color: rgb(0, 170, 0);font: 75 10pt \"Tahoma\";")
                            else:
                                combo.setCurrentIndex(4)
                        except Exception as er:
                            combo.setCurrentIndex(4)

                        self.ui.tableWidget.setCellWidget(0, col, combo)
                        combo.currentIndexChanged.connect(lambda: self.get(urlFile))
                    else:
                        self.ui.tableWidget.setItem(row, col, cellinfo)


                    col += 1
                row += 1
        except Exception as err:
            self.returnErrorAll(err)

    def get(self, url):
        try:
            combo = self.sender()
            nameColumn = combo.currentText()
            if nameColumn != "N/A":
                combo.setStyleSheet("color: rgb(0, 170, 0);font: 75 10pt \"Tahoma\";")
            elif nameColumn == "N/A":
                combo.setStyleSheet("color: rgb(0, 0, 0);font: 75 10pt \"Tahoma\";")
            numberColumn = combo.property('col')
            nameFile = getNameFile(url)
            insertSeting(nameFile, url, self.listValue[nameColumn], numberColumn)
        except Exception as err:
            self.returnErrorAll(err)


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Delete:
            self.ui.listWidget.takeItem(self.getListRow())
            self.ui.comboBox.clear()
            self.updateList(True)










app = QtWidgets.QApplication([])
application = window()
login = mywindow()
login.show()
sys.exit(app.exec())