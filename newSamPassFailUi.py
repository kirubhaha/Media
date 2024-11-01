# Form implementation generated from reading ui file 'newSamPassFailUi.ui'
#
# Created by: PyQt6 UI code generator 6.4.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class NewSamplePassFail_Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        self.screen = QtWidgets.QApplication.primaryScreen()
        self.screen_geometry = self.screen.geometry()
        self.screen_width = self.screen_geometry.width()
        self.screen_height = self.screen_geometry.height()
        Form.resize(self.screen_width, self.screen_height)
        Form.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        Form.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.widget = QtWidgets.QWidget(parent=Form)
        self.widget.setGeometry(QtCore.QRect(5, 5, 191, 131))
        self.widget.setStyleSheet("QPushButton#logOutButton{\n"
"    background-color:#41436A;\n"
"    color:rgba(255, 255, 255, 200);\n"
"    border-radius:5px;\n"
"}\n"
"QPushButton#logOutButton:pressed{\n"
"    padding-left:5px;\n"
"    padding-top:5px;\n"
"    background-color:#F64668;\n"
"    background-position:calc(100%-10px)center;\n"
"}\n"
"QPushButton#logOutButton:hover{\n"
"    background-color:#F64668;\n"
"}\n"
"QPushButton#logsButton{\n"
"    background-color:#41436A;\n"
"    color:rgba(255, 255, 255, 200);\n"
"    border-radius:15px;\n"
"padding-bottom:3px;\n"
"}\n"
"QPushButton#logsButton:pressed{\n"
"    padding-left:5px;\n"
"    padding-top:5px;\n"
"    background-color:#F64668;\n"
"    background-position:calc(100%-10px)center;\n"
"}\n"
"QPushButton#logsButton:hover{\n"
"    background-color:#F64668;\n"
"}\n"
"QToolButton#settingsButton{\n"
"    background-color:#41436A;\n"
"    color:rgba(255, 255, 255, 200);\n"
"    border-radius:15px;\n"
"padding-bottom:3px;\n"
"}\n"
"QToolButton#settingsButton:pressed{\n"
"    padding-left:5px;\n"
"    padding-top:5px;\n"
"    background-color:#F64668;\n"
"    background-position:calc(100%-10px)center;\n"
"}\n"
"QToolButton#settingsButton:hover{\n"
"    background-color:#F64668;\n"
"}\n"
"QPushButton{\n"
"    background-color:#984063;\n"
"    color:rgba(255, 255, 255, 200);\n"
"    border-radius:5px;\n"
"}\n"
"QPushButton:pressed{\n"
"    padding-left:5px;\n"
"    padding-top:5px;\n"
"    background-color:#26648E;\n"
"    background-position:calc(100%-10px)center;\n"
"}\n"
"QPushButton:hover{\n"
"    background-color:#26648E;\n"
"}\n"
"")
        self.widget.setObjectName("widget")
        self.containerLabel = QtWidgets.QLabel(parent=self.widget)
        self.containerLabel.setGeometry(QtCore.QRect(0, 5, 189, 121))
        self.containerLabel.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"border-radius:20px;\n"
"border:3px solid #41436A;")
        self.containerLabel.setText("")
        self.containerLabel.setObjectName("containerLabel")
        self.passButton = QtWidgets.QPushButton(parent=self.widget)
        self.passButton.setGeometry(QtCore.QRect(18, 20, 151, 41))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(14)
        font.setBold(True)
        self.passButton.setFont(font)
        self.passButton.setStyleSheet("")
        self.passButton.setObjectName("passButton")
        self.failButton = QtWidgets.QPushButton(parent=self.widget)
        self.failButton.setGeometry(QtCore.QRect(18, 70, 151, 41))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(14)
        font.setBold(True)
        self.failButton.setFont(font)
        self.failButton.setStyleSheet("")
        self.failButton.setObjectName("failButton")

        self.passButton.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25,xOffset=3,yOffset=3))
        self.failButton.setGraphicsEffect(QtWidgets.QGraphicsDropShadowEffect(blurRadius=25,xOffset=3,yOffset=3))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.passButton.setText(_translate("Form", "Pass"))
        self.failButton.setText(_translate("Form", "Fail"))
