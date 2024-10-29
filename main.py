from PyQt6 import QtWidgets,QtCore,QtGui
from loginUi import Login_Ui_Form
from signupUi import Signup_Ui_Form
from resetPasswordUi import RstPassword_Ui_Form
from mainRecUi import Recipient_Ui_MainWindow
from newSamPassFailUi import NewSamplePassFail_Ui_Form
from newSampleUi import NewSample_Ui_Form
from newDeclineUi import NewDecline_Ui_Form
from mainLabUi import Lab_Ui_MainWindow
from enterValueUi import ValueEntry_Ui_Form
from enterValueBigUi import ValueEntryBig_Ui_Form
from mainTechManTestUi import TechManTest_Ui_MainWindow
from mainTechManSamUi import TechManSam_Ui_MainWindow
from mainTechManSaleUi import TechSale_Ui_MainWindow
from newTestUi import NewTest_Ui_Form
from mainAccManServiceUi import AccManService_Ui_MainWindow
from adminMenuUi import AdminMenu_Ui_Form
from mainAdminServiceUi import AdminService_Ui_MainWindow
from mainAdminTestUi import AdminTest_Ui_MainWindow
from mainAdminServiceAnalysisUi import AdminServiceAnalysis_Ui_MainWindow
from mainAdminSaleUi import AdminSale_Ui_MainWindow
from addItemUi import AddItem_Ui_Form
from removeItemUi import RemoveItem_Ui_Form
from mainAdminSalesOrdersUi import AdminSalesOrders_Ui_MainWindow
from addSalesUi import AddSale_Ui_Form
from mainAdminPurchaseOrdersUi import AdminPurchaseOrders_Ui_MainWindow
from addPurchaseUi import AddPurchase_Ui_Form
from mainAdminSaleAnalysisUi import AdminSaleAnalysis_Ui_MainWindow
from mainAccSalesOrdersUi import AccSalesOrders_Ui_MainWindow
from mainAccPurchaseOrdersUi import AccPurchaseOrders_Ui_MainWindow
from mainAccSaleAnalysisUi import AccSaleAnalysis_Ui_MainWindow
from detailsUi import DetailsUi_Form
from logsUi import LogsUi_Form
from jinja2 import Environment, FileSystemLoader
import psycopg2
import base64
import time
import re
import socket
import webbrowser
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from concurrent.futures import ThreadPoolExecutor
import sys
import datetime
import os
import pandas as pd

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def check_internet_connection():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

def create_connection():
    conn = psycopg2.connect(host="192.168.140.201", dbname="postgres", user="postgres", password="root", port=5432)
    return conn

def log_db_operation(c, eid,message):
    try:
        c.execute("SELECT Name FROM EmployeeMaster WHERE EID = %s", (eid,))
        employeeName = c.fetchone()[0]  
        dateTimeNow = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        logEntry = """INSERT INTO Logs(Details) 
                VALUES (%s)"""
        Detail = f"{dateTimeNow} - {employeeName} {message}"
        c.execute(logEntry, (Detail,))
    except Exception as e:
        print(e)

class loginApp(QtWidgets.QWidget,Login_Ui_Form):
    def __init__(self):
        super(loginApp,self).__init__()
        self.setupUi(self)

        self.logInButton.clicked.connect(self.checkUser)
        self.logInButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.checkUser()
        else:
            super(loginApp, self).keyPressEvent(event)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def checkUser(self):
        style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(46, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;"
        username=self.usernameLineEdit.text().strip()
        password=self.passwordLineEdit.text()
        self.usernameLineEdit.setStyleSheet(style)
        self.passwordLineEdit.setStyleSheet(style)

        try:
            conn=create_connection()
            c=conn.cursor()
            query = """SELECT EmployeeMaster.EID,EmployeeMaster.Name, EmployeeMaster.Role 
            FROM EmployeeMaster 
            INNER JOIN LoginCredentials ON LoginCredentials.EID = EmployeeMaster.EID 
            WHERE LoginCredentials.Username = %s AND LoginCredentials.Password = %s;"""
            c.execute(query, (username, password))
            queryData=c.fetchone()
            if queryData:
                print("Login Success")
                Eid,Ename,Erole=queryData
                self.loadRoleSpecificWindow(Eid, Ename, Erole)
                c.close()
                conn.close()
                return
            else:
                self.showLoginError()
                c.close()
                conn.close()
                return
        except psycopg2.Error as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
         
    def loadRoleSpecificWindow(self, Eid, Ename, Erole):
        conn=create_connection()
        c=conn.cursor()
        if Erole == "Receipient": 
            log_db_operation(c,Eid,f"has logged in")
            conn.commit()
            c.close()
            conn.close()
            receipientWindow = mainRecApp(Eid, Ename, Erole.lower())
            widget.addWidget(receipientWindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        if Erole == "Lab Technician":           
            log_db_operation(c,Eid,f"has logged in")
            conn.commit()
            c.close()
            conn.close()
            labWindow = mainLabApp(Eid,Ename, Erole.lower())
            widget.addWidget(labWindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        if Erole == "Technical Manager":    
            log_db_operation(c,Eid,f"has logged in")   
            conn.commit()
            c.close()
            conn.close()    
            techWindow = mainTechManSamApp(Eid, Ename, Erole.lower())
            widget.addWidget(techWindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        if Erole == "Account Manager":   
            log_db_operation(c,Eid,f"has logged in")   
            conn.commit()
            c.close()
            conn.close()     
            accWindow = mainAccApp(Eid, Ename, Erole.lower())
            widget.addWidget(accWindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        if Erole == "Admin":   
            log_db_operation(c,Eid,f"has logged in") 
            conn.commit()
            c.close()
            conn.close()
            adminWindow = AdminMenuApp(Eid, Ename, Erole.lower())
            widget.addWidget(adminWindow)
            widget.setCurrentIndex(widget.currentIndex() + 1)
        self.close()

    def showLoginError(self):
        self.highlightError(self.usernameLineEdit)
        self.highlightError(self.passwordLineEdit)
        self.highlightButton()
        print("Login Failed")

    def highlightButton(self):
        originalStyleSheet = self.logInButton.styleSheet()
        self.logInButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.logInButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

class DraggableMixin(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.draggable = True
        self.old_pos = None

    def mousePressEvent(self, event):
        if self.draggable:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.old_pos = event.globalPosition()

    def mouseMoveEvent(self, event):
        if self.draggable and self.old_pos:
            delta = event.globalPosition() - self.old_pos
            new_pos = self.pos() + delta.toPoint() 
            self.move(new_pos)
            self.old_pos = event.globalPosition()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.old_pos = None

class mainRecApp(QtWidgets.QMainWindow,Recipient_Ui_MainWindow):
    BigReport=False
    browser_closed = QtCore.pyqtSignal()
    def __init__(self,Eid,Ename,Erole):
        super(mainRecApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()  
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.reloadButton.clicked.connect(self.gotoReload)
        self.newButton.clicked.connect(self.gotoPassFail)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            query = """SELECT Date, Name, Age, Gender, MobileNo, Email, Address, SID, CID, AmountEstimated, PaymentType
                    FROM CustomerMaster ORDER BY Date DESC;"""
            try:
                c.execute(query)
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRow(self, tablerow, row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)
            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)
            item2=QtWidgets.QTableWidgetItem(str(row[2]))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)
            item3=QtWidgets.QTableWidgetItem(str(row[3]))
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)
            item4=QtWidgets.QTableWidgetItem(str(row[4]))
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,4,item4)
            item5=QtWidgets.QTableWidgetItem(str(row[5]))
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,5,item5)
            item6=QtWidgets.QTableWidgetItem(str(row[6]))
            item6.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,6,item6)
            
            combinedStr1=self.retrivelNames(str(row[7]))
            list_widget7 = ListViewInCellWidget(combinedStr1)
            self.tableWidget.setCellWidget(tablerow, 7, list_widget7)
            
            combinedStr2=self.retrivelTests(str(row[7]))
            list_widget8 = ListViewInCellWidget(combinedStr2)
            self.tableWidget.setCellWidget(tablerow, 8, list_widget8)

            combinedStr3=self.retrivelStatus(str(row[7]))
            if combinedStr3=="Failed":
                item9=QtWidgets.QTableWidgetItem("Failed")
                item9.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow, 9, item9)

                item10=QtWidgets.QTableWidgetItem("NA")
                item10.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow, 10, item10)

                item11=QtWidgets.QTableWidgetItem("NA")
                item11.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow, 11, item11)

                item12=QtWidgets.QTableWidgetItem("NA")
                item12.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow, 12, item12)

            else:
                list_widget9 = ListViewInCellWidget(combinedStr3)
                self.tableWidget.setCellWidget(tablerow, 9, list_widget9)

                item10=QtWidgets.QTableWidgetItem(f"₹ {str(row[9])}")
                item10.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow, 10, item10)

                item11 = None
                payment_type = str(row[10])
                if payment_type in ['Cash','Credit Card','Debit Card','Net Banking','UPI']:
                    if payment_type == 'Cash':
                        item11 = QtWidgets.QTableWidgetItem("Cash")
                    elif payment_type == 'Credit Card':
                        item11 = QtWidgets.QTableWidgetItem("Credit Card")
                    elif payment_type == 'Debit Card':
                        item11 = QtWidgets.QTableWidgetItem("Debit Card")
                    elif payment_type == 'Net Banking':
                        item11 = QtWidgets.QTableWidgetItem("Net Banking")
                    elif payment_type == 'UPI':
                        item11 = QtWidgets.QTableWidgetItem("UPI")
                    if item11 is not None:
                        item11.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                        self.tableWidget.setItem(tablerow, 11, item11)
                else:
                    combo_box_widget = ComboBoxInCellWidget(str(row[8]),self.Erole, parent=self.tableWidget)
                    self.tableWidget.setCellWidget(tablerow,11,combo_box_widget)

                self.addPreviewButton(tablerow, 12, "Preview", str(row[8]), self.Ename, self.Erole,str(row[7]))
                        
            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)

    def retrivelNames(self,SIDS):
        try:
            self.strNamesList=[]
            self.strId=SIDS
            if ', ' in self.strId:
                items = self.strId.split(', ') 
            else:
                items = [self.strId]
            conn=create_connection()
            c=conn.cursor()
            for item in items:
                try:
                    Qry="SELECT SampleName FROM SampleMaster WHERE SID = %s"
                    c.execute(Qry,(item,))
                    self.QryResult=c.fetchone()
                    self.strNamesList.append(self.QryResult[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.strNames=', '.join(self.strNamesList)
            return self.strNames
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            
    def retrivelStatus(self,SIDS):
        try:
            self.strStatusList=[]
            self.strId=SIDS
            if ', ' in self.strId:
                items = self.strId.split(', ') 
            else:
                items = [self.strId]
            conn=create_connection()
            c=conn.cursor()
            for item in items:
                try:
                    Qry="SELECT Status FROM SampleMaster WHERE SID = %s"
                    c.execute(Qry,(item,))
                    self.QryResult=c.fetchone()
                    if self.QryResult[0]=="Failed":
                        return "Failed"
                    self.strStatusList.append(self.QryResult[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.strStatus=', '.join(self.strStatusList)
            return self.strStatus
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def retrivelTests(self,SIDS):
        try:
            self.strTestsList=[]
            self.strId=SIDS
            if ', ' in self.strId:
                items = self.strId.split(', ') 
            else:
                items = [self.strId]
            conn=create_connection()
            c=conn.cursor()
            for item in items:
                try:
                    Qry1 ="SELECT TID FROM SampleMaster WHERE SID = %s"
                    c.execute(Qry1,(item,))
                    self.Qry1Result=c.fetchone()
                    tidLists=[int(x) for x in self.Qry1Result[0].split(',')]
                    testNameLists=[]
                    for val in tidLists:
                        Qry2="SELECT TestName FROM TestMaster WHERE TID = %s"
                        c.execute(Qry2,(val,))
                        self.Qry2Result=c.fetchone()
                        testNameLists.append(self.Qry2Result[0])
                    if len(testNameLists)>1:
                        self.val = ' ,'.join(testNameLists)
                        self.strTestsList.append(self.val)
                    else:
                        self.strTestsList.append(testNameLists[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.strTests=', '.join(self.strTestsList)
            return self.strTests
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSearch(self):
        try:            
            searchData=self.searchLineEdit.text().strip()
            conn=create_connection()
            c=conn.cursor()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            if not searchData:
                self.gotoReload()
            else:
                query = "SELECT Date,Name,Age,Gender,MobileNo,Email,Address,SID,CID,AmountEstimated,PaymentType FROM CustomerMaster WHERE Name LIKE %s;"
                c.execute(query, (f"%{searchData}%",))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoPassFail(self):
        newSampleWindow = PassFailApp(self.Eid, self.Ename, self.Erole)
        if not(newSampleWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def addPreviewButton(self, row, col, text, Id, Ename, Erole,Sid):
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(12)
        font.setBold(True)
        button = QtWidgets.QPushButton(str(text))
        button.setFont(font)
        button.setObjectName("cellPreviewButton")
        button.clicked.connect(lambda:self.gotoPreview(row,Id,Sid))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.tableWidget.setCellWidget(row, col, container)
        self.tableWidget.resizeRowToContents(row)

    def getCellWidgetText(self, row, col):
        widget = self.tableWidget.cellWidget(row, col)
        if widget and isinstance(widget, ListViewInCellWidget):
            return widget.getText()
        elif self.tableWidget.item(row, col):
            return self.tableWidget.item(row, col).text()
        else:
            return ''

    def gotoPreview(self, row, ID,SID):
        self.strTestsList=[]
        self.strId=SID
        if ', ' in self.strId:
            items = self.strId.split(', ') 
        else:
            items = [self.strId]
        conn=create_connection()
        c=conn.cursor()
        for item in items:
            try:
                Qry1 ="SELECT TID FROM SampleMaster WHERE SID = %s"
                c.execute(Qry1,(item,))
                self.Qry1Result=c.fetchone()
                tidLists=[int(x) for x in self.Qry1Result[0].split(',')]
                testNameLists=[]
                for val in tidLists:
                    Qry2="SELECT TestName FROM TestMaster WHERE TID = %s"
                    c.execute(Qry2,(val,))
                    self.Qry2Result=c.fetchone()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        if self.Qry2Result[0] not in ["Plant","Animal","Bacteria","Fungus"]:
            try:
                conn = create_connection()
                c = conn.cursor()
                c.execute("SELECT Name, Phno, Address, District, State, Email FROM CompanyDetails ORDER BY ID DESC")
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    CName, CPhno, CAddress, CDistrict, CState, CEmail = result
                else:
                    CName, CPhno, CAddress, CDistrict, CState, CEmail = '', '', '', '', '', ''
                Date = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ''
                todayDate = datetime.datetime.now().strftime('%Y-%m-%d')
                Name = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ''
                Age = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ''
                Gender = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ''
                MobileNo = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ''
                Email = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ''
                Address = self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else ''

                samples_str = self.getCellWidgetText(row, 7)
                tests_str = self.getCellWidgetText(row, 8)
                status_str = self.getCellWidgetText(row, 9)

                samples = samples_str.split(', ') if samples_str else []
                tests = tests_str.split(', ') if tests_str else []
                statuses = status_str.split(', ') if status_str else []

                conn = create_connection()
                c = conn.cursor()
                c.execute("SELECT TestResult FROM SampleMaster WHERE CID=%s", (ID,))
                results = [str(r[0]) for r in c.fetchall()]
                c.close()
                conn.close()
                
                if len(tests) != len(results):
                    raise ValueError("Mismatch in the number of tests and results")

                sample_details = []
                for i in range(len(samples)):
                    sample_tests = tests[i].split(' ,') if ' ,' in tests[i] else [tests[i]]
                    sample_results = results[i].split(', ') if ', ' in results[i] else [results[i]]
                    if len(sample_tests) != len(sample_results):
                        raise ValueError("Preview Unavailable..!Try after some time.")

                    test_and_results = [{'test': test, 'result': result} for test, result in zip(sample_tests, sample_results)]
                    sample_details.append({
                        'sno': i + 1,
                        'name': samples[i],
                        'tests_and_results': test_and_results
                    })

                status = "Approved" if any(s == "Approved" for s in statuses) else "Not approved"

                data = {
                    'CName': CName,
                    'CPhno': CPhno,
                    'CEmail': CEmail,
                    'CAddress': CAddress,
                    'CDistrict': CDistrict,
                    'CState': CState,
                    'Date': Date,
                    'todayDate': todayDate,
                    'Name': Name,
                    'Age': Age,
                    'Gender': Gender,
                    'MobileNo': MobileNo,
                    'Email': Email,
                    'Address': Address,
                    'Status': status,
                    'samples': sample_details
                }


                env = Environment(loader=FileSystemLoader(resource_path('')))
                template = env.get_template('Services.html')
                output_text = template.render(data)

                output_html = 'Report.html'
                with open(output_html, 'w', encoding='utf-8') as file:
                    file.write(output_text)
                    file_path = resource_path(output_html)
                
                webbrowser.open(f'file://{file_path}')
                time.sleep(5)
                try:
                    while True:
                        os.remove(file_path)
                        break
                except PermissionError:
                    time.sleep(5)

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        else:
            try:
                conn = create_connection()
                c = conn.cursor()
                c.execute("SELECT Name, Phno, Address, District, State, Email FROM CompanyDetails ORDER BY ID DESC")
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    CName, CPhno, CAddress, CDistrict, CState, CEmail = result
                else:
                    CName, CPhno, CAddress, CDistrict, CState, CEmail = '', '', '', '', '', ''
                Date = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ''
                todayDate = datetime.datetime.now().strftime('%Y-%m-%d')
                Name = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ''
                Age = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ''
                Gender = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ''
                MobileNo = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ''
                Email = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ''
                Address = self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else ''
                
                sample = self.getCellWidgetText(row, 7) if self.getCellWidgetText(row, 7) else ''
                test = self.getCellWidgetText(row, 8) if self.getCellWidgetText(row, 8) else ''
                status = self.getCellWidgetText(row, 9) if self.getCellWidgetText(row, 9) else ''

                conn = create_connection()
                c = conn.cursor()
                c.execute("SELECT TestResult,Result,Img1,Img2,Quantity,SampleDesp FROM SampleMaster WHERE CID=%s", (ID,))
                result = c.fetchone()
                c.close()
                conn.close()
                
                if not result:
                    raise ValueError("No results found for the given CID")

                test_result, result, img1, img2,qty,lbl = result

                img1_base64 = base64.b64encode(img1).decode('utf-8') if img1 else ''
                img2_base64 = base64.b64encode(img2).decode('utf-8') if img2 else ''


                data = {
                    'CName': CName,
                    'CPhno': CPhno,
                    'CEmail': CEmail,
                    'CAddress': CAddress,
                    'CDistrict': CDistrict,
                    'CState': CState,
                    'Date': Date,
                    'todayDate': todayDate,
                    'Name': Name,
                    'Age': Age,
                    'Gender': Gender,
                    'MobileNo': MobileNo,
                    'Email': Email,
                    'Address': Address,
                    'Status': status,
                    'SName': sample,
                    'SQuan':qty,
                    'SLabel':lbl,
                    'Data':test_result,
                    'Result':result,
                    'image1':img1_base64,
                    'image2':img2_base64
                }

                env = Environment(loader=FileSystemLoader(resource_path('')))
                template = env.get_template('Sequence.html')
                output_text = template.render(data)

                output_html = 'Report.html'
                with open(output_html, 'w', encoding='utf-8') as file:
                    file.write(output_text)
                    file_path = resource_path(output_html)
                
                webbrowser.open(f'file://{file_path}')
                time.sleep(5)
                try:
                    while True:
                        os.remove(file_path)
                        break
                except PermissionError:
                    time.sleep(5)

            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def closeEvent(self, event):
        self.browser_closed.emit()
        super().closeEvent(event)

class PassFailApp(QtWidgets.QDialog, DraggableMixin,NewSamplePassFail_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(PassFailApp,self).__init__()
        self.setupUi(self)
        self.Ename=Ename
        self.Eid=Eid
        self.Erole=Erole
        self.passButton.clicked.connect(self.gotoAddSample)
        self.failButton.clicked.connect(self.gotoDeclineSample)
    
    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def gotoAddSample(self):
        newSampleWindow = NewSamApp(self.Eid, self.Ename, self.Erole)
        if not(newSampleWindow.exec()) == QtWidgets.QDialog.rejected:
            self.reject() 

    def gotoDeclineSample(self):
        newDeclineWindow = NewDecApp(self.Eid, self.Ename, self.Erole)
        if not(newDeclineWindow.exec()) == QtWidgets.QDialog.rejected:
            self.reject() 
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.reject()
        else:
            super(PassFailApp, self).keyPressEvent(event)

class NewSamApp(QtWidgets.QDialog, DraggableMixin,NewSample_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(NewSamApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.smtp_server_conn = None
        self.setupSampleEntryFields()
                
        self.addButton.clicked.connect(self.addNewLine) 
        self.nameLineEdit.editingFinished.connect(self.updateLineEdits)   
        self.okButton.clicked.connect(self.gotoAddDt)
        self.cancelButton.clicked.connect(self.gotoRec)
        self.searchLineEdit.textChanged.connect(self.filterComboBoxItems)
        self.okButton.setFocus()
        
    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoAddDt()
        else:
            super(NewSamApp, self).keyPressEvent(event)
        
    def updateLineEdits(self):
        try:
            name = self.nameLineEdit.text().strip()
            if name:
                conn = create_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT Age,Gender,MobileNo,Email,Address 
                    FROM CustomerMaster 
                    WHERE Name LIKE %s 
                    ORDER BY CID DESC LIMIT 1
                """, (f"%{name}%",))
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    age,gender,mobileno,email,address = result
                    self.ageSpinBox.setValue(int(age if age!='' else 0)) 
                    if gender == 'Male':
                        self.genderComboBox.setCurrentIndex(0)
                    elif gender == 'Female':
                        self.genderComboBox.setCurrentIndex(1)
                    else:
                        self.genderComboBox.setCurrentIndex(2)
                    self.emailLineEdit.setText(str(email))
                    self.MnoLineEdit.setText(str(mobileno))
                    self.addressLineEdit.setText(str(address))
                else:
                    self.ageSpinBox.clear()
                    self.genderComboBox.setCurrentIndex(-1)
                    self.emailLineEdit.clear()
                    self.MnoLineEdit.clear()
                    self.addressLineEdit.clear()
            else:
                self.ageSpinBox.clear()
                self.genderComboBox.setCurrentIndex(-1)
                self.emailLineEdit.clear()
                self.MnoLineEdit.clear()
                self.addressLineEdit.clear()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def setupSampleEntryFields(self):
        try:
            self.hboxLayout = QtWidgets.QHBoxLayout()

            font = QtGui.QFont()
            font.setFamily("Dubai") 
            font.setPointSize(14)
            self.sampleNameLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            self.sampleNameLineEdit.setFont(font)
            self.sampleNameLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            self.sampleNameLineEdit.setPlaceholderText("Sample Name*")
            self.sampleNameLineEdit.setObjectName("sampleNameLineEdit")
            self.sampleNameLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            self.sampleNameLineEdit.setMaxLength(25)
            self.sampleNameLineEdit.setClearButtonEnabled(True)

            self.sampleDespLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            self.sampleDespLineEdit.setFont(font)
            self.sampleDespLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            self.sampleDespLineEdit.setPlaceholderText("Description")
            self.sampleDespLineEdit.setObjectName("sampleDespLineEdit")
            self.sampleDespLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            self.sampleDespLineEdit.setMaxLength(100)
            self.sampleDespLineEdit.setClearButtonEnabled(True)

            self.sampleQuantityLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            self.sampleQuantityLineEdit.setFont(font)
            self.sampleQuantityLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            self.sampleQuantityLineEdit.setPlaceholderText("Quantity")
            self.sampleQuantityLineEdit.setObjectName("sampleQuantityLineEdit")
            self.sampleQuantityLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            self.sampleQuantityLineEdit.setMaxLength(25)
            self.sampleQuantityLineEdit.setClearButtonEnabled(True)

            self.comboBox = CheckableComboBox()
            self.comboBox.setMaximumSize(QtCore.QSize(290, 16777215))
            self.comboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
            self.comboBox.setObjectName("comboBox")
            font = QtGui.QFont()
            font.setFamily("Dubai")
            font.setPointSize(13)
            self.comboBox.setFont(font)
            self.comboBox.setAcceptDrops(False)
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT TestName FROM TestMaster ORDER BY TestName ASC")
            self.QryResult=c.fetchall()
            c.close()
            conn.close()
            self.QryFinal=[self.item[0] for self.item in self.QryResult]
            self.comboBox.addItems(self.QryFinal)
            self.newRows = []
            
            for j in range(self.comboBox.count()):
                item = self.comboBox.model().item(j, 0)
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            self.hboxLayout.addWidget(self.sampleNameLineEdit, stretch=1)
            self.hboxLayout.addSpacing(10)
            self.hboxLayout.addWidget(self.sampleDespLineEdit, stretch=1)
            self.hboxLayout.addSpacing(10)
            self.hboxLayout.addWidget(self.sampleQuantityLineEdit, stretch=1)
            self.hboxLayout.addSpacing(10)
            self.hboxLayout.addWidget(self.comboBox, stretch=4)

            self.formLayout.addRow(self.hboxLayout)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.comboBoxes = [self.comboBox]
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def filterComboBoxItems(self):
        try:
            search_text = self.searchLineEdit.text().strip().lower()
            for comboBox in self.comboBoxes:
                for i in range(comboBox.count()):
                    item = comboBox.model().item(i)
                    item_text = item.text().lower()
                    comboBox.view().setRowHidden(i, search_text not in item_text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoRec(self):
        self.reject()
    
    def addNewLine(self):
        try:
            hboxLayout = QtWidgets.QHBoxLayout()

            font = QtGui.QFont()
            font.setFamily("Dubai") 
            font.setPointSize(14)
            newSampleNameLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            newSampleNameLineEdit.setFont(font)
            newSampleNameLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            newSampleNameLineEdit.setPlaceholderText("Sample Name*")
            newSampleNameLineEdit.setObjectName(f"sampleNameLineEdit_{self.i}")
            newSampleNameLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            newSampleNameLineEdit.setMaxLength(25)
            newSampleNameLineEdit.setClearButtonEnabled(True)

            newSampleDespLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            newSampleDespLineEdit.setFont(font)
            newSampleDespLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            newSampleDespLineEdit.setPlaceholderText("Description")
            newSampleDespLineEdit.setObjectName(f"sampleDespLineEdit_{self.i}")
            newSampleDespLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            newSampleDespLineEdit.setMaxLength(100)
            newSampleDespLineEdit.setClearButtonEnabled(True)

            newSampleQuantityLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            newSampleQuantityLineEdit.setFont(font)
            newSampleQuantityLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            newSampleQuantityLineEdit.setPlaceholderText("Quantity")
            newSampleQuantityLineEdit.setObjectName(f"sampleQuantityLineEdit_{self.i}")
            newSampleQuantityLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            newSampleQuantityLineEdit.setMaxLength(25)
            newSampleQuantityLineEdit.setClearButtonEnabled(True)

            newcomboBox = CheckableComboBox()
            newcomboBox.setMaximumSize(QtCore.QSize(290, 16777215))
            newcomboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
            font = QtGui.QFont()
            font.setFamily("Dubai")
            font.setPointSize(13)
            newcomboBox.setFont(font)
            newcomboBox.setObjectName(f"comboBox_{self.i}")
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT TestName FROM TestMaster ORDER BY TestName ASC")
            self.QryResult=c.fetchall()
            c.close()
            conn.close()
            self.QryFinal=[self.item[0] for self.item in self.QryResult]
            newcomboBox.addItems(self.QryFinal)

            for j in range(newcomboBox.count()):
                    item = newcomboBox.model().item(j, 0)
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            self.searchLineEdit.clear()
            self.comboBoxes.append(newcomboBox)
            hboxLayout.addWidget(newSampleNameLineEdit, stretch=1)
            hboxLayout.addSpacing(10)
            hboxLayout.addWidget(newSampleDespLineEdit, stretch=1)
            hboxLayout.addSpacing(10)
            hboxLayout.addWidget(newSampleQuantityLineEdit, stretch=1)
            hboxLayout.addSpacing(10)
            hboxLayout.addWidget(newcomboBox, stretch=4)
            self.formLayout.addRow(hboxLayout)

            self.newRows.append(self.i)
            self.i=self.i+1
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoAddDt(self):
        try:
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:#984063; color:rgb(0, 0, 0); padding-bottom:7px;"
            self.nameLineEdit.setStyleSheet(style)
            self.MnoLineEdit.setStyleSheet(style)
            self.addressLineEdit.setStyleSheet(style)
            self.emailLineEdit.setStyleSheet(style)
            self.sampleNameLineEdit.setStyleSheet(style)
            regexEmail = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
            name=self.nameLineEdit.text().strip()
            if not name or any(char.isdigit() for char in name):
                self.highlightError(self.nameLineEdit)
                self.highlightButton()
                return
            age=self.ageSpinBox.value() or ""
            age=''.join(str(age))
            gender=self.genderComboBox.currentText() or ""
            mno=self.MnoLineEdit.text().strip()
            if len(mno)!=10:
                self.highlightError(self.MnoLineEdit)
                self.highlightButton()
                return
            address=self.addressLineEdit.text()
            if not address or len(address) > 150:
                self.highlightError(self.addressLineEdit)
                self.highlightButton()
                return
            email=self.emailLineEdit.text().strip()
            if not bool(re.match(regexEmail, email)):
                self.highlightError(self.emailLineEdit)
                self.highlightButton()
                return
            sampleName=self.sampleNameLineEdit.text().strip()
            sampleDesp=self.sampleDespLineEdit.text().strip() or ""
            sampleQty=self.sampleQuantityLineEdit.text().strip() or ""
            testApplied=self.comboBox.checked_items()
            if not sampleName or testApplied == None or testApplied == []:
                self.highlightError(self.sampleNameLineEdit)
                self.highlightButton()
                return
            samplesDictionary = {}
            samplesDictionary[sampleName]=[sampleDesp,sampleQty,testApplied]
            if not self.newRows == []:
                for k in range(1,len(self.newRows)+1):
                    sample_name = self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)).text()
                    sample_desp = self.findChild(QtWidgets.QLineEdit,"sampleDespLineEdit_"+str(k)).text() or ""
                    sample_qty = self.findChild(QtWidgets.QLineEdit,"sampleQuantityLineEdit_"+str(k)).text() or ""
                    comboBox_values = self.findChild(QtWidgets.QComboBox,"comboBox_"+str(k)).checked_items()
                    if not self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)):
                        self.highlightError(self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)))
                        self.highlightButton()
                        return
                    if comboBox_values == None or comboBox_values == []:
                        self.highlightError(self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)))
                        self.highlightButton()
                        return
                    samplesDictionary[sample_name] = [sample_desp,sample_qty,comboBox_values]
            dateToday=datetime.datetime.now().strftime("%Y-%m-%d")
            SNames=''
            conn=create_connection()
            c=conn.cursor()
            try:
                queryForCus = "INSERT INTO  CustomerMaster(Date, Name,Age , Gender,MobileNo,Email, Address,EID,SID,PaymentType) VALUES (%s, %s, %s, %s, %s,%s, %s,%s, %s,%s)"
                c.execute(queryForCus, (dateToday,name,age,gender,mno,email,address,self.Eid," ","Not Paid"))
                conn.commit()
                queryForId = "SELECT CID FROM CustomerMaster WHERE Name = %s and Age = %s and Gender = %s and MobileNo = %s and Email = %s and EID = %s ORDER BY CID DESC LIMIT 1"
                c.execute(queryForId,(name,age,gender,mno,email,self.Eid))
                retrievedCID=c.fetchone()
                sidLists=self.generate_sample_unique_id(retrievedCID[0],len(samplesDictionary))
                sidString=", ".join(sidLists)
                queryForSid = "UPDATE CustomerMaster SET SID = %s WHERE Name = %s and Age = %s and Gender = %s and MobileNo = %s and Email = %s and EID = %s and CID = %s "
                c.execute(queryForSid,(sidString,name,age,gender,mno,email,self.Eid,retrievedCID[0]))
                conn.commit()
                samplesTestDictionary={sidLists[i]: value for i,value in enumerate(samplesDictionary.values())}
                for key in samplesTestDictionary:
                    tidList=[]
                    value=samplesTestDictionary[key]
                    for item in value[2]:
                        queryForTid="SELECT TID FROM TestMaster WHERE TestName = %s"
                        c.execute(queryForTid,(item,))
                        retrievedTID=c.fetchone()
                        tidList.append(retrievedTID[0])
                    tidStr=", ".join(map(str, tidList))
                    samplesTestDictionary[key][2]=tidStr
                for (keys,values),nameKey in zip(samplesTestDictionary.items(),samplesDictionary):
                    SNames=SNames+nameKey
                    queryForSamp="INSERT INTO SampleMaster(SID,SampleName,SampleDesp,Quantity,TID,CID,Status) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                    c.execute(queryForSamp,(keys,nameKey, values[0], values[1], values[2],retrievedCID[0],"Pending",)) 
                    conn.commit()
                    rFee=self.retrivelFees(str(keys),dateToday)
                    c.execute("UPDATE SampleMaster SET AmountEstimated = %s WHERE SID = %s",(rFee,keys))
                    conn.commit()
                rTotalFee=self.retrivelTotalFees(str(retrievedCID[0]))
                c.execute("UPDATE CustomerMaster SET AmountEstimated = %s WHERE CID = %s",(rTotalFee,retrievedCID[0]))
                
                log_db_operation(c,self.Eid,f"has enrolled a new customer with CID {retrievedCID[0]}")

                conn.commit()
            except psycopg2.Error as e:
                print(e)
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.send_confirmation_email(email,SNames)
            self.gotoRec()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
          
    def retrivelFees(self,SID,Date):
        try:
            self.strFeesList=[]
            self.strId=SID
            if ', ' in self.strId:
                items = self.strId.split(', ') 
            else:
                items = [self.strId]
            conn=create_connection()
            c=conn.cursor()
            for item in items:
                try:
                    Qry1 ="SELECT TID FROM SampleMaster WHERE SID = %s"
                    c.execute(Qry1,(item,))
                    self.Qry1Result=c.fetchone()
                    tidLists=[int(x) for x in self.Qry1Result[0].split(',')]
                    testFeeList=[]
                    for tid in tidLists:
                        Qry2 = "SELECT Fee FROM RateMaster WHERE TID = %s AND Date = %s"
                        c.execute(Qry2, (tid, Date))
                        dateFeeResult = c.fetchone()

                        if not dateFeeResult:
                            Qry3 = "SELECT Fee FROM RateMaster WHERE TID = %s ORDER BY Date DESC LIMIT 1"
                            c.execute(Qry3, (tid,))
                            lastModifiedFeeResult = c.fetchone()
                            fee = float(lastModifiedFeeResult[0]) if lastModifiedFeeResult else 0.0
                        else:
                            fee = float(dateFeeResult[0])

                        Qry4 = "SELECT TaxRate, InclusiveOfTax FROM TestMaster WHERE TID = %s"
                        c.execute(Qry4, (tid,))
                        taxResult = c.fetchone()
                        if taxResult:
                            taxRate, inclusiveOfTax = taxResult
                            taxRateDigits = re.findall(r'\d+', taxRate)
                            if taxRateDigits:
                                taxRateDigits=int(taxRateDigits[0])
                                taxRateDigits = float(taxRateDigits) / 100  
                                if inclusiveOfTax == 'Yes':
                                    tax_amount = fee * taxRateDigits
                                    fee += tax_amount

                        testFeeList.append(fee)
                    if len(testFeeList)>1:
                        self.val = ' ,'.join(map(str, testFeeList))
                        self.strFeesList.append(self.val)
                    else:
                        self.strFeesList.append(testFeeList[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.strFees=', '.join(map(str, self.strFeesList))
            self.fee = [float(num) for num in self.strFees.split(",")]
            self.totalAmount=sum(self.fee)
            self.totalAmount=round(self.totalAmount, 2)
            return  self.totalAmount
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def retrivelTotalFees(self,CID):
        try:
            strTotalFeesList=[]
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT SID FROM CustomerMaster WHERE CID = %s",(CID,))
            strId,=c.fetchone()
            if ', ' in strId:
                items = strId.split(', ') 
            else:
                items = [strId]
            for item in items:
                try:
                    c.execute("SELECT AmountEstimated FROM SampleMaster WHERE SID = %s",(item,))
                    retrievedAE=c.fetchone()
                    strTotalFeesList.append(retrievedAE[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            fee = [float(num) for num in strTotalFeesList]
            totalAmount=sum(fee)
            totalAmount=round(totalAmount, 2)
            return totalAmount
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def generate_sample_unique_id(self,CustoId,SampNos):
        try:
            sample_id = 0
            sample_ids = []  
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            for i in range(SampNos):
                sample_id += 1
                padded_sample_id=str(sample_id).zfill(2)
                unique_sample_id = f"PAR-L/{current_date}/{CustoId}-{padded_sample_id}"
                sample_ids.append(unique_sample_id)
            return sample_ids
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def send_confirmation_email(self,to_address,Samples):      
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT Name, Phno, Email, Password FROM CompanyDetails ORDER BY ID DESC")
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            CName, CPhno, CEmail, CPassword = result
        else:
            CName, CPhno, CEmail, CPassword = '', '', '', ''

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        msg = MIMEMultipart()
        msg['From'] = CEmail
        msg['To'] = to_address
        msg['Subject'] = 'Sample Received and Under Processing'

        html_content = f"""
                <html>
                <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        width: 100%;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .content {{
                        background-color: #ffffff;
                        padding: 20px;
                        border: 1px solid #dddddd;
                    }}
                    h1 {{
                        color: #333333;
                    }}
                    p {{
                        color: #666666;
                    }}
                </style>
                </head>
                <body>
                    <div class="container">
                        <div class="content">
                            <p>Dear Customer,</p>
                            <p>We are pleased to inform you that we have received your sample {Samples} on <strong>{current_datetime}</strong>.</p>
                            <p>Our team is now processing your sample further. For any inquiries or clarifications, please contact us at <strong>{CPhno}</strong>.</p>
                            <p>Thank you for choosing our services.</p>
                            <p>Best regards,</p>
                            <p>{CName}</p>
                        </div>
                    </div>
                </body>
                </html>
                """
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            if check_internet_connection() and self.smtp_server_conn is None:
                try:
                    self.smtp_server_conn = smtplib.SMTP('smtp.gmail.com',587)
                    self.smtp_server_conn.starttls()
                    self.smtp_server_conn.login(CEmail,CPassword)
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            elif check_internet_connection() and self.smtp_server_conn is not None:
                try:
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "No internet connection - Send Confirmation Manually")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            
class NewDecApp(QtWidgets.QDialog, DraggableMixin,NewDecline_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(NewDecApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.smtp_server_conn = None
        self.setupSampleEntryFields()
                
        self.addButton.clicked.connect(self.addNewLine) 
        self.nameLineEdit.editingFinished.connect(self.updateLineEdits)   
        self.okButton.clicked.connect(self.gotoAddDt)
        self.cancelButton.clicked.connect(self.gotoRec)
        self.searchLineEdit.textChanged.connect(self.filterComboBoxItems)
        self.okButton.setFocus()
        

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoAddDt()
        else:
            super(NewDecApp, self).keyPressEvent(event)
        
    def updateLineEdits(self):
        try:
            name = self.nameLineEdit.text().strip()
            if name:
                conn = create_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT Age,Gender,MobileNo,Email,Address 
                    FROM CustomerMaster 
                    WHERE Name LIKE %s 
                    ORDER BY CID DESC LIMIT 1
                """, (f"%{name}%",))
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    age,gender,mobileno,email,address = result
                    self.ageSpinBox.setValue(int(age if age!='' else 0)) 
                    if gender == 'Male':
                        self.genderComboBox.setCurrentIndex(0)
                    elif gender == 'Female':
                        self.genderComboBox.setCurrentIndex(1)
                    else:
                        self.genderComboBox.setCurrentIndex(2)
                    self.emailLineEdit.setText(str(email))
                    self.MnoLineEdit.setText(str(mobileno))
                    self.addressLineEdit.setText(str(address))
                else:
                    self.ageSpinBox.clear()
                    self.genderComboBox.setCurrentIndex(-1)
                    self.emailLineEdit.clear()
                    self.MnoLineEdit.clear()
                    self.addressLineEdit.clear()
            else:
                self.ageSpinBox.clear()
                self.genderComboBox.setCurrentIndex(-1)
                self.emailLineEdit.clear()
                self.MnoLineEdit.clear()
                self.addressLineEdit.clear()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def setupSampleEntryFields(self):
        try:
            self.hboxLayout = QtWidgets.QHBoxLayout()

            font = QtGui.QFont()
            font.setFamily("Dubai") 
            font.setPointSize(14)
            self.sampleNameLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            self.sampleNameLineEdit.setFont(font)
            self.sampleNameLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            self.sampleNameLineEdit.setPlaceholderText("Sample Name*")
            self.sampleNameLineEdit.setObjectName("sampleNameLineEdit")
            self.sampleNameLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            self.sampleNameLineEdit.setMaxLength(25)
            self.sampleNameLineEdit.setClearButtonEnabled(True)

            self.sampleDespLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            self.sampleDespLineEdit.setFont(font)
            self.sampleDespLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            self.sampleDespLineEdit.setPlaceholderText("Reason*")
            self.sampleDespLineEdit.setObjectName("sampleDespLineEdit")
            self.sampleDespLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            self.sampleDespLineEdit.setMaxLength(100)
            self.sampleDespLineEdit.setClearButtonEnabled(True)

            self.comboBox = CheckableComboBox()
            self.comboBox.setMaximumSize(QtCore.QSize(290, 16777215))
            self.comboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
            self.comboBox.setObjectName("comboBox")
            font = QtGui.QFont()
            font.setFamily("Dubai")
            font.setPointSize(13)
            self.comboBox.setFont(font)
            self.comboBox.setAcceptDrops(False)
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT TestName FROM TestMaster ORDER BY TestName ASC")
            self.QryResult=c.fetchall()
            c.close()
            conn.close()
            self.QryFinal=[self.item[0] for self.item in self.QryResult]
            self.comboBox.addItems(self.QryFinal)
            self.newRows = []
            
            for j in range(self.comboBox.count()):
                item = self.comboBox.model().item(j, 0)
                item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            self.hboxLayout.addWidget(self.sampleNameLineEdit, stretch=1)
            self.hboxLayout.addSpacing(10)
            self.hboxLayout.addWidget(self.sampleDespLineEdit, stretch=2)
            self.hboxLayout.addSpacing(10)
            self.hboxLayout.addWidget(self.comboBox, stretch=4)

            self.formLayout.addRow(self.hboxLayout)
            self.scrollArea.setWidget(self.scrollAreaWidgetContents)
            self.comboBoxes = [self.comboBox]
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def filterComboBoxItems(self):
        try:
            search_text = self.searchLineEdit.text().strip().lower()
            for comboBox in self.comboBoxes:
                for i in range(comboBox.count()):
                    item = comboBox.model().item(i)
                    item_text = item.text().lower()
                    comboBox.view().setRowHidden(i, search_text not in item_text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoRec(self):
        self.reject()
    
    def addNewLine(self):
        try:
            hboxLayout = QtWidgets.QHBoxLayout()

            font = QtGui.QFont()
            font.setFamily("Dubai") 
            font.setPointSize(14)
            newSampleNameLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            newSampleNameLineEdit.setFont(font)
            newSampleNameLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            newSampleNameLineEdit.setPlaceholderText("Sample Name*")
            newSampleNameLineEdit.setObjectName(f"sampleNameLineEdit_{self.i}")
            newSampleNameLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            newSampleNameLineEdit.setMaxLength(25)
            newSampleNameLineEdit.setClearButtonEnabled(True)

            newSampleDespLineEdit = QtWidgets.QLineEdit(parent=self.scrollAreaWidgetContents)
            newSampleDespLineEdit.setFont(font)
            newSampleDespLineEdit.setStyleSheet("background-color:rgba(0, 0, 0, 0);\n"
                                    "border:2px solid rgba(0, 0, 0, 0);\n"
                                    "border-bottom-color:#984063;\n"
                                    "color:rgb(0, 0, 0);\n"
                                    "padding-bottom:5px;")
            newSampleDespLineEdit.setPlaceholderText("Reason*")
            newSampleDespLineEdit.setObjectName(f"sampleDespLineEdit_{self.i}")
            newSampleDespLineEdit.setInputMethodHints(QtCore.Qt.InputMethodHint.ImhPreferLowercase|QtCore.Qt.InputMethodHint.ImhPreferUppercase)
            newSampleDespLineEdit.setMaxLength(100)
            newSampleDespLineEdit.setClearButtonEnabled(True)


            newcomboBox = CheckableComboBox()
            newcomboBox.setMaximumSize(QtCore.QSize(290, 16777215))
            newcomboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
            font = QtGui.QFont()
            font.setFamily("Dubai")
            font.setPointSize(13)
            newcomboBox.setFont(font)
            newcomboBox.setObjectName(f"comboBox_{self.i}")
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT TestName FROM TestMaster ORDER BY TestName ASC")
            self.QryResult=c.fetchall()
            c.close()
            conn.close()
            self.QryFinal=[self.item[0] for self.item in self.QryResult]
            newcomboBox.addItems(self.QryFinal)

            for j in range(newcomboBox.count()):
                    item = newcomboBox.model().item(j, 0)
                    item.setCheckState(QtCore.Qt.CheckState.Unchecked)

            self.searchLineEdit.clear()
            self.comboBoxes.append(newcomboBox)
            hboxLayout.addWidget(newSampleNameLineEdit, stretch=1)
            hboxLayout.addSpacing(10)
            hboxLayout.addWidget(newSampleDespLineEdit, stretch=2)
            hboxLayout.addSpacing(10)
            hboxLayout.addWidget(newcomboBox, stretch=4)
            self.formLayout.addRow(hboxLayout)

            self.newRows.append(self.i)
            self.i=self.i+1
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoAddDt(self):
        try:
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:#984063; color:rgb(0, 0, 0); padding-bottom:7px;"
            self.nameLineEdit.setStyleSheet(style)
            self.MnoLineEdit.setStyleSheet(style)
            self.addressLineEdit.setStyleSheet(style)
            self.emailLineEdit.setStyleSheet(style)
            self.sampleNameLineEdit.setStyleSheet(style)
            regexEmail = r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$"
            name=self.nameLineEdit.text().strip()
            if not name or any(char.isdigit() for char in name):
                self.highlightError(self.nameLineEdit)
                self.highlightButton()
                return
            age=self.ageSpinBox.value() or ""
            age=''.join(str(age))
            gender=self.genderComboBox.currentText() or ""
            mno=self.MnoLineEdit.text().strip()
            if len(mno)!=10:
                self.highlightError(self.MnoLineEdit)
                self.highlightButton()
                return
            address=self.addressLineEdit.text()
            if not address or len(address) > 150:
                self.highlightError(self.addressLineEdit)
                self.highlightButton()
                return
            email=self.emailLineEdit.text().strip()
            if not bool(re.match(regexEmail, email)):
                self.highlightError(self.emailLineEdit)
                self.highlightButton()
                return
            sampleName=self.sampleNameLineEdit.text().strip()
            sampleDesp=self.sampleDespLineEdit.text().strip() or ""
            testApplied=self.comboBox.checked_items()
            if not sampleName or not sampleDesp or testApplied == None or testApplied == []:
                self.highlightError(self.sampleNameLineEdit)
                self.highlightButton()
                return
            samplesDictionary = {}
            samplesDictionary[sampleName]=[sampleDesp,'',testApplied]
            if not self.newRows == []:
                for k in range(1,len(self.newRows)+1):
                    sample_name = self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)).text()
                    sample_desp = self.findChild(QtWidgets.QLineEdit,"sampleDespLineEdit_"+str(k)).text() or ""
                    comboBox_values = self.findChild(QtWidgets.QComboBox,"comboBox_"+str(k)).checked_items()
                    if not self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)):
                        self.highlightError(self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)))
                        self.highlightButton()
                        return
                    if not self.findChild(QtWidgets.QLineEdit,"sampleDespLineEdit_"+str(k)):
                        self.highlightError(self.findChild(QtWidgets.QLineEdit,"sampleDespLineEdit_"+str(k)))
                        self.highlightButton()
                        return
                    if comboBox_values == None or comboBox_values == []:
                        self.highlightError(self.findChild(QtWidgets.QLineEdit,"sampleNameLineEdit_"+str(k)))
                        self.highlightButton()
                        return
                    samplesDictionary[sample_name] = [sample_desp,'',comboBox_values]
            dateToday=datetime.datetime.now().strftime("%Y-%m-%d")
            SName=''
            SDesp=''
            conn=create_connection()
            c=conn.cursor()
            try:
                queryForCus = "INSERT INTO  CustomerMaster(Date, Name,Age , Gender,MobileNo,Email, Address,EID,SID,PaymentType) VALUES (%s, %s, %s, %s, %s,%s, %s,%s, %s,%s)"
                c.execute(queryForCus, (dateToday,name,age,gender,mno,email,address,self.Eid," ","NA"))
                conn.commit()
                queryForId = "SELECT CID FROM CustomerMaster WHERE Name = %s and Age = %s and Gender = %s and MobileNo = %s and Email = %s and EID = %s ORDER BY CID DESC LIMIT 1"
                c.execute(queryForId,(name,age,gender,mno,email,self.Eid))
                retrievedCID=c.fetchone()
                sidLists=self.generate_sample_unique_id(retrievedCID[0],len(samplesDictionary))
                sidString=", ".join(sidLists)
                queryForSid = "UPDATE CustomerMaster SET SID = %s WHERE Name = %s and Age = %s and Gender = %s and MobileNo = %s and Email = %s and EID = %s and CID = %s "
                c.execute(queryForSid,(sidString,name,age,gender,mno,email,self.Eid,retrievedCID[0]))
                conn.commit()
                samplesTestDictionary={sidLists[i]: value for i,value in enumerate(samplesDictionary.values())}
                for key in samplesTestDictionary:
                    tidList=[]
                    value=samplesTestDictionary[key]
                    for item in value[2]:
                        queryForTid="SELECT TID FROM TestMaster WHERE TestName = %s"
                        c.execute(queryForTid,(item,))
                        retrievedTID=c.fetchone()
                        tidList.append(retrievedTID[0])
                    tidStr=", ".join(map(str, tidList))
                    samplesTestDictionary[key][2]=tidStr
                for (keys,values),nameKey in zip(samplesTestDictionary.items(),samplesDictionary):
                    SName=nameKey
                    SDesp=values[0]
                    queryForSamp="INSERT INTO SampleMaster(SID,SampleName,SampleDesp,Quantity,TID,CID,Status) VALUES(%s,%s,%s,%s,%s,%s,%s)"
                    c.execute(queryForSamp,(keys,nameKey, values[0], values[1], values[2],retrievedCID[0],"Failed",)) 
                    conn.commit()
                    c.execute("UPDATE SampleMaster SET AmountEstimated = %s WHERE SID = %s",('0.0',keys))
                    conn.commit()
                c.execute("UPDATE CustomerMaster SET AmountEstimated = %s WHERE CID = %s",('0.0',retrievedCID[0]))         
                log_db_operation(c,self.Eid,f"has enrolled a new customer with CID {retrievedCID[0]} as failed sample")
                conn.commit()
            except psycopg2.Error as e:
                print(e)
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.send_confirmation_email(email,SName,SDesp)
            self.gotoRec()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
          
    def generate_sample_unique_id(self,CustoId,SampNos):
        try:
            sample_id = 0
            sample_ids = []  
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            
            for i in range(SampNos):
                sample_id += 1
                padded_sample_id=str(sample_id).zfill(2)
                unique_sample_id = f"PAR-L/{current_date}/{CustoId}-{padded_sample_id}"
                sample_ids.append(unique_sample_id)
            return sample_ids
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def send_confirmation_email(self,to_address,Sample,Reason):      
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT Name, Phno, Email, Password FROM CompanyDetails ORDER BY ID DESC")
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            CName, CPhno, CEmail, CPassword = result
        else:
            CName, CPhno, CEmail, CPassword = '', '', '', ''

        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        msg = MIMEMultipart()
        msg['From'] = CEmail
        msg['To'] = to_address
        msg['Subject'] = 'Sample Received But Pending in Processing'

        html_content = f"""
                <html>
                <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        width: 100%;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #f9f9f9;
                    }}
                    .content {{
                        background-color: #ffffff;
                        padding: 20px;
                        border: 1px solid #dddddd;
                    }}
                    h1 {{
                        color: #333333;
                    }}
                    p {{
                        color: #666666;
                    }}
                </style>
                </head>
                <body>
                    <div class="container">
                        <div class="content">
                            <p>Dear Customer,</p>
                            <p>We are pleased to inform you that we have received your sample on <strong>{current_datetime}</strong>.</p>
                            <p>However, we regret to inform you that your sample {Sample} did not pass the initial stage of processing due to {Reason}. Kindly resend the sample as per the specified requirements for further processing.</p>
                            <p>For any inquiries or clarifications, please contact us at <strong>{CPhno}</strong>.</p>
                            <p>Thank you for your understanding and cooperation.</p>
                            <p>Best regards,</p>
                            <p>{CName}</p>
                        </div>
                    </div>
                </body>
                </html>
                """
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            if check_internet_connection() and self.smtp_server_conn is None:
                try:
                    self.smtp_server_conn = smtplib.SMTP('smtp.gmail.com',587)
                    self.smtp_server_conn.starttls()
                    self.smtp_server_conn.login(CEmail,CPassword)
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            elif check_internet_connection() and self.smtp_server_conn is not None:
                try:
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "No internet connection - Send Confirmation Manually")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

class mainLabApp(QtWidgets.QMainWindow,Lab_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainLabApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(Ename))
        self.roleLabel.setText(str(Erole))

        self.loadData()
                  
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.reloadButton.clicked.connect(self.gotoReload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
   
    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT SID,SampleName,TestResult FROM SampleMaster WHERE Status != 'Approved' ORDER BY SID DESC;"
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRow(tablerow, row)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRow(self, tablerow, row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)
            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)

            item2=QtWidgets.QTableWidgetItem(str(self.retrivelTests(str(row[0]))))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)

            item3=QtWidgets.QTableWidgetItem(str(row[2]))
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)

            modify_button_widget = self.ModifyButtonInCellWidget("✍",self.Eid,self.Ename,self.Erole,str(row[0]),tablerow)
            self.tableWidget.setCellWidget(tablerow, 4, modify_button_widget)

            self.tableWidget.update()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.loadData()
        self.tableWidget.blockSignals(False)

    def retrivelTests(self,SIDS):
        try:
            self.strTestsList=[]
            self.strId=SIDS
            if ', ' in self.strId:
                items = self.strId.split(', ') 
            else:
                items = [self.strId]
            conn=create_connection()
            c=conn.cursor()
            for item in items:
                try:
                    Qry1 ="SELECT TID FROM SampleMaster WHERE SID = %s"
                    c.execute(Qry1,(item,))
                    self.Qry1Result=c.fetchone()
                    tidLists=[int(x) for x in self.Qry1Result[0].split(',')]
                    testNameLists=[]
                    for val in tidLists:
                        Qry2="SELECT TestName FROM TestMaster WHERE TID = %s"
                        c.execute(Qry2,(val,))
                        self.Qry2Result=c.fetchone()
                        testNameLists.append(self.Qry2Result[0])
                    if len(testNameLists)>1:
                        self.val = ' ,'.join(testNameLists)
                        self.strTestsList.append(self.val)
                    else:
                        self.strTestsList.append(testNameLists[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.strTests=', '.join(self.strTestsList)
            return self.strTests
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSearch(self):
        try:
            
            searchData=self.searchLineEdit.text().strip()
            conn=create_connection()
            c=conn.cursor()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            if not searchData:
                self.gotoReload()
            else:
                query = "SELECT SID,SampleName,TestResult FROM SampleMaster WHERE SID LIKE %s AND Status != 'Approved'"
                c.execute(query, (f"%{searchData}%",))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def ModifyButtonInCellWidget(self,Text,Eid, Ename, Erole, Sid, row):
        button = QtWidgets.QPushButton(str(Text))
        font = QtGui.QFont()
        font.setFamily("Dubai") 
        font.setPointSize(12)
        font.setBold(True)
        button.setFont(font)
        button.setObjectName("cellModifyButton")
        
        def gotoEdit():
            test_data=self.tableWidget.item(row,2).text()
            test_results, final_results = retrivelResultsAndTestResults(Sid)
            if test_data in ["Plant","Animal","Bacteria","Fungus"]:
                enterValBigWindow = enterValBigApp(Eid,Ename, Erole, Sid,test_data,str(test_results),str(final_results))
                if not(enterValBigWindow.exec()) == QtWidgets.QDialog.rejected:
                    self.gotoReload()
            else:            
                enterValWindow = enterValApp(Eid,Ename, Erole, Sid,test_data,str(test_results))
                if not(enterValWindow.exec()) == QtWidgets.QDialog.rejected:
                    self.gotoReload()

        def retrivelResultsAndTestResults(Sid):
            try:
                conn = create_connection()
                c = conn.cursor()
                c.execute("SELECT TestResult, Result FROM SampleMaster WHERE SID = %s", (Sid,))
                result = c.fetchone()
                test_results = result[0] if result else ""
                final_results = result[1] if result else ""
                c.close()
                conn.close()
                return test_results, final_results
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                return None, None
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                return None, None

        button.clicked.connect(gotoEdit)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

class enterValBigApp(QtWidgets.QDialog, DraggableMixin,ValueEntryBig_Ui_Form):
    image_data1=None
    image_data2=None
    def __init__(self,Eid,Ename,Erole,Sid,test_data,result_data,final_data):
        super(enterValBigApp,self).__init__()
        self.setupUi(self)
        self.lst=[]
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.Sid=Sid
        self.test_data=test_data
        self.result_data=result_data
        self.final=final_data
        self.sampleIdValueLabel.setText(Sid)

        self.loadData()
        
        self.okButton.clicked.connect(self.gotoModDt)
        self.image1Button.clicked.connect(self.uploadImage1)
        self.image2Button.clicked.connect(self.uploadImage2)
        self.cancelButton.clicked.connect(self.gotoLab)
        self.okButton.setFocus()

    def uploadImage1(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if fileName:
            pixmap = QtGui.QPixmap(fileName)
            self.image1Label.setPixmap(pixmap)
            self.image1Label.setScaledContents(True)

            with open(fileName, 'rb') as file:
                self.image_data1 = file.read()

    def uploadImage2(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)")
        if fileName:
            pixmap = QtGui.QPixmap(fileName)
            self.image2Label.setPixmap(pixmap)
            self.image2Label.setScaledContents(True)

            with open(fileName, 'rb') as file:
                self.image_data2 = file.read()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoModDt()
        else:
            super(enterValBigApp, self).keyPressEvent(event)

    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def loadData(self):
        try:
            self.testNameLabel.setText(str(self.test_data))
            if self.result_data and self.result_data!='None':
                self.plainTextEdit.setPlainText(str(self.result_data)) 
            if self.result_data and self.final!='None':
                self.resultLineEdit.setText(str(self.final)) 
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoLab(self):
        self.reject()

    def gotoModDt(self):
        try:
            sqnc=self.plainTextEdit.toPlainText().strip()
            resl=self.resultLineEdit.text().strip()
            if not sqnc or sqnc=='' or not resl or  resl=='' or not self.image_data1:
                self.highlightButton()  
                return
            try:
                conn=create_connection()
                c=conn.cursor()
                query = "UPDATE SampleMaster SET TestResult = %s,Status = %s,Result=%s ,Img1 = %s,Img2=%s WHERE SID = %s"
                c.execute(query, (sqnc,"Tested",resl,psycopg2.Binary(self.image_data1),psycopg2.Binary(self.image_data2),self.Sid))
                log_db_operation(c,self.Eid,f"has uploaded Test result for {self.Sid}")
                conn.commit()
                c.close()
                conn.close()
                self.gotoLab()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

class enterValApp(QtWidgets.QDialog, DraggableMixin,ValueEntry_Ui_Form):
    def __init__(self,Eid,Ename,Erole,Sid,test_data,result_data):
        super(enterValApp,self).__init__()
        self.setupUi(self)
        self.lst=[]
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.Sid=Sid
        self.test_data=test_data
        self.result_data=result_data
        self.sampleIdValueLabel.setText(Sid)

        self.loadData()
        
        self.tableWidget.cellChanged.connect(self.gotoStoreDt)
        self.okButton.clicked.connect(self.gotoModDt)
        self.cancelButton.clicked.connect(self.gotoLab)
        self.okButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoModDt()
        else:
            super(enterValApp, self).keyPressEvent(event)

    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def loadData(self):
        try:
            items1 = self.test_data.split(' ,') if ' ,' in self.test_data else [self.test_data]
            if self.result_data and self.result_data not in ['None']:
                if ', ' in self.result_data:
                    items2 = self.result_data.split(', ')
                else:
                    items2 = [self.result_data]
            else:
                items2 = [''] * len(items1)
            self.tableWidget.blockSignals(True)
            self.tableWidget.setRowCount(len(items1))
            
            for tablerow, (item1, item2) in enumerate(zip(items1, items2)):
                cell0 = QtWidgets.QTableWidgetItem(str(item1))
                cell0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow, 0, cell0)

                cell1 = QtWidgets.QTableWidgetItem(str(item2))
                cell1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsEditable)
                self.tableWidget.setItem(tablerow, 1, cell1)
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoLab(self):
        self.reject()

    def gotoStoreDt(self,row,column):
        try:
            self.lst = []  
            for row in range(self.tableWidget.rowCount()):
                item_result = self.tableWidget.item(row, 1)
                if item_result is not None and item_result.text().strip():
                    self.lst.append(str(item_result.text().strip()))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoModDt(self):
        try:
            for row in range(self.tableWidget.rowCount()):
                item_result = self.tableWidget.item(row, 1)
                if item_result is None or not item_result.text().strip():
                    self.highlightButton()
                    return 
            
            if len(self.lst) == 1:
                tresult = str(self.lst[0])
            else:
                tresult = ', '.join(map(str, self.lst))
            if tresult == '':
                self.highlightButton()  
                return
            try:
                conn=create_connection()
                c=conn.cursor()
                query = "UPDATE SampleMaster SET TestResult = %s,Status = %s WHERE SID = %s"
                c.execute(query, (tresult,"Tested",self.Sid))
                log_db_operation(c,self.Eid,f"has uploaded Test result for {self.Sid}")
                conn.commit()
                c.close()
                conn.close()
                self.gotoLab()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
class ApproveButtonInCellWidget(QtWidgets.QWidget):
    def __init__(self,Text, Eid,Ename,Erole,Sid,parent=None):
        super().__init__(parent)
        self.Eid=Eid
        self.Ename=Ename
        self.Sid=Sid
        self.button = QtWidgets.QPushButton(str(Text))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(12)
        font.setBold(True)
        self.button.setFont(font)
        self.button.setObjectName("cellApproveButton")
        self.button.clicked.connect(lambda:self.gotoEdit(Ename,Erole,Sid))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def findParentTableWidget(self):
        parent = self.parent()
        while parent and not isinstance(parent, QtWidgets.QTableWidget):
            parent = parent.parent()
        return parent
    
    def gotoEdit(self,Ename,Erole,Sid):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "UPDATE SampleMaster SET Status = %s WHERE SID = %s"
            c.execute(query, ("Approved",Sid))
            log_db_operation(c,self.Eid,f"has approved the Test result for {self.Sid}")
            conn.commit()
            c.close()
            conn.close()

            tableWidget = self.findParentTableWidget()
            if tableWidget is None:
                raise ValueError("No parent QTableWidget found")
            
            row= tableWidget.indexAt(self.pos()).row()
            tableWidget.removeCellWidget(row,5)
            tableWidget.removeCellWidget(row,4)
            item4=QtWidgets.QTableWidgetItem("✔")
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            item4.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            tableWidget.setItem(row,4,item4)

            item5=QtWidgets.QTableWidgetItem("")
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            tableWidget.setItem(row,5,item5)
        except psycopg2.Error as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
class RejectButtonInCellWidget(QtWidgets.QWidget):
    def __init__(self,Text, Eid,Ename,Erole,Sid,parent=None):
        super().__init__(parent)
        self.Eid=Eid
        self.Ename=Ename
        self.Sid=Sid
        self.button = QtWidgets.QPushButton(str(Text))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(12)
        font.setBold(True)
        self.button.setFont(font)
        self.button.setObjectName("cellRejectButton")
        self.button.clicked.connect(lambda:self.gotoEdit(Ename,Erole,Sid))
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.button)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
 
    def findParentTableWidget(self):
        parent = self.parent()
        while parent and not isinstance(parent, QtWidgets.QTableWidget):
            parent = parent.parent()
        return parent
    
    def gotoEdit(self,Ename,Erole,Sid):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "UPDATE SampleMaster SET Status = %s WHERE SID = %s"
            c.execute(query, ("ReTest",Sid))
            log_db_operation(c,self.Eid,f"has rejected the Test result for {self.Sid}")
            conn.commit()
            c.close()
            conn.close()

            tableWidget = self.findParentTableWidget()
            if tableWidget is None:
                raise ValueError("No parent QTableWidget found")
            
            row= tableWidget.indexAt(self.pos()).row()
            tableWidget.removeCellWidget(row,5)
            tableWidget.removeCellWidget(row,4)
            item5=QtWidgets.QTableWidgetItem("✖")
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            item5.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            tableWidget.setItem(row,5,item5)

            item4=QtWidgets.QTableWidgetItem("")
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            tableWidget.setItem(row,4,item4)

        except psycopg2.Error as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

class ListViewInCellWidget(QtWidgets.QWidget):
    def __init__(self, Text, parent=None):
        super().__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        if ', ' in Text:
            items = Text.split(', ') 
        else:
            items = [Text]  
        
        self.labels = []
        for item in items:
            label = QtWidgets.QLabel(item)
            font = QtGui.QFont()
            font.setFamily("Dubai")
            font.setPointSize(12)
            label.setFont(font)
            label.setObjectName("listTest")
            label.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            label.setStyleSheet("padding:2px;")
            layout.addWidget(label)
            self.labels.append(label)

        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        
    def getText(self):
        return ', '.join([label.text() for label in self.labels])

class ComboBoxInCellWidget(QtWidgets.QWidget):
    def __init__(self,Cid,Erole,parent=None):
        super().__init__(parent)
        self.comboBoxCell = QtWidgets.QComboBox()
        font = QtGui.QFont()
        font.setFamily("Dubai") 
        font.setPointSize(12)
        self.comboBoxCell.setFont(font)
        self.comboBoxCell.setObjectName("cellComboBox")
        self.comboBoxCell.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        self.comboBoxCell.setAcceptDrops(False)
        self.comboBoxCell.setEditable(False)
        self.comboBoxCell.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
        self.comboBoxCell.setPlaceholderText("Select")

        self.comboBoxCell.addItems(['Cash','Credit Card','Debit Card','Net Banking','UPI','Not Paid'])
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.comboBoxCell)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        conn=create_connection()
        c=conn.cursor()
        c.execute("SELECT PaymentType FROM CustomerMaster WHERE CID = %s",(Cid,))
        self.res=c.fetchone()[0]
        c.close()
        conn.close()
        if self.res==None:
            self.comboBoxCell.setCurrentIndex(-1)
        elif self.res=='Cash':
            self.comboBoxCell.setCurrentIndex(0)
        elif self.res=='Credit Card':
            self.comboBoxCell.setCurrentIndex(1)
        elif self.res=='Debit Card':
            self.comboBoxCell.setCurrentIndex(2)
        elif self.res=='Net Banking':
            self.comboBoxCell.setCurrentIndex(3)
        elif self.res=='UPI':
            self.comboBoxCell.setCurrentIndex(4)
        else:
            self.comboBoxCell.setCurrentIndex(5)

        self.comboBoxCell.currentTextChanged.connect(lambda : self.gotoModify(Cid,Erole))
 
    def findParentTableWidget(self):
        parent = self.parent()
        while parent and not isinstance(parent, QtWidgets.QTableWidget):
            parent = parent.parent()
        return parent
            
    def gotoModify(self,Cid,Erole):
        try:
            conn=create_connection()
            c=conn.cursor()
            if self.comboBoxCell.currentText() in ['Cash','Credit Card','Debit Card','Net Banking','UPI']:
                pType=self.comboBoxCell.currentText()
                c.execute("UPDATE CustomerMaster SET PaymentType = %s WHERE CID = %s",(pType,Cid))
                tableWidget = self.findParentTableWidget()
                if tableWidget is None:
                    raise ValueError("No parent QTableWidget found")
                
                row= tableWidget.indexAt(self.pos()).row()
                tableWidget.removeCellWidget(row,11)
                if pType=='Cash':
                    item11=QtWidgets.QTableWidgetItem("Cash")
                if pType=='Credit Card':
                    item11=QtWidgets.QTableWidgetItem("Credit Card")
                if pType=='Debit Card':
                    item11=QtWidgets.QTableWidgetItem("Debit Card")
                if pType=='Net Banking':
                    item11=QtWidgets.QTableWidgetItem("Net Banking")
                if pType=='UPI':
                    item11=QtWidgets.QTableWidgetItem("UPI")
                item11.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                tableWidget.setItem(row,11,item11)

            else:
                c.execute("UPDATE CustomerMaster SET PaymentType = NULL WHERE CID = %s",(Cid,))
            conn.commit()
            c.close()
            conn.close()       
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
class CheckableComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super().__init__()
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        self.lineEdit().setPlaceholderText('Select Tests*')
        

        self.closeOnLineEditClick=False
        
        self.lineEdit().installEventFilter(self)

        self.view().viewport().installEventFilter(self)

        self.model().dataChanged.connect(self.checked_items)
        
    def eventFilter(self,widget,event):
        if widget==self.lineEdit():
            if event.type()==QtCore.QEvent.Type.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return super().eventFilter(widget,event)
        if widget == self.view().viewport():
            if event.type()==QtCore.QEvent.Type.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())
                if item: 
                    if item.checkState()==QtCore.Qt.CheckState.Checked:
                        item.setCheckState(QtCore.Qt.CheckState.Unchecked)
                    else:
                        item.setCheckState(QtCore.Qt.CheckState.Checked)
                return True
            return super().eventFilter(widget,event)
        return super().eventFilter(widget,event)

    def hidePopup(self):
        super().hidePopup()
        self.startTimer(100)

    def addItems(self,items,itemList=None):
        try:
            for index,text in enumerate(items):
                try:
                    data=itemList[index]
                except (TypeError,IndexError):
                    data=None
                self.addItem(text,data)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def addItem(self,text,userData=None):
        try:
            item = QtGui.QStandardItem()
            item.setText(text)
            if not userData is None:
                item.setData(userData)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
            item.setData(QtCore.Qt.CheckState.Unchecked,QtCore.Qt.ItemDataRole.CheckStateRole)
            self.model().appendRow(item)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def checked_items(self):
        try:
            text_container=[]
            for i in range(self.model().rowCount()):
                if self.model().item(i).checkState()==QtCore.Qt.CheckState.Checked:
                    text_container.append(self.model().item(i).text())
            if self.lineEdit():
                if text_container:
                    text_string = ', '.join(text_container)
                    self.lineEdit().setText(text_string)
                else:
                    self.lineEdit().clear()
                    self.lineEdit().setPlaceholderText('Select Tests*')
            return text_container
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
class mainTechManSamApp(QtWidgets.QMainWindow,TechManSam_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainTechManSamApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))

        self.loadData()
                  
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.viewTestsButton.clicked.connect(self.gotoTest)
        self.viewSalesButton.clicked.connect(self.gotoSales)
        self.reloadButton.clicked.connect(self.gotoReload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT SID,SampleName,TestResult,Status FROM SampleMaster ORDER BY SID DESC;"
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRows(tablerow, row)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRows(self,tablerow,row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)
            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)

            combinedStr1=self.retrivelTests(str(row[0]))
            list_widget2 = ListViewInCellWidget(combinedStr1)
            self.tableWidget.setCellWidget(tablerow, 2, list_widget2)

            item3=QtWidgets.QTableWidgetItem(str(row[2]))
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)

            if str(row[3])=='Approved':
                item4=QtWidgets.QTableWidgetItem("✔")
                item4.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                item4.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.tableWidget.setItem(tablerow,4,item4)

                item5=QtWidgets.QTableWidgetItem("")
                item5.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(tablerow,5,item5)

            else:
                approve_button_widget = ApproveButtonInCellWidget("✔",self.Eid,self.Ename,self.Erole,str(row[0]), parent=self.tableWidget)
                self.tableWidget.setCellWidget(tablerow, 4, approve_button_widget)

                reject_button_widget = RejectButtonInCellWidget("✖",self.Eid,self.Ename,self.Erole,str(row[0]), parent=self.tableWidget)
                self.tableWidget.setCellWidget(tablerow, 5, reject_button_widget)

            self.tableWidget.update()
            if combinedStr1 not in ['Fungus','Bacteria','Animal','Plant']:
                self.tableWidget.resizeRowToContents(tablerow)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)

    def retrivelTests(self,SIDS):
        try:
            self.strTestsList=[]
            self.strId=SIDS
            if ', ' in self.strId:
                items = self.strId.split(', ') 
            else:
                items = [self.strId]
            conn=create_connection()
            c=conn.cursor()
            for item in items:
                try:
                    Qry1 ="SELECT TID FROM SampleMaster WHERE SID = %s"
                    c.execute(Qry1,(item,))
                    self.Qry1Result=c.fetchone()
                    tidLists=[int(x) for x in self.Qry1Result[0].split(',')]
                    testNameLists=[]
                    for val in tidLists:
                        Qry2="SELECT TestName FROM TestMaster WHERE TID = %s"
                        c.execute(Qry2,(val,))
                        self.Qry2Result=c.fetchone()
                        testNameLists.append(self.Qry2Result[0])
                    if len(testNameLists)>1:
                        self.val = ' ,'.join(testNameLists)
                        self.strTestsList.append(self.val)
                    else:
                        self.strTestsList.append(testNameLists[0])
                except psycopg2.Error as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.strTests=', '.join(self.strTestsList)
            c.close()
            conn.close()
            return self.strTests
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            conn=create_connection()
            c=conn.cursor()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            if not searchData:
                self.gotoReload()
            else:
                query = "SELECT SID,SampleName,TestResult,Status FROM SampleMaster WHERE SID LIKE %s OR SampleName LIKE %s"
                c.execute(query, (f"%{searchData}%",f"%{searchData}%"))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRows(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoTest(self):
        TechmantestWindow=mainTechManTestApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(TechmantestWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoSales(self):
        TechmanSaleWindow=mainTechSaleApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(TechmanSaleWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainTechSaleApp(QtWidgets.QMainWindow,TechSale_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainTechSaleApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.reloadButton.clicked.connect(self.gotoReload)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.addItemButton.clicked.connect(self.gotoAddItem)
        self.importButton.clicked.connect(self.gotoImport)
        self.exportButton.clicked.connect(self.gotoExport)
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.tableWidget.cellChanged.connect(self.itemChanged)
        self.viewServicesButton.clicked.connect(self.gotoServices)
        self.templateButton.clicked.connect(self.gotoDownload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT Date,ItemCode,ItemName,HSN,SalePrice,PurchasePrice,StockQuantity,GSTIN,TaxRate,InclusiveOfTax,ExpDate,MfgDate,AdditionalInfo FROM ItemMaster ORDER BY Date DESC;"
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRows(tablerow, row)
            c.close()
            conn.close()
          
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRows(self,tablerow,row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)

            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)

            item2=QtWidgets.QTableWidgetItem(str(row[2]))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)

            item3=QtWidgets.QTableWidgetItem(str(row[3]))
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)

            item4=QtWidgets.QTableWidgetItem(f"₹ {str(row[4])}")
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,4,item4)

            item5=QtWidgets.QTableWidgetItem(f"₹ {str(row[5])}")
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,5,item5)

            item6=QtWidgets.QTableWidgetItem(str(row[6]))
            item6.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,6,item6)

            item7=QtWidgets.QTableWidgetItem(str(row[7]))
            item7.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,7,item7)

            item8=QtWidgets.QTableWidgetItem(str(row[8]))
            item8.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,8,item8)

            item9=QtWidgets.QTableWidgetItem(str(row[9]))
            item9.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,9,item9)

            item10=QtWidgets.QTableWidgetItem(str(row[10]))
            item10.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,10,item10)

            item11=QtWidgets.QTableWidgetItem(str(row[11]))
            item11.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,11,item11)

            item12=QtWidgets.QTableWidgetItem(str(row[12]))
            item12.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,12,item12)

            if int(row[6]) < 2:
                for col in range(13):
                    self.tableWidget.item(tablerow, col).setForeground(QtGui.QColor('red'))

            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def itemChanged(self, row,column):
        try:
            self.tableWidget.blockSignals(True)
            item_name = self.tableWidget.item(row, 3).text()
            if column == 2:
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")  
                new_itemname = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET ItemName = %s , Date = %s WHERE ItemCode = %s", (new_itemname,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has renamed Item name from {item_name} to {new_itemname}")
                conn.commit()
                c.close()
                conn.close()
            if column == 3:
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")  
                new_itemhsn = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET HSN = %s , Date = %s WHERE ItemCode = %s", (new_itemhsn,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has changed HSN for {item_name} to {new_itemhsn}")
                conn.commit()
                c.close()
                conn.close()

            if column == 4:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_saleprice = self.tableWidget.item(row,column).text()
                new_saleprice=''.join(re.findall(r'\d+\.%s\d*', new_saleprice))
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET SalePrice = %s , Date = %s WHERE ItemCode = %s", (float(new_saleprice),todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Sellig price for {item_name} to {new_saleprice}")
                conn.commit()
                c.close()
                conn.close()

            if column == 5:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_purchaseprice = self.tableWidget.item(row,column).text()
                new_purchaseprice=''.join(re.findall(r'\d+\.%s\d*', new_purchaseprice))
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET PurchasePrice = %s , Date = %s WHERE ItemCode = %s", (float(new_purchaseprice),todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Purchase price for {item_name} to {new_purchaseprice}")
                conn.commit()
                c.close()
                conn.close()
            
            if column == 6:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_stockqty = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET StockQuantity = %s , Date = %s WHERE ItemCode = %s", (new_stockqty,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Stock for {item_name} to {new_stockqty}")
                conn.commit()
                c.close()
                conn.close()

            if column == 7:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_gstin = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET GSTIN = %s , Date = %s WHERE ItemCode = %s", (str(new_gstin),todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated GSTIN for {item_name} to {new_gstin}")
                conn.commit()
                c.close()
                conn.close()

            if column == 8:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemtax = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET TaxRate = %s , Date = %s WHERE ItemCode = %s", (new_itemtax,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Tax rate for {item_name} to {new_itemtax}")
                conn.commit()
                c.close()
                conn.close()
                
            if column == 9:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemiot = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET InclusiveOfTax = %s , Date = %s WHERE ItemCode = %s", (new_itemiot,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Inclusive of tax for {item_name} to {new_itemiot}")
                conn.commit()
                c.close()
                conn.close()

            if column == 10:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemexp = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET ExpDate = %s , Date = %s WHERE ItemCode = %s", (new_itemexp,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Exp date for {item_name} to {new_itemexp}")
                conn.commit()
                c.close()
                conn.close()
            
            if column == 11:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemmfg = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET MfgDate = %s , Date = %s WHERE ItemCode = %s", (new_itemmfg,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Mfg for {item_name} to {new_itemmfg}")
                conn.commit()
                c.close()
                conn.close()

            if column == 12:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemaf = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET AdditionalInfo = %s , Date = %s WHERE ItemCode = %s", (new_itemaf,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Additional info for {item_name} to {new_itemaf}")
                conn.commit()
                c.close()
                conn.close()
            self.gotoReload()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoDownload(self):
        headers = ["Date", "Item Code", "Item Name", "HSN", "Sale Price", "Purchase Price","Stock Quantity","GSTIN","Tax Rate","Inclusive of Tax","Exp Date","Mfg Date","Additional Info"]
        df = pd.DataFrame(columns=headers)
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "CSV files (*.csv)")
        if save_path:
            if not save_path.endswith('.csv'):
                save_path += '.csv'
            df.to_csv(save_path, index=False)
            QtWidgets.QMessageBox.information(self, "Success", f"Template file saved to {save_path}")
        else:
            print("Export canceled by user.")

    def gotoImport(self):
        try:
            path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV or Excel Files (*.csv *.xls *.xlsx)')[0]
            if path.endswith('.csv'):
                self.all_data = pd.read_csv(path)
            elif path.endswith('.xls') or path.endswith('.xlsx'):
                self.all_data = pd.read_excel(path)
            else:
                return

            required_columns = {'adet', 'cdeeimot', 'aeeimmnt', 'hns', 'aceeilprs', 'acceehipprrsu','aciknoqstttuy','ginst','aaerttx','acefiilnostuvx','adeeptx','adefgmt'}
            if not required_columns.issubset(set(map(lambda x: ''.join(sorted(x.lower().replace(' ', ''))), self.all_data.columns))):
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid Format: Required columns are missing")
                return
            
            conn = create_connection()
            c = conn.cursor()
            for i in range(len(self.all_data.index)):
                raw_date = None
                formatted_date = None
                itemCode = None
                itemSale = None
                itemPurchase = None                
                for j in range(len(self.all_data.columns)):
                    column_name = ''.join(sorted(self.all_data.columns[j].lower().replace(' ', '')))
                    cell_value = self.all_data.iat[i, j]

                    if column_name == 'adet':  # Date column
                        raw_date = str(cell_value)
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        else:
                            formatted_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    if column_name == 'cdeeimot':  # Item Code column
                        itemCode = cell_value
                        c.execute("SELECT COUNT(*) FROM ItemMaster WHERE ItemCode = %s", (itemCode,))
                        count = c.fetchone()[0]
                        if count == 0:
                            c.execute("""
                                INSERT INTO ItemMaster (Date, ItemCode)
                                VALUES (%s,%s)
                            """, (str(formatted_date), str(itemCode)))
                            conn.commit()
                    if column_name == 'aeeimmnt':  # Item Name column
                        c.execute("SELECT ID FROM ItemMaster WHERE ItemCode = %s",(itemCode,))
                        rId,=c.fetchone()
                        c.execute("""
                                UPDATE ItemMaster
                                SET ItemName = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'hns':  # HSN column
                        c.execute("""
                                UPDATE ItemMaster
                                SET HSN = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'aceeilprs':  # Sale Price column
                        itemSale = float(re.findall(r'\d+\.?\d*', str(cell_value))[0]) if re.findall(r'\d+\.?\d*', str(cell_value)) else 0.0
                        c.execute("""
                                UPDATE ItemMaster
                                SET SalePrice = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (float(itemSale), itemCode,rId))
                    if column_name == 'acceehipprrsu':  # Purchase Price column
                        itemPurchase = float(re.findall(r'\d+\.?\d*', str(cell_value))[0]) if re.findall(r'\d+\.?\d*', str(cell_value)) else 0.0
                        c.execute("""
                                UPDATE ItemMaster
                                SET PurchasePrice = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (float(itemPurchase), itemCode,rId))
                    if column_name == 'aciknoqstttuy':  # Stock Quantity column
                        c.execute("""
                                UPDATE ItemMaster
                                SET StockQuantity = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (int(cell_value), itemCode,rId))
                    if column_name == 'ginst':  # GSTIN column
                        c.execute("""
                                UPDATE ItemMaster
                                SET GSTIN = %s
                                WHERE ItemCode = %s  AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'aaerttx':  # Tax Rate column
                        c.execute("""
                                UPDATE ItemMaster
                                SET TaxRate = %s
                                WHERE ItemCode = %s  AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'acefiilnostuvx':  # Inclusive of Tax column
                        c.execute("""
                                UPDATE ItemMaster
                                SET InclusiveOfTax = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'adeeptx':  # Exp Date column
                        raw_date = str(cell_value)
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        c.execute("""
                                UPDATE ItemMaster
                                SET ExpDate = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(formatted_date), itemCode,rId))
                    if column_name == 'adefgmt':  # Mfg Date column
                        raw_date = str(cell_value)
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        c.execute("""
                                UPDATE ItemMaster
                                SET MfgDate = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(formatted_date), itemCode,rId))
                    if column_name in ['aaaddfiiiilmnnnooortt', 'aaddfiiilnnoot']:  # Additional Info column
                        c.execute("""
                                UPDATE ItemMaster
                                SET AdditionalInfo = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))

                    c.execute("SELECT Name FROM EmployeeMaster WHERE EID = %s", (self.Eid,))
                    employeeName = c.fetchone()[0]  
                    dateTimeNow = datetime.datetime.now()
                    logEntry = """INSERT INTO Logs(Details) 
                        VALUES (%s)"""
                    
                    Detail = f"{dateTimeNow} - {employeeName} has imported new Items"
                    c.execute(logEntry, (Detail))

                    conn.commit()
            log_db_operation(c,self.Eid,f"has imported new Items")
            conn.commit()
            c.close()
            conn.close() 
            QtWidgets.QMessageBox.information(self, "Success", "File imported")
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoAddItem(self):
        AddItemWindow=AddItemApp(self.Eid,self.Ename,self.Erole)
        if not(AddItemWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                query = "SELECT Date,ItemCode,ItemName,HSN,SalePrice,PurchasePrice,StockQuantity,GSTIN,TaxRate,InclusiveOfTax,ExpDate,MfgDate,AdditionalInfo FROM ItemMaster WHERE Date LIKE %s or ItemName LIKE %s or ItemCode = %s or HSN LIKE %s"
                c.execute(query, (f"%{searchData}%",f"%{searchData}%",searchData,f"%{searchData}%"))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRows(tablerow, row)

            self.tableWidget.blockSignals(False)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoServices(self):
        TechManSamWindow=mainTechManSamApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(TechManSamWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainTechManTestApp(QtWidgets.QMainWindow,TechManTest_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainTechManTestApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.viewSamplesButton.clicked.connect(self.gotoSample)
        self.importButton.clicked.connect(self.gotoImport)
        self.exportButton.clicked.connect(self.gotoExport)
        self.newButton.clicked.connect(self.gotoNewTest)
        self.tableWidget.cellChanged.connect(self.itemChanged)
        self.reloadButton.clicked.connect(self.gotoReload)
        self.templateButton.clicked.connect(self.gotoDownload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
  
    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT RM.Date, TM.TID, TM.TestName, RM.Fee,TM.GSTIN,TM.TaxRate,TM.InclusiveOfTax FROM TestMaster TM INNER JOIN RateMaster RM ON TM.TID = RM.TID WHERE (RM.TID, RM.Date) IN (SELECT TID, MAX(Date) FROM RateMaster GROUP BY TID) ORDER BY TM.TID ASC;"
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRows(tablerow, row)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRows(self,tablerow,row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)
            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)
            item2=QtWidgets.QTableWidgetItem(str(row[2]))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)
            item3=QtWidgets.QTableWidgetItem(f"₹ {str(row[3])}")
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)
            item4=QtWidgets.QTableWidgetItem(str(row[4]))
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,4,item4)
            item5=QtWidgets.QTableWidgetItem(str(row[5]))
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,5,item5)
            item6=QtWidgets.QTableWidgetItem(str(row[6]))
            item6.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,6,item6)

            
            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoDownload(self):
        headers = ["Date", "Test Name", "Fee", "GSTIN", "Tax Rate", "Inclusive Of Tax"]
        df = pd.DataFrame(columns=headers)
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "CSV files (*.csv)")
        if save_path:
            if not save_path.endswith('.csv'):
                save_path += '.csv'
            df.to_csv(save_path, index=False)
            QtWidgets.QMessageBox.information(self, "Success", f"Template file saved to {save_path}")
        else:
            print("Export canceled by user.")

    def gotoImport(self):
        try:
            path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV or Excel Files (*.csv *.xls *.xlsx)')[0]
            if path.endswith('.csv'):
                self.all_data = pd.read_csv(path)
            elif path.endswith('.xls') or path.endswith('.xlsx'):
                self.all_data = pd.read_excel(path)
            else:
                return

            required_columns = {'adet', 'aeemnstt', 'eef', 'ginst', 'aaerttx', 'acefiilnostuvx'}
            if not required_columns.issubset(set(map(lambda x: ''.join(sorted(x.lower().replace(' ', ''))), self.all_data.columns))):
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid Format: Required columns are missing")
                return
            
            conn = create_connection()
            c = conn.cursor()
            for i in range(len(self.all_data.index)):
                raw_date=None
                parsed_date=None
                formatted_date=None
                tName=None
                fee=None
                for j in range(len(self.all_data.columns)):
                    column_name = ''.join(sorted(self.all_data.columns[j].lower().replace(' ', '')))
                    if column_name=='adet': #Date column
                        raw_date = str(self.all_data.iat[i,j])
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        else:
                            formatted_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    if column_name=='aeemnstt': #Test Name column
                        tName=str(self.all_data.iat[i,j])
                        c.execute("SELECT COUNT(*) FROM TestMaster WHERE TestName = %s", (tName,))
                        count = c.fetchone()[0]
                        if count == 0:
                            c.execute("INSERT INTO TestMaster(TestName) VALUES(%s)", (tName,))
                            conn.commit()                        
                    if column_name=='eef': #Fee column
                        cell_value = str(self.all_data.iat[i, j]) 
                        if cell_value:
                            fee = float(''.join(re.findall(r'\d+\.?\d*', cell_value) ) ) 
                        else:
                            fee = None 
                        c.execute("SELECT TID FROM TestMaster WHERE TestName = %s",(tName,))
                        rTid,=c.fetchone()
                        c.execute("SELECT COUNT(*) FROM RateMaster WHERE Date = %s AND TID = %s", (formatted_date, rTid))
                        count = c.fetchone()[0]
                        if count == 0:
                            c.execute("INSERT INTO RateMaster(Date, TID, Fee) VALUES(%s, %s, %s)", (str(formatted_date), rTid, fee))
                        else:
                            c.execute("UPDATE RateMaster SET Fee = %s WHERE Date = %s AND TID = %s", (fee, str(formatted_date), rTid))
                        conn.commit()
                    if column_name=='ginst': #GSTIN column
                        c.execute("UPDATE TestMaster SET GSTIN = %s WHERE TID = %s AND TestName = %s", (str(self.all_data.iat[i, j]),rTid,tName))
                        conn.commit()
                    if column_name=='aaerttx': #Tax Rate column
                        c.execute("UPDATE TestMaster SET TaxRate = %s WHERE TID = %s AND TestName = %s", (str(self.all_data.iat[i, j]),rTid,tName))
                        conn.commit()    
                    if column_name=='acefiilnostuvx': #Inclusive Of Tax column
                        c.execute("UPDATE TestMaster SET InclusiveOfTax = %s WHERE TID = %s AND TestName = %s", (str(self.all_data.iat[i, j]),rTid,tName))
                        conn.commit()  

            log_db_operation(c,self.Eid,f"has imported new Tests")
            conn.commit()
            c.close()
            conn.close()
            QtWidgets.QMessageBox.information(self, "Success", "File imported")
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.loadData()
        self.tableWidget.blockSignals(False)

    def itemChanged(self, row,column):
        try:
            self.tableWidget.blockSignals(True)
            test_name = self.tableWidget.item(row, 2).text()
            if column == 3:  
                new_fee = self.tableWidget.item(row,column).text()
                new_fee=''.join(re.findall(r'\d+\.?\d*', new_fee))
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor()

                c.execute("SELECT COUNT(*) FROM RateMaster WHERE Date = %s AND TID = %s", (todayDate, test_id))
                count = c.fetchone()[0]

                if count > 0:  
                    c.execute("UPDATE RateMaster SET Fee = %s WHERE Date = %s AND TID = %s", (float(new_fee), todayDate, test_id))
                else:  
                    c.execute("INSERT INTO RateMaster (Date, TID, Fee) VALUES (%s, %s, %s)", (todayDate, test_id, float(new_fee)))
                log_db_operation(c,self.Eid,f"has updated fee for {test_name} to {float(new_fee)}")
                conn.commit()
                c.close()
                conn.close()

            if column == 4:  
                new_gstin = self.tableWidget.item(row,column).text()
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE TestMaster SET GSTIN = %s WHERE TID = %s", (str(new_gstin),test_id))
                log_db_operation(c,self.Eid,f"has updated GSTIN for {test_name} to {str(new_gstin)}")
                conn.commit()
                c.close()
                conn.close()

            if column == 5:  
                new_taxrate = self.tableWidget.item(row,column).text()
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE TestMaster SET TaxRate = %s WHERE TID = %s", (new_taxrate,test_id))
                log_db_operation(c,self.Eid,f"has updated TaxRate for {test_name} to {new_taxrate}")
                conn.commit()
                c.close()
                conn.close()

            if column == 6:  
                new_iot = self.tableWidget.item(row,column).text()
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE TestMaster SET InclusiveOfTax = %s WHERE TID = %s", (new_iot,test_id))
                log_db_operation(c,self.Eid,f"has updated InclusiveOfTax for {test_name} to {new_iot}")
                conn.commit()
                c.close()
                conn.close()
            self.tableWidget.blockSignals(False)
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSearch(self):
        try:
            
            searchData=self.searchLineEdit.text().strip()
            
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                query = """
                        SELECT RM.Date, TM.TID, TM.TestName, RM.Fee,TM.GSTIN,TM.TaxRate,TM.InclusiveOfTax
                        FROM TestMaster TM
                        INNER JOIN RateMaster RM ON TM.TID = RM.TID
                        WHERE (RM.TID, RM.Date) IN (
                            SELECT TID, MAX(Date)
                            FROM RateMaster
                            GROUP BY TID
                        ) AND TM.TestName LIKE %s
                        ORDER BY TM.TID ASC
                        """
                c.execute(query, (f"%{searchData}%",))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRows(tablerow, row)

            self.tableWidget.blockSignals(False)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSample(self):
        TechmansampleWindow=mainTechManSamApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(TechmansampleWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoNewTest(self):
        newTestWindow=newTestApp(self.Eid,self.Ename,self.Erole)
        if not(newTestWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class newTestApp(QtWidgets.QDialog, DraggableMixin,NewTest_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(newTestApp,self).__init__()
        self.setupUi(self)
        self.Ename=Ename
        self.Eid=Eid
        self.Erole=Erole
        self.okButton.clicked.connect(self.gotoModDt)
        self.cancelButton.clicked.connect(self.gotoTechTest)
        self.okButton.setFocus()
        self.inclusiveOfTaxComboBox.currentTextChanged.connect(self.gotoDisableTaxRate)

    def gotoDisableTaxRate(self):
        if self.inclusiveOfTaxComboBox.currentText()=="No":
            self.newTestTaxRateLineEdit.setDisabled(True)
            self.newTestTaxRateLineEdit.clear()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoModDt()
        else:
            super(newTestApp, self).keyPressEvent(event)

    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)
    
    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoTechTest(self):
        self.reject()

    def gotoModDt(self):
        try:
            self.testName=self.newTestNameLineEdit.text().strip()
            self.testFee=self.newTestFeeLineEdit.text().strip()
            self.testGSTIN=self.newTestGSTINeLineEdit.text().strip() or ""
            self.testTax=self.newTestTaxRateLineEdit.text().strip() or ""
            selected_option = self.inclusiveOfTaxComboBox.currentText()
            self.testInclusiveOfTax = selected_option if selected_option != "Select" else ""
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:#984063; color:rgb(0, 0, 0); padding-bottom:7px;"
            self.newTestNameLineEdit.setStyleSheet(style)
            self.newTestFeeLineEdit.setStyleSheet(style)

            if not self.testName or any(char.isdigit() for char in self.testName):
                self.highlightError(self.newTestNameLineEdit)
                self.highlightButton()
                return
            if not self.testFee or self.testFee.isalpha():
                self.highlightError(self.newTestFeeLineEdit)
                self.highlightButton()
                return

            self.feeDate=datetime.datetime.now().strftime("%Y-%m-%d")
            try:
                conn=create_connection()
                c=conn.cursor()
                query1 = "INSERT INTO TestMaster(TestName,GSTIN,TaxRate,InclusiveOfTax) VALUES(%s,%s,%s,%s);"
                c.execute(query1, (self.testName,str(self.testGSTIN),self.testTax,self.testInclusiveOfTax))
                log_db_operation(c,self.Eid,f"has added new Test {self.testName}")
                conn.commit()
                query2 = "SELECT TID FROM TestMaster WHERE TestName = %s;"
                c.execute(query2, (self.testName,))
                retrievedTid = c.fetchone()[0]
                query3 = "INSERT INTO RateMaster VALUES(%s,%s,%s);"
                c.execute(query3, (self.feeDate,retrievedTid,self.testFee))
                conn.commit()
                c.close()
                conn.close()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoTechTest()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
class mainAccApp(QtWidgets.QMainWindow,AccManService_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAccApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.roleLabel.setText(str(self.Erole))
        self.nameLabel.setText(str(self.Ename))
        
        self.executor = ThreadPoolExecutor(max_workers=10)

        self.populate_dates()
        self.loadData()
         
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.debounce_timer = QtCore.QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_combobox_change)
        self.yearComboBox.currentTextChanged.connect(lambda: self.debounce_selection("year"))
        self.monthComboBox.currentTextChanged.connect(lambda: self.debounce_selection("month"))
        self.dailyComboBox.currentTextChanged.connect(lambda: self.debounce_selection("daily"))
        self.viewSalesButton.clicked.connect(self.gotoSales)
        self.reloadButton.clicked.connect(self.gotoReload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
 
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)
        self.axes.cla()
        self.canvas.draw()
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,'','',''))

    def debounce_selection(self, combo_type):
        self.selected_combo_type = combo_type
        self.debounce_timer.start(5)

    def on_combobox_change(self):
        if self.selected_combo_type == "year":
            self.gotoModChartYear(self.yearComboBox.currentText())
        elif self.selected_combo_type == "month":
            self.gotoModChartMonth(self.monthComboBox.currentText())
        elif self.selected_combo_type == "daily":
            if self.monthComboBox.currentText() == "" or self.monthComboBox.currentText() == "Select":
                    QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select a month before choosing a day.")
            else:
                self.gotoModChartDaily(self.monthComboBox.currentText(), self.dailyComboBox.currentText())

    def populate_dates(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT Date FROM CustomerMaster")
            self.alldates = c.fetchall()
            c.execute("SELECT TestName FROM TestMaster")
            self.alltests = c.fetchall()
            c.close()
            conn.close()
            self.years = sorted({date_tuple[0][:4] for date_tuple in self.alldates if date_tuple[0]}, reverse=True)
            self.manyYears = sorted({date_tuple[0][:4] for date_tuple in self.alldates if date_tuple[0]})
            self.months = sorted({date_tuple[0][5:7] for date_tuple in self.alldates if date_tuple[0]})
            self.dates = sorted({date_tuple[0][8:10] for date_tuple in self.alldates if date_tuple[0]})
            self.tests = sorted({test_tuple[0] for test_tuple in self.alltests if test_tuple[0]})

            self.monthComboBox.addItems(self.years)
            self.years = [int(x) for x in self.years]
            self.year_groups = self.group_years(self.manyYears)
            if self.year_groups:
                self.yearComboBox.addItems(self.year_groups)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def group_years(self, years):
        try:
            grouped_years = []
            while years:
                group = []
                min_year = int(years[0])
                for i in range(min_year, min_year + 7):
                    if str(i) in years:
                        years.remove(str(i))
                    group.append(str(i))
                if len(group) > 1:
                    formatted_group = f"{min_year}-{group[-1]}"
                else:
                    formatted_group = group[0] 
                grouped_years.append(formatted_group)
            return grouped_years
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def loadData(self):
        try:
            self.axes.cla()
            self.canvas.draw()
            self.yearComboBox.blockSignals(True)
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.monthComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            conn=create_connection()
            c=conn.cursor()
            query = """
                SELECT sm.SID, sm.AmountEstimated 
                FROM SampleMaster sm
                INNER JOIN CustomerMaster cm ON cm.SID LIKE '%' || sm.SID || '%'
                WHERE cm.PaymentType != 'Not Paid'
                ORDER BY sm.SID DESC;
            """
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRows(tablerow, row)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
 
    def populateRows(self,tablerow,row):
        try:
            item0 = QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, 0, item0)

            combinedStr1 = self.retrivelTests(str(row[0]))
            list_widget1 = ListViewInCellWidget(combinedStr1)
            self.tableWidget.setCellWidget(tablerow, 1, list_widget1)

            item2 = QtWidgets.QTableWidgetItem(f"₹ {str(row[1])}")
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, 2, item2)

            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoSales(self):
        AccSaleWindow=mainAccSalesOrdersApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AccSaleWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def update_chart(self):
        try:
            self.yearComboBox.blockSignals(True)
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.monthComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)

            self.axes.cla()
            self.canvas.draw()

            yearly = self.yearComboBox.currentText()
            monthly = self.monthComboBox.currentText()
            daily = self.dailyComboBox.currentText()

            if yearly:
                self.executor.submit(self.gotoModChartYear, yearly)
            if monthly and not daily:
                self.executor.submit(self.gotoModChartMonth, monthly)
            if monthly and daily:
                self.executor.submit(self.gotoModChartDaily, monthly,daily)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def get_year_range(self,group_year):
        try:
            if not group_year or "-" not in group_year:
                return [] 

            start_year, end_year = group_year.split("-")
            start_year = int(start_year)
            end_year = int(end_year)

            year_range = list(range(start_year, end_year + 1))
            return year_range
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoModChartYear(self,value):
        self.executor.submit(self.update_chart_year, value)

    def update_chart_year(self, value):
        try:
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.monthComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            x = [0] * 7
            y = self.get_year_range(value)
            conn = create_connection()
            c = conn.cursor()
            for year in self.years:
                if year in y:
                    val = f"{year}-"
                    c.execute("SELECT AmountEstimated FROM CustomerMaster WHERE SID LIKE %s AND PaymentType != 'Not Paid'", (f"%{val}%",))
                    fees = c.fetchall()
                    fees_list = [item[0] for item in fees]
                    count = sum(fees_list)
                    month_index = y.index(year)
                    x[month_index] = count
            y=[str(year) for year in y]
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel="Year", ylabel="Total Amount")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoModChartMonth(self, value):
        self.executor.submit(self.update_chart_month, value)

    def update_chart_month(self, value):
        try:
            self.yearComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            x = [0] * 12
            y = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_noTonames = {
                '01': 'Jan',
                '02': 'Feb',
                '03': 'Mar',
                '04': 'Apr',
                '05': 'May',
                '06': 'Jun',
                '07': 'Jul',
                '08': 'Aug',
                '09': 'Sep',
                '10': 'Oct',
                '11': 'Nov',
                '12': 'Dec'
            }
            conn = create_connection()
            c = conn.cursor()
            for month in self.months:
                val = f"{value}-{month}"
                c.execute("SELECT AmountEstimated FROM CustomerMaster WHERE SID LIKE %s AND PaymentType != 'Not Paid'", (f"%{val}%",))
                fees = c.fetchall()
                fees_list = [item[0] for item in fees]
                count = sum(fees_list)
                month_index = y.index(month_noTonames.get(month))
                x[month_index] = count
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel="Month", ylabel="Total Amount")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_plot(self, labels, values, xlabel, ylabel):
        try:
            self.axes.cla()
            self.canvas.draw()
            self.axes.plot(labels, values, marker='o', linestyle='-',color='#26648E')
            self.axes.set_facecolor('#E5ECF6')
            self.axes.tick_params(axis='x', rotation=45)
            self.axes.set_xlabel(xlabel)
            self.axes.set_ylabel(ylabel)
            self.fig.subplots_adjust(bottom=0.239)
            self.canvas.draw()
            self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,labels,xlabel,ylabel))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def hover(self, event,labels,xlbl,ylbl):
        try:
            if labels=='' or xlbl=='' or ylbl=='':
                self.axes.set_title('')
            elif event.inaxes == self.axes:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    rounded_x = round(x)
                    if 0 <= rounded_x < len(labels):
                        xlabel = labels[rounded_x]
                    else:
                        rounded_x = max(0, min(len(labels) - 1, int(x)))
                        xlabel = labels[rounded_x]
                    self.axes.set_title(f'{xlbl} : {xlabel}  {ylbl} : {y:.0f}')
                else:
                    self.axes.set_title('')
            else:
                self.axes.set_title('')
            self.fig.canvas.draw()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
             
    def gotoModChartDaily(self, yearValue,monthValue):
        self.executor.submit(self.update_chart_daily, yearValue,monthValue)

    def update_chart_daily(self, yearValue,monthValue):
        try:
            self.yearComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            month_namesTonum = {
                'January': '01',
                'February': '02',
                'March': '03',
                'April': '04',
                'May': '05',
                'June': '06',
                'July': '07',
                'August': '08',
                'September': '09',
                'October': '10',
                'November': '11',
                'December': '12'
            }
            value = month_namesTonum.get(monthValue)
            yearMonthValue = f"{yearValue}-{value}"

            days_in_month = {
                '01': 31, '03': 31, '05': 31, '07': 31, '08': 31, '10': 31, '12': 31,
                '04': 30, '06': 30, '09': 30, '11': 30,
                '02': 29 if self.checkLeapYear(int(yearValue)) else 28
            }
            days = days_in_month[value]
            x = [0] * days
            y = [str(day) for day in range(1, days + 1)]
            conn = create_connection()
            c = conn.cursor()
            for day in y:
                val = f"{yearMonthValue}-{day.zfill(2)}"
                c.execute("SELECT AmountEstimated FROM CustomerMaster WHERE SID LIKE %s AND PaymentType != 'Not Paid'", (f"%{val}%",))
                fees = c.fetchall()
                fees_list = [item[0] for item in fees]
                count = sum(fees_list)
                day_index = y.index(day)
                x[day_index] = count

            c.close()
            conn.close()
            self.update_plot(y, x,xlabel="Day", ylabel="Total Amount")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def checkLeapYear(self,year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def retrivelTests(self, SIDS):
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT TID FROM SampleMaster WHERE SID = %s", (SIDS,))
            Qry1Result = c.fetchone()
            if Qry1Result:
                tidLists = [int(x) for x in Qry1Result[0].split(',')]
                testNameLists = []
                for val in tidLists:
                    c.execute("SELECT TestName FROM TestMaster WHERE TID = %s", (val,))
                    Qry2Result = c.fetchone()
                    if Qry2Result:
                        testNameLists.append(Qry2Result[0])
                c.close()
                conn.close()
                return ' ,'.join(testNameLists)
            c.close()
            conn.close()
            return ""
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSearch(self):
        try:
            searchData = self.searchLineEdit.text().strip()
            conn=create_connection()
            c=conn.cursor()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            if not searchData:
                self.gotoReload()
            elif re.match(r"^([A-Za-z]+)$", searchData):
                c.execute("SELECT TID FROM TestMaster WHERE TestName LIKE %s", (f"%{searchData}%",))
                tid_result = c.fetchone()
                if tid_result:
                    tid = tid_result[0]
                    c.execute("""
                              SELECT sm.SID, sm.AmountEstimated 
                                FROM SampleMaster sm
                                INNER JOIN CustomerMaster cm ON cm.SID LIKE '%%' || sm.SID || '%%'
                                WHERE cm.PaymentType != 'Not Paid' AND sm.TID LIKE %s""", (f"%{tid}%",))
                    results = c.fetchall()
                    if results:
                        self.tableWidget.setRowCount(len(results))
                        for row, (sid, fee) in enumerate(results):
                            item0 = QtWidgets.QTableWidgetItem(str(sid))
                            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                            self.tableWidget.setItem(row, 0, item0)

                            combinedStr1 = self.retrivelTests(str(sid))
                            list_widget1 = ListViewInCellWidget(combinedStr1)
                            self.tableWidget.setCellWidget(row, 1, list_widget1)

                            item2 = QtWidgets.QTableWidgetItem(f"₹ {str(fee)}")
                            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                            self.tableWidget.setItem(row, 2, item2)

                            self.tableWidget.update()
                            self.tableWidget.resizeRowToContents(row)
                    else:
                        self.tableWidget.setRowCount(0)
                else:
                    self.tableWidget.setRowCount(0)
            else:
                c.execute("""
                          SELECT sm.SID, sm.AmountEstimated 
                            FROM SampleMaster sm
                            INNER JOIN CustomerMaster cm ON cm.SID LIKE '%%' || sm.SID || '%%'
                            WHERE cm.PaymentType != 'Not Paid' AND sm.SID LIKE %s""", (f"%{searchData}%",))
                results = c.fetchall()
                if results:
                    self.tableWidget.setRowCount(len(results))
                    for row, (sid, fee) in enumerate(results):
                        item0 = QtWidgets.QTableWidgetItem(str(sid))
                        item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                        self.tableWidget.setItem(row, 0, item0)

                        combinedStr1 = self.retrivelTests(str(sid))
                        list_widget1 = ListViewInCellWidget(combinedStr1)
                        self.tableWidget.setCellWidget(row, 1, list_widget1)

                        item2 = QtWidgets.QTableWidgetItem(f"₹ {str(fee)}")
                        item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                        self.tableWidget.setItem(row, 2, item2)

                        self.tableWidget.update()
                        self.tableWidget.resizeRowToContents(row)
                else:
                    self.tableWidget.setRowCount(0)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainAccSalesOrdersApp(QtWidgets.QMainWindow,AccSalesOrders_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAccSalesOrdersApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.reloadButton.clicked.connect(self.gotoReload)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.viewServicesButton.clicked.connect(self.gotoServices)
        self.purchasesButton.clicked.connect(self.gotoPurchase)
        self.analysisButton.clicked.connect(self.gotoAnalysis)
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            query = """
                SELECT OrderNo, OrderDate, OrderTime, Party, Email,ContactNo,BillingAddress, State, Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                FROM SalesMaster
                ORDER BY ID DESC;
                """
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRow(tablerow, row)
            c.close()
            conn.close()
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRow(self,tablerow,row):
        for col in range(21):
            if col in {17, 18, 19,20}:
                text = f"₹ {row[col]}"
            elif col == 16:
                text = f"{row[col]} %"
            else:
                cell_text = str(row[col])
                if ', ' in cell_text:
                    item = ListViewInCellWidget(cell_text)
                    self.tableWidget.setCellWidget(tablerow, col, item)
                    continue
                else:
                    text = cell_text
            
            item = QtWidgets.QTableWidgetItem(text)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, col, item)
            self.tableWidget.resizeRowToContents(tablerow)
            self.tableWidget.update()

    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                parameters = (
                        f"%{searchData}%", f"%{searchData}%", 
                        searchData, f"%{searchData}%", searchData, 
                        searchData, f"%{searchData}%", f"%{searchData}%", 
                        f"%{searchData}%", f"%{searchData}%", f"%{searchData}%", 
                        searchData, searchData, searchData, 
                        searchData, searchData,searchData, searchData,searchData
                    )

                query = """
                        SELECT OrderNo,OrderDate, OrderTime,  Party,Email,ContactNo, BillingAddress,State ,Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                        FROM SalesMaster 
                        WHERE OrderDate LIKE %s 
                        OR Party LIKE %s 
                        OR OrderNo::text = %s 
                        OR BillingAddress LIKE %s 
                        OR OrderTime = %s 
                        OR State = %s 
                        OR Items LIKE %s 
                        OR HSNCode LIKE %s 
                        OR Qty LIKE %s 
                        OR Price LIKE %s 
                        OR Tax = %s 
                        OR TaxAmount = %s 
                        OR Total = %s 
                        OR PaymentType = %s 
                        OR Discount::text = %s 
                        OR TotalAmount::text = %s 
                        OR AdvAmount::text = %s 
                        OR TotalBalance::text = %s
                        OR CurrentBalance::text = %s
                        """
                c.execute(query, parameters)
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoServices(self):
        AccService=mainAccApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AccService)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()
         
    def gotoPurchase(self):
        AccPurchase=mainAccPurchaseOrdersApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AccPurchase)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoAnalysis(self):
        AccAnalyse=mainAccSaleAnalyseApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AccAnalyse)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainAccPurchaseOrdersApp(QtWidgets.QMainWindow,AccPurchaseOrders_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAccPurchaseOrdersApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.reloadButton.clicked.connect(self.gotoReload)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.salesButton.clicked.connect(self.gotoSales)
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            query = """
                SELECT OrderNo, OrderDate, OrderTime, Party, Email,ContactNo, BillingAddress, State, Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                FROM PurchaseMaster
                ORDER BY ID DESC;
                """
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRow(tablerow, row)
            c.close()
            conn.close()
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRow(self,tablerow,row):
        for col in range(21):
            if col in {17, 18, 19,20}:
                text = f"₹ {row[col]}"
            elif col == 16:
                text = f"{row[col]} %"
            else:
                cell_text = str(row[col])
                if ', ' in cell_text:
                    item = ListViewInCellWidget(cell_text)
                    self.tableWidget.setCellWidget(tablerow, col, item)
                    continue
                else:
                    text = cell_text
            
            item = QtWidgets.QTableWidgetItem(text)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, col, item)
            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)

    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                parameters = (
                        f"%{searchData}%", f"%{searchData}%", 
                        searchData, f"%{searchData}%", searchData, 
                        searchData, f"%{searchData}%", f"%{searchData}%", 
                        f"%{searchData}%", f"%{searchData}%", f"%{searchData}%", 
                        searchData, searchData, searchData, 
                        searchData, searchData,searchData, searchData,searchData
                    )

                query = """
                        SELECT OrderNo,OrderDate, OrderTime,  Party,Email,ContactNo, BillingAddress,State ,Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                        FROM PurchaseMaster 
                        WHERE OrderDate LIKE %s 
                        OR Party LIKE %s 
                        OR OrderNo::text = %s 
                        OR BillingAddress LIKE %s 
                        OR OrderTime = %s 
                        OR State = %s 
                        OR Items LIKE %s 
                        OR HSNCode LIKE %s 
                        OR Qty LIKE %s 
                        OR Price LIKE %s 
                        OR Tax = %s 
                        OR TaxAmount = %s 
                        OR Total = %s 
                        OR PaymentType = %s 
                        OR Discount::text = %s 
                        OR TotalAmount::text = %s 
                        OR AdvAmount::text = %s 
                        OR TotalBalance::text = %s
                        OR CurrentBalance::text = %s
                        """
                c.execute(query, parameters)
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoSales(self):
        AccWindow=mainAccSalesOrdersApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AccWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainAccSaleAnalyseApp(QtWidgets.QMainWindow,AccSaleAnalysis_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAccSaleAnalyseApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))

        self.executor = ThreadPoolExecutor(max_workers=10)
         
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.debounce_timer = QtCore.QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_combobox_change)

        self.yearComboBox.currentTextChanged.connect(lambda: self.debounce_selection("year"))
        self.monthComboBox.currentTextChanged.connect(lambda: self.debounce_selection("month"))
        self.dailyComboBox.currentTextChanged.connect(lambda: self.debounce_selection("daily"))
        self.categoryComboBox.currentTextChanged.connect(self.update_chart)
        self.salesButton.clicked.connect(self.gotoSales)

        self.itemComboBox = None
        self.reloadButton.clicked.connect(self.gotoReload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

        self.fetch_dates_and_items()
        

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def gotoReload(self):
        self.categoryComboBox.blockSignals(True)
        self.yearComboBox.blockSignals(True)
        self.monthComboBox.blockSignals(True)
        self.dailyComboBox.blockSignals(True)
        self.categoryComboBox.setCurrentIndex(-1)
        self.yearComboBox.setCurrentIndex(-1)
        self.monthComboBox.setCurrentIndex(-1)
        self.dailyComboBox.setCurrentIndex(-1)
        self.categoryComboBox.blockSignals(False)
        self.monthComboBox.blockSignals(False)
        self.yearComboBox.blockSignals(False)
        self.dailyComboBox.blockSignals(False)
        if self.itemComboBox:
            self.horizontalLayout_2.removeWidget(self.itemComboBox)
            self.itemComboBox.deleteLater()
            self.itemComboBox = None
        self.axes.cla()
        self.canvas.draw()
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,'','',''))

    def gotoSales(self):
        AccSaleWindow=mainAccSalesOrdersApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AccSaleWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def debounce_selection(self, combo_type):
        self.selected_combo_type = combo_type
        self.debounce_timer.start(100)

    def on_combobox_change(self):
        try:
            if self.selected_combo_type == "year":
                self.gotoModChartYear(self.yearComboBox.currentText())
            elif self.selected_combo_type == "month":
                self.gotoModChartMonth(self.monthComboBox.currentText())
            elif self.selected_combo_type == "daily":
                if self.monthComboBox.currentText() == "" or self.monthComboBox.currentText() == "Select":
                    QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select a month before choosing a day.")
                else:
                    self.gotoModChartDaily(self.monthComboBox.currentText(), self.dailyComboBox.currentText())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def fetch_dates_and_items(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT OrderDate FROM SalesMaster")
            sales_dates = [record[0] for record in c.fetchall()]

            c.execute("SELECT OrderDate FROM PurchaseMaster")
            purchases_dates = [record[0] for record in c.fetchall()]

            self.dates_by_category = {
                "Sales": sales_dates,
                "Purchases": purchases_dates
            }

            c.execute("SELECT ItemName FROM ItemMaster")
            self.items = [record[0] for record in c.fetchall()]

            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def group_years(self, years):
        try:
            grouped_years = []
            while years:
                group = []
                min_year = int(years[0])
                for i in range(min_year, min_year + 7):
                    if str(i) in years:
                        years.remove(str(i))
                    group.append(str(i))
                if len(group) > 1:
                    formatted_group = f"{min_year}-{group[-1]}"
                else:
                    formatted_group = group[0] 
                grouped_years.append(formatted_group)
            return grouped_years
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_chart(self):
        try:
            category = self.categoryComboBox.currentText()
            self.yearComboBox.blockSignals(True)
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.yearComboBox.clear()
            self.monthComboBox.setCurrentIndex(-1)
            self.monthComboBox.clear()
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)

            self.axes.cla()
            self.canvas.draw()
        
            self.years=[]
            self.manyYears=[]
            self.months=[]
            self.dates=[]

            self.years = sorted({date[:4] for date in self.dates_by_category[category]},reverse=True)
            self.manyYears = sorted({date[:4] for date in self.dates_by_category[category]})
            self.months = sorted({date[5:7] for date in self.dates_by_category[category]})
            self.dates = sorted({date[8:10] for date in self.dates_by_category[category]})

            self.monthComboBox.addItems(self.years)
            self.years = [int(x) for x in self.years]
            self.yearComboBox.addItems(self.group_years(self.manyYears))
        
            if category in ["Sales","Purchases"]:
                self.add_test_combobox()
            else:
                self.remove_test_combobox()


            self.update_charts_based_on_selection()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def add_test_combobox(self):
        try:
            if self.itemComboBox is None:
                self.itemComboBox = QtWidgets.QComboBox(parent=self.horizontalLayoutWidget_2)
                self.itemComboBox.setMaximumSize(QtCore.QSize(290, 16777215))
                font = QtGui.QFont()
                font.setFamily("Dubai")
                font.setPointSize(12)
                self.itemComboBox.setFont(font)
                self.itemComboBox.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
                self.itemComboBox.setAcceptDrops(False)
                self.itemComboBox.setEditable(False)
                self.itemComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
                self.itemComboBox.setPlaceholderText("Item Names")
                self.horizontalLayout_2.addWidget(self.itemComboBox)
                self.itemComboBox.currentTextChanged.connect(self.update_charts_based_on_selection)

            self.itemComboBox.blockSignals(True)
            self.itemComboBox.clear()
            self.itemComboBox.addItem("Select")
            self.itemComboBox.addItems(self.items)
            self.itemComboBox.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
           
    def remove_test_combobox(self):
        if self.itemComboBox:
            self.horizontalLayout_2.removeWidget(self.itemComboBox)
            self.itemComboBox.deleteLater()
            self.itemComboBox = None

    def update_charts_based_on_selection(self):
        try:
            yearly = self.yearComboBox.currentText()
            monthly = self.monthComboBox.currentText()
            daily = self.dailyComboBox.currentText()

            if yearly and not monthly and not daily:
                self.executor.submit(self.gotoModChartYear, yearly)
            if monthly and not daily and not yearly:
                self.executor.submit(self.gotoModChartMonth, monthly)
            if monthly and daily and not yearly:
                self.executor.submit(self.gotoModChartDaily, monthly, daily)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def get_year_range(self,group_year):
        try:
            if not group_year or "-" not in group_year:
                return [] 

            start_year, end_year = group_year.split("-")
            start_year = int(start_year)
            end_year = int(end_year)

            year_range = list(range(start_year, end_year + 1))
            return year_range
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
          
    def gotoModChartYear(self,value):
        self.executor.submit(self.update_chart_year, value)

    def update_chart_year(self, value):
        try:
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.monthComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            xlbl="Year"
            ylbl=""
            x = [0] * 7
            y = self.get_year_range(value)
            conn = create_connection()
            c = conn.cursor()
            if self.itemComboBox and self.itemComboBox.currentText() != "" and self.itemComboBox.currentText() != "Select":
                category = self.categoryComboBox.currentText()
                item=self.itemComboBox.currentText()
                for year in self.years:
                    if year in y:
                        val = f"{year}-"
                        if category == "Sales":
                            c.execute("SELECT COUNT(*) FROM SalesMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                            ylbl="Sales"
                        elif category == "Purchases":
                            c.execute("SELECT COUNT(*) FROM PurchaseMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                            ylbl="Purchases"
                        result = c.fetchone()
                        count = result[0] if result else 0
                        day_index = y.index(year)
                        x[day_index] = count
                ylbl = f"{item} {ylbl}"
            else:
                category = self.categoryComboBox.currentText()
                for year in self.years:
                    if year in y:
                        val = f"{year}-"
                        if category == "Sales":
                            c.execute("SELECT Items FROM SalesMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                            items=c.fetchall()
                            items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                            count=len(items_list)
                            year_index = y.index(year)
                            x[year_index] = count
                            ylbl="Sales"
                            continue
                        elif category == "Purchases":
                            c.execute("SELECT Items FROM PurchaseMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                            items=c.fetchall()
                            items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                            count=len(items_list)
                            year_index = y.index(year)
                            x[year_index] = count
                            ylbl="Purchases"
                            continue
            y=[str(year) for year in y]
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoModChartMonth(self, value):
        self.executor.submit(self.update_chart_month, value)

    def update_chart_month(self, value):
        try:
            self.yearComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            xlbl="Month"
            ylbl=""
            x = [0] * 12
            y = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_noTonames = {
                '01': 'Jan',
                '02': 'Feb',
                '03': 'Mar',
                '04': 'Apr',
                '05': 'May',
                '06': 'Jun',
                '07': 'Jul',
                '08': 'Aug',
                '09': 'Sep',
                '10': 'Oct',
                '11': 'Nov',
                '12': 'Dec'
            }
            conn = create_connection()
            c = conn.cursor()
            if self.itemComboBox and self.itemComboBox.currentText() != "" and self.itemComboBox.currentText() != "Select":
                category = self.categoryComboBox.currentText()
                item=self.itemComboBox.currentText()
                for month in self.months:
                    val = f"{value}-{month}"
                    if category == "Sales":
                        c.execute("SELECT COUNT(*) FROM SalesMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Sales"
                    elif category == "Purchases":
                        c.execute("SELECT COUNT(*) FROM PurchaseMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Purchases"
                    result = c.fetchone()
                    count = result[0] if result else 0
                    month_index = y.index(month_noTonames.get(month))
                    x[month_index] = count
                ylbl = f"{item} {ylbl}"
            else:
                category = self.categoryComboBox.currentText()
                for month in self.months:
                    val = f"{value}-{month}"
                    if category == "Sales":
                        c.execute("SELECT Items FROM SalesMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        month_index = y.index(month_noTonames.get(month))
                        x[month_index] = count
                        ylbl="Sales"
                        continue
                    elif category == "Purchases":
                        c.execute("SELECT Items FROM PurchaseMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        month_index = y.index(month_noTonames.get(month))
                        x[month_index] = count
                        ylbl="Purchases"
                        continue
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_plot(self, labels, values, xlabel, ylabel):
        try:
            self.axes.cla()
            self.canvas.draw()
            self.axes.plot(labels, values, marker='o', linestyle='-',color='#26648E')
            self.axes.set_facecolor('#E5ECF6')
            self.axes.tick_params(axis='x', rotation=45)
            self.axes.set_xlabel(xlabel)
            self.axes.set_ylabel(ylabel)
            self.fig.subplots_adjust(bottom=0.239)
            self.canvas.draw()
            self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,labels,xlabel,ylabel))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def hover(self, event,labels,xlbl,ylbl):
        try:
            if labels=='' or xlbl=='' or ylbl=='':
                self.axes.set_title('')
            elif event.inaxes == self.axes:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    rounded_x = round(x)
                    if 0 <= rounded_x < len(labels):
                        xlabel = labels[rounded_x]
                    else:
                        rounded_x = max(0, min(len(labels) - 1, int(x)))
                        xlabel = labels[rounded_x]
                    self.axes.set_title(f'{xlbl} : {xlabel}  {ylbl} : {y:.0f}')
                else:
                    self.axes.set_title('')
            else:
                self.axes.set_title('')
            self.fig.canvas.draw()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoModChartDaily(self, yearValue,monthValue):
        self.executor.submit(self.update_chart_daily, yearValue,monthValue)

    def update_chart_daily(self, yearValue,monthValue):
        try:
            self.yearComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            xlbl="Day"
            ylbl=""
            month_namesTonum = {
                'January': '01',
                'February': '02',
                'March': '03',
                'April': '04',
                'May': '05',
                'June': '06',
                'July': '07',
                'August': '08',
                'September': '09',
                'October': '10',
                'November': '11',
                'December': '12'
            }
            value = month_namesTonum.get(monthValue)
            yearMonthValue = f"{yearValue}-{value}"

            days_in_month = {
                '01': 31, '03': 31, '05': 31, '07': 31, '08': 31, '10': 31, '12': 31,
                '04': 30, '06': 30, '09': 30, '11': 30,
                '02': 29 if self.checkLeapYear(int(yearValue)) else 28
            }
            days = days_in_month[value]
            x = [0] * days
            y = [str(day) for day in range(1, days + 1)]
            conn = create_connection()
            c = conn.cursor()
            if self.itemComboBox and self.itemComboBox.currentText() != "" and self.itemComboBox.currentText() != "Select":
                category = self.categoryComboBox.currentText()
                item=self.itemComboBox.currentText()
                for day in y:
                    val = f"{yearMonthValue}-{day.zfill(2)}"
                    if category == "Sales":
                        c.execute("SELECT COUNT(*) FROM SalesMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Sales"
                    elif category == "Purchases":
                        c.execute("SELECT COUNT(*) FROM PurchaseMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Purchases"
                    result = c.fetchone()
                    count = result[0] if result else 0
                    day_index = y.index(day)
                    x[day_index] = count
                ylbl = f"{item} {ylbl}"
            else:
                category = self.categoryComboBox.currentText()
                for day in y:
                    val = f"{yearMonthValue}-{day.zfill(2)}"
                    if category == "Sales":
                        c.execute("SELECT Items FROM SalesMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        day_index = y.index(day)
                        x[day_index] = count
                        ylbl="Sales"
                        continue
                    elif category == "Purchases":
                        c.execute("SELECT Items FROM PurchaseMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        day_index = y.index(day)
                        x[day_index] = count
                        ylbl="Purchases"
                        continue
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            
    def checkLeapYear(self,year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class AdminMenuApp(QtWidgets.QDialog, DraggableMixin,AdminMenu_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(AdminMenuApp,self).__init__()
        self.setupUi(self)
        self.Ename=Ename
        self.Eid=Eid
        self.Erole=Erole
        self.newEmployeeButton.clicked.connect(self.gotoSignUp)
        self.resetPasswordButton.clicked.connect(self.gotoResetPassword)
        self.servicesButton.clicked.connect(self.gotoService)
        self.salesButton.clicked.connect(self.gotoSale)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.logsButton.clicked.connect(self.gotoLogs)
        self.settingsButton.clicked.connect(self.gotoSettings)
    
    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def gotoSignUp(self):
        signUpWindow=SignUpApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(signUpWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoSettings(self):
        DetailsWindow=DetailsApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(DetailsWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogs(self):
        LogsWindow=LogsApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(LogsWindow)    
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoResetPassword(self):
        resetPasswordWindow=ResetPasswordApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(resetPasswordWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoService(self):
        AdminServiceWindow=mainAdminServiceApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminServiceWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoSale(self):
        AdminSaleWindow=mainAdminSaleApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminSaleWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.gotoLogout()
        else:
            super(AdminMenuApp, self).keyPressEvent(event)

class mainAdminTestApp(QtWidgets.QMainWindow,AdminTest_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminTestApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.viewServicesButton.clicked.connect(self.gotoServices)
        self.importButton.clicked.connect(self.gotoImport)
        self.exportButton.clicked.connect(self.gotoExport)
        self.newButton.clicked.connect(self.gotoNewTest)
        self.tableWidget.cellChanged.connect(self.itemChanged)
        self.reloadButton.clicked.connect(self.gotoReload)
        self.templateButton.clicked.connect(self.gotoDownload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)
        
    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
 
    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT RM.Date, TM.TID, TM.TestName, RM.Fee,TM.GSTIN,TM.TaxRate,TM.InclusiveOfTax FROM TestMaster TM INNER JOIN RateMaster RM ON TM.TID = RM.TID WHERE (RM.TID, RM.Date) IN (SELECT TID, MAX(Date) FROM RateMaster GROUP BY TID) ORDER BY TM.TID ASC;"
            c.execute("SELECT COUNT(*) FROM TestMaster")
            row_count, = c.fetchone()
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet(" QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;} ")
            tablerow=0        
            c.execute(query)
            inference = c.fetchall()
            if inference:      
                for row in inference:
                    self.populateRows(tablerow,row)
                    tablerow+=1
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRows(self,tablerow,row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)
            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)
            item2=QtWidgets.QTableWidgetItem(str(row[2]))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)
            item3=QtWidgets.QTableWidgetItem(f"₹ {str(row[3])}")
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)
            item4=QtWidgets.QTableWidgetItem(str(row[4]))
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,4,item4)
            item5=QtWidgets.QTableWidgetItem(str(row[5]))
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,5,item5)
            item6=QtWidgets.QTableWidgetItem(str(row[6]))
            item6.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,6,item6)

            
            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoDownload(self):
        headers = ["Date", "Test Name", "Fee", "GSTIN", "Tax Rate", "Inclusive Of Tax"]
        df = pd.DataFrame(columns=headers)
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "CSV files (*.csv)")
        if save_path:
            if not save_path.endswith('.csv'):
                save_path += '.csv'
            df.to_csv(save_path, index=False)
            QtWidgets.QMessageBox.information(self, "Success", f"Template file saved to {save_path}")
        else:
            print("Export canceled by user.")

    def gotoImport(self):
        try:
            path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV or Excel Files (*.csv *.xls *.xlsx)')[0]
            if path.endswith('.csv'):
                self.all_data = pd.read_csv(path)
            elif path.endswith('.xls') or path.endswith('.xlsx'):
                self.all_data = pd.read_excel(path)
            else:
                return

            required_columns = {'adet', 'aeemnstt', 'eef', 'ginst', 'aaerttx', 'acefiilnostuvx'}
            if not required_columns.issubset(set(map(lambda x: ''.join(sorted(x.lower().replace(' ', ''))), self.all_data.columns))):
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid Format: Required columns are missing")
                return
            
            conn = create_connection()
            c = conn.cursor()
            for i in range(len(self.all_data.index)):
                raw_date=None
                parsed_date=None
                formatted_date=None
                tName=None
                fee=None
                for j in range(len(self.all_data.columns)):
                    column_name = ''.join(sorted(self.all_data.columns[j].lower().replace(' ', '')))
                    if column_name=='adet': #Date column
                        raw_date = str(self.all_data.iat[i,j])
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        else:
                            formatted_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    if column_name=='aeemnstt': #Test Name column
                        tName=str(self.all_data.iat[i,j])
                        c.execute("SELECT COUNT(*) FROM TestMaster WHERE TestName = %s", (tName,))
                        count = c.fetchone()[0]
                        if count == 0:
                            c.execute("INSERT INTO TestMaster(TestName) VALUES(%s)", (tName,))
                            conn.commit()                        
                    if column_name=='eef': #Fee column
                        cell_value = str(self.all_data.iat[i, j]) 
                        if cell_value:
                            fee = float(''.join(re.findall(r'\d+\.?\d*', cell_value) ) ) 
                        else:
                            fee = None 
                        c.execute("SELECT TID FROM TestMaster WHERE TestName = %s",(tName,))
                        rTid,=c.fetchone()
                        c.execute("SELECT COUNT(*) FROM RateMaster WHERE Date = %s AND TID = %s", (formatted_date, rTid))
                        count = c.fetchone()[0]
                        if count == 0:
                            c.execute("INSERT INTO RateMaster(Date, TID, Fee) VALUES(%s, %s, %s)", (str(formatted_date), rTid, fee))
                        else:
                            c.execute("UPDATE RateMaster SET Fee = %s WHERE Date = %s AND TID = %s", (fee, str(formatted_date), rTid))
                        conn.commit()
                    if column_name=='ginst': #GSTIN column
                        c.execute("UPDATE TestMaster SET GSTIN = %s WHERE TID = %s AND TestName = %s", (str(self.all_data.iat[i, j]),rTid,tName))
                        conn.commit()
                    if column_name=='aaerttx': #Tax Rate column
                        c.execute("UPDATE TestMaster SET TaxRate = %s WHERE TID = %s AND TestName = %s", (str(self.all_data.iat[i, j]),rTid,tName))
                        conn.commit()    
                    if column_name=='acefiilnostuvx': #Inclusive Of Tax column
                        c.execute("UPDATE TestMaster SET InclusiveOfTax = %s WHERE TID = %s AND TestName = %s", (str(self.all_data.iat[i, j]),rTid,tName))
                        conn.commit() 
            log_db_operation(c,self.Eid,f"has imported new Tests") 
            conn.commit()
            c.close()
            conn.close()
            QtWidgets.QMessageBox.information(self, "Success", "File imported")
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.loadData()
        self.tableWidget.blockSignals(False)

    def itemChanged(self, row,column):
        try:
            self.tableWidget.blockSignals(True)
            test_name = self.tableWidget.item(row, 2).text()
            if column == 3:  
                new_fee = self.tableWidget.item(row,column).text()
                new_fee=''.join(re.findall(r'\d+\.?\d*', new_fee))
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor()

                c.execute("SELECT COUNT(*) FROM RateMaster WHERE Date = %s AND TID = %s", (todayDate, test_id))
                count = c.fetchone()[0]

                if count > 0:  
                    c.execute("UPDATE RateMaster SET Fee = %s WHERE Date = %s AND TID = %s", (float(new_fee), todayDate, test_id))
                else:  
                    c.execute("INSERT INTO RateMaster (Date, TID, Fee) VALUES (%s, %s, %s)", (todayDate, test_id, float(new_fee)))
                log_db_operation(c,self.Eid,f"has updated fee for {test_name} to {float(new_fee)}")
                conn.commit()
                c.close()
                conn.close()

            if column == 4:  
                new_gstin = self.tableWidget.item(row,column).text()
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE TestMaster SET GSTIN = %s WHERE TID = %s", (str(new_gstin),test_id))
                log_db_operation(c,self.Eid,f"has updated GSTIN for {test_name} to {str(new_gstin)}")
                conn.commit()
                c.close()
                conn.close()

            if column == 5:  
                new_taxrate = self.tableWidget.item(row,column).text()
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE TestMaster SET TaxRate = %s WHERE TID = %s", (new_taxrate,test_id))
                log_db_operation(c,self.Eid,f"has updated TaxRate for {test_name} to {new_taxrate}")
                conn.commit()
                c.close()
                conn.close()

            if column == 6:  
                new_iot = self.tableWidget.item(row,column).text()
                test_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE TestMaster SET InclusiveOfTax = %s WHERE TID = %s", (new_iot,test_id))
                log_db_operation(c,self.Eid,f"has updated InclusiveOfTax for {test_name} to {new_iot}")
                conn.commit()
                c.close()
                conn.close()
            self.tableWidget.blockSignals(False)
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSearch(self):
        try:
            
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                c.execute("SELECT COUNT(*) FROM TestMaster WHERE TestName LIKE %s",(f"%{searchData}%",))
                row_count, = c.fetchone()
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet(" QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;} ")
                tablerow=0
                query = """
                        SELECT RM.Date, TM.TID, TM.TestName, RM.Fee,TM.GSTIN,TM.TaxRate,TM.InclusiveOfTax
                        FROM TestMaster TM
                        INNER JOIN RateMaster RM ON TM.TID = RM.TID
                        WHERE (RM.TID, RM.Date) IN (
                            SELECT TID, MAX(Date)
                            FROM RateMaster
                            GROUP BY TID
                        ) AND TM.TestName LIKE %s
                        ORDER BY TM.TID ASC
                        """
                c.execute(query, (f"%{searchData}%",))
                rows = c.fetchall()
                tablerow=0 
                if rows: 
                    for row in rows:
                        self.populateRows(tablerow,row)
                        tablerow+=1

            self.tableWidget.blockSignals(False)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoServices(self):
        AdminServiceWindow=mainAdminServiceApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminServiceWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoNewTest(self):
        newTestWindow=newTestApp(self.Eid,self.Ename,self.Erole)
        if not(newTestWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainAdminServiceApp(QtWidgets.QMainWindow,AdminService_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminServiceApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.reloadButton.clicked.connect(self.gotoReload)
        self.menuButton.clicked.connect(self.gotoMenu)
        self.exportButton.clicked.connect(self.gotoExport)
        self.tableWidget.cellChanged.connect(self.itemChanged)
        self.testsButton.clicked.connect(self.gotoTest)
        self.viewServicesAnalysisButton.clicked.connect(self.gotoServiceAnalysis)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
  
    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT Date,Name,Age,Gender,MobileNo,Email,Address,SID,CID,AmountEstimated,Discount,PaymentType FROM CustomerMaster ORDER BY Date DESC;"
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRows(tablerow, row)

            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRows(self,tablerow,row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)
            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)
            item2=QtWidgets.QTableWidgetItem(str(row[2]))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)
            item3=QtWidgets.QTableWidgetItem(str(row[3]))
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)
            item4=QtWidgets.QTableWidgetItem(str(row[4]))
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,4,item4)
            item5=QtWidgets.QTableWidgetItem(str(row[5]))
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,5,item5)
            item6=QtWidgets.QTableWidgetItem(str(row[6]))
            item6.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,6,item6)

            data = self.retrieveData(str(row[7]))
            
            combinedStr1=data["names"]
            list_widget7 = ListViewInCellWidget(combinedStr1)
            self.tableWidget.setCellWidget(tablerow, 7, list_widget7)
            
            combinedStr2=data["tests"]
            list_widget8 = ListViewInCellWidget(combinedStr2)
            self.tableWidget.setCellWidget(tablerow, 8, list_widget8)

            combinedStr3=data["status"]
            list_widget9 = ListViewInCellWidget(combinedStr3)
            self.tableWidget.setCellWidget(tablerow, 9, list_widget9)

            combinedStr4=data["results"]
            list_widget10 = ListViewInCellWidget(combinedStr4)
            self.tableWidget.setCellWidget(tablerow, 10, list_widget10)

            item11=QtWidgets.QTableWidgetItem(f"₹ {str(row[9])}")
            item11.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, 11, item11)

            item12=QtWidgets.QTableWidgetItem(f"{str(row[10])} %")
            item12.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,12,item12)

            item13=QtWidgets.QTableWidgetItem(str(row[11]))
            item13.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,13,item13)
            
            self.tableWidget.update()
            if combinedStr2 not in ['Fungus','Bacteria','Animal','Plant']:
                self.tableWidget.resizeRowToContents(tablerow)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
          
    def itemChanged(self, row,column):
        try:
            self.tableWidget.blockSignals(True)
            if column == 12:  
                discount = self.tableWidget.item(row,column).text()
                if discount.endswith('%'):
                    discount = discount.rstrip('%')
                discount_value = float(re.findall(r'\d+\.?\d*', str(discount))[0]) if re.findall(r'\d+\.?\d*', str(discount)) else 0.0
                discount_percentage = discount_value / 100 

                rDate= self.tableWidget.item(row, 0).text()
                rName=self.tableWidget.item(row, 1).text()
                rAge=self.tableWidget.item(row, 2).text()
                rGender=self.tableWidget.item(row, 3).text()
                rMobileNo=self.tableWidget.item(row, 4).text()
                rEmail=self.tableWidget.item(row, 5).text()
                rAddress=self.tableWidget.item(row, 6).text()
                rFee=self.tableWidget.item(row, 11).text()

                conn = create_connection()
                c = conn.cursor()

                c.execute("""
                    SELECT CID 
                    FROM CustomerMaster 
                    WHERE Date = %s AND Name = %s AND Age = %s AND Gender = %s AND MobileNo = %s AND Email = %s AND Address = %s
                """, (rDate, rName, rAge, rGender, rMobileNo, rEmail, rAddress))
                rCid=c.fetchone()[0]

                c.execute("""
                    SELECT SUM(AmountEstimated) 
                    FROM SampleMaster 
                    WHERE CID = %s
                """, (rCid,))
                total_fee_result = c.fetchone()
                total_fee = float(total_fee_result[0]) if total_fee_result[0] is not None else 0.0


                discounted_fee = total_fee - (total_fee * discount_percentage)
                estimatedFee = round(discounted_fee, 2)  

            
                c.execute("""UPDATE CustomerMaster
                        SET AmountEstimated = %s , Discount = %s 
                        WHERE CID = %s
                        """, (estimatedFee,discount,rCid))
                conn.commit()
                c.close()
                conn.close()
            self.tableWidget.blockSignals(False)
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoMenu(self):
        menuWindow=AdminMenuApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(menuWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoTest(self):
        AdminTestWindow=mainAdminTestApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminTestWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoServiceAnalysis(self):
        AdminServiceAnalysisWindow=mainAdminServiceAnalyseApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminServiceAnalysisWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()
    
    def retrieveData(self, SIDS):
        try:
            self.strNamesList = []
            self.strResultsList = []
            self.strStatusList = []
            self.strTestsList = []

            items = SIDS.split(', ') if ', ' in SIDS else [SIDS]
            conn = create_connection()
            c = conn.cursor()

            query = """
            SELECT 
                SID, SampleName, TestResult, Status, TID
            FROM SampleMaster
            WHERE SID IN (%s)
            """ % ','.join(['%s'] * len(items))

            c.execute(query, items)
            results = c.fetchall()

            for result in results:
                sid, sample_name, test_result, status, tids = result
                
                self.strNamesList.append(sample_name if sample_name else "None")
                self.strResultsList.append(self.add_spaces_around_commas(test_result) if test_result else "None")
                self.strStatusList.append(status if status else "None")

                tid_list = [int(tid) for tid in tids.split(',')]
                test_names = []
                for tid in tid_list:
                    c.execute("SELECT TestName FROM TestMaster WHERE TID = %s", (tid,))
                    test_name = c.fetchone()
                    if test_name:
                        test_names.append(test_name[0])
                    else:
                        test_names.append("None")
                
                self.strTestsList.append(' ,'.join(test_names))

            self.strNames = ', '.join(self.strNamesList)
            self.strResults = ', '.join(self.strResultsList)
            self.strStatus = ', '.join(self.strStatusList)
            self.strTests = ', '.join(self.strTestsList)

            c.close()
            conn.close()

            return {
                "names": self.strNames,
                "results": self.strResults,
                "status": self.strStatus,
                "tests": self.strTests
            }
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def add_spaces_around_commas(self,element):
        try:
            if not isinstance(element, str):
                element = str(element)

            if ',' in element:
                return ' ,'.join(part.strip() for part in element.split(','))
            return element
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                query = """
                    SELECT DISTINCT CM.Date, CM.Name, CM.Age, CM.Gender, CM.MobileNo, CM.Email, CM.Address, CM.SID,CM.CID,CM.AmountEstimated,CM.Discount, CM.PaymentType
                    FROM CustomerMaster CM
                    INNER JOIN SampleMaster SM ON CM.SID LIKE '%%' || SM.SID || '%%'
                    INNER JOIN TestMaster TM ON SM.TID LIKE '%%' || TM.TID || '%%'
                    WHERE CM.Date = %s OR CM.Name = %s OR CM.MobileNo = %s OR CM.Email = %s OR CM.Address = %s OR
                        SM.SampleName = %s OR TM.TestName = %s OR SM.Status = %s OR CM.PaymentType = %s
                    """
                c.execute(query,(searchData,searchData,searchData,searchData,searchData,searchData,searchData,searchData,searchData))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRows(tablerow, row)

            self.tableWidget.blockSignals(False)

            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    widget = self.tableWidget.cellWidget(row, col)
                    if widget and isinstance(widget, ListViewInCellWidget):
                        df.at[row, columnHeaders[col]] = widget.getText()
                    else:
                        if self.tableWidget.item(row, col):
                            df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()
                        else:
                            df.at[row, columnHeaders[col]]= ""

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class mainAdminServiceAnalyseApp(QtWidgets.QMainWindow,AdminServiceAnalysis_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminServiceAnalyseApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        self.populate_dates()

        self.executor = ThreadPoolExecutor(max_workers=10)
         
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.debounce_timer = QtCore.QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_combobox_change)

        self.yearComboBox.currentTextChanged.connect(lambda: self.debounce_selection("year"))
        self.monthComboBox.currentTextChanged.connect(lambda: self.debounce_selection("month"))
        self.dailyComboBox.currentTextChanged.connect(lambda: self.debounce_selection("daily"))
        self.categoryComboBox.currentTextChanged.connect(self.update_chart)
        self.viewServicesButton.clicked.connect(self.gotoService)

        self.testComboBox = None
        self.reloadButton.clicked.connect(self.gotoReload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
 
    def gotoReload(self):
        self.categoryComboBox.blockSignals(True)
        self.yearComboBox.blockSignals(True)
        self.monthComboBox.blockSignals(True)
        self.dailyComboBox.blockSignals(True)
        self.categoryComboBox.setCurrentIndex(-1)
        self.yearComboBox.setCurrentIndex(-1)
        self.monthComboBox.setCurrentIndex(-1)
        self.dailyComboBox.setCurrentIndex(-1)
        self.categoryComboBox.blockSignals(False)
        self.monthComboBox.blockSignals(False)
        self.yearComboBox.blockSignals(False)
        self.dailyComboBox.blockSignals(False)
        if self.testComboBox:
            self.horizontalLayout_2.removeWidget(self.testComboBox)
            self.testComboBox.deleteLater()
            self.testComboBox = None
        self.axes.cla()
        self.canvas.draw()
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,'','',''))

    def gotoService(self):
        AdminServiceWindow=mainAdminServiceApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminServiceWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def debounce_selection(self, combo_type):
        self.selected_combo_type = combo_type
        self.debounce_timer.start(5)

    def on_combobox_change(self):
        try:
            if self.selected_combo_type == "year":
                self.gotoModChartYear(self.yearComboBox.currentText())
            elif self.selected_combo_type == "month":
                self.gotoModChartMonth(self.monthComboBox.currentText())
            elif self.selected_combo_type == "daily":
                if self.monthComboBox.currentText() == "" or self.monthComboBox.currentText() == "Select":
                    QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select a month before choosing a day.")
                else:
                    self.gotoModChartDaily(self.monthComboBox.currentText(), self.dailyComboBox.currentText())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populate_dates(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            c.execute("SELECT Date FROM CustomerMaster")
            self.alldates = c.fetchall()
            c.execute("SELECT TestName FROM TestMaster")
            self.alltests = c.fetchall()
            c.close()
            conn.close()
            self.years = sorted({date_tuple[0][:4] for date_tuple in self.alldates if date_tuple[0]}, reverse=True)
            self.manyYears = sorted({date_tuple[0][:4] for date_tuple in self.alldates if date_tuple[0]})
            self.months = sorted({date_tuple[0][5:7] for date_tuple in self.alldates if date_tuple[0]})
            self.dates = sorted({date_tuple[0][8:10] for date_tuple in self.alldates if date_tuple[0]})
            self.tests = sorted({test_tuple[0] for test_tuple in self.alltests if test_tuple[0]})

            self.monthComboBox.addItems(self.years)
            self.years = [int(x) for x in self.years]
            self.year_groups = self.group_years(self.manyYears)
            if self.year_groups:
                self.yearComboBox.addItems(self.year_groups)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def group_years(self, years):
        try:
            grouped_years = []
            while years:
                group = []
                min_year = int(years[0])
                for i in range(min_year, min_year + 7):
                    if str(i) in years:
                        years.remove(str(i))
                    group.append(str(i))
                if len(group) > 1:
                    formatted_group = f"{min_year}-{group[-1]}"
                else:
                    formatted_group = group[0] 
                grouped_years.append(formatted_group)
            return grouped_years
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_chart(self):
        self.yearComboBox.blockSignals(True)
        self.monthComboBox.blockSignals(True)
        self.dailyComboBox.blockSignals(True)
        self.yearComboBox.setCurrentIndex(-1)
        self.monthComboBox.setCurrentIndex(-1)
        self.dailyComboBox.setCurrentIndex(-1)
        self.monthComboBox.blockSignals(False)
        self.yearComboBox.blockSignals(False)
        self.dailyComboBox.blockSignals(False)

        self.axes.cla()
        self.canvas.draw()
        
        if self.categoryComboBox.currentText() == "Tests":
            self.add_test_combobox()
        else:
            self.remove_test_combobox()

        self.update_charts_based_on_selection()

    def add_test_combobox(self):
        try:
            if self.testComboBox is None:
                self.testComboBox = QtWidgets.QComboBox(parent=self.horizontalLayoutWidget_2)
                self.testComboBox.setMaximumSize(QtCore.QSize(290, 16777215))
                font = QtGui.QFont()
                font.setFamily("Dubai")
                font.setPointSize(12)
                self.testComboBox.setFont(font)
                self.testComboBox.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
                self.testComboBox.setAcceptDrops(False)
                self.testComboBox.setEditable(False)
                self.testComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
                self.testComboBox.setPlaceholderText("Test Names (Optional)")
                self.horizontalLayout_2.addWidget(self.testComboBox)
                self.testComboBox.currentTextChanged.connect(self.update_charts_based_on_selection)

            self.testComboBox.blockSignals(True)
            self.testComboBox.clear()
            self.testComboBox.addItem("Select")
            self.testComboBox.addItems(self.tests)
            self.testComboBox.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
           
    def remove_test_combobox(self):
        if self.testComboBox:
            self.horizontalLayout_2.removeWidget(self.testComboBox)
            self.testComboBox.deleteLater()
            self.testComboBox = None

    def update_charts_based_on_selection(self):
        try:
            yearly = self.yearComboBox.currentText()
            monthly = self.monthComboBox.currentText()
            daily = self.dailyComboBox.currentText()

            if yearly and not monthly and not daily:
                self.executor.submit(self.gotoModChartYear, yearly)
            if monthly and not daily and not yearly:
                self.executor.submit(self.gotoModChartMonth, monthly)
            if monthly and daily and not yearly:
                self.executor.submit(self.gotoModChartDaily, monthly, daily)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def get_year_range(self,group_year):
        try:
            if not group_year or "-" not in group_year:
                return [] 

            start_year, end_year = group_year.split("-")
            start_year = int(start_year)
            end_year = int(end_year)

            year_range = list(range(start_year, end_year + 1))
            return year_range
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
          
    def gotoModChartYear(self,value):
        self.executor.submit(self.update_chart_year, value)

    def update_chart_year(self, value):
        try:
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.monthComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            xlbl="Year"
            ylbl=""
            x = [0] * 7
            y = self.get_year_range(value)
            conn = create_connection()
            c = conn.cursor()
            if self.testComboBox and self.testComboBox.currentText() != "" and self.testComboBox.currentText() != "Select":
                category = self.testComboBox.currentText()
                c.execute("SELECT TID FROM TestMaster WHERE TestName LIKE %s", (f"%{category}%",))
                reTid=c.fetchone()[0]
                for year in self.years:
                    if year in y:
                        val = f"{year}-"
                        c.execute("SELECT COUNT(*) FROM SampleMaster WHERE SID LIKE %s AND TID LIKE %s", (f"%{val}%",f"%{reTid}%"))
                        result = c.fetchone()
                        count = result[0] if result and result[0] is not None else 0
                        month_index = y.index(year)
                        x[month_index] = count
                ylbl=category
            else:
                category = self.categoryComboBox.currentText()
                for year in self.years:
                    if year in y:
                        val = f"{year}-"
                        if category == "Customers":
                            c.execute("SELECT COUNT(*) FROM CustomerMaster WHERE Date LIKE %s", (f"%{val}%",))
                            ylbl="Customers"
                        elif category == "Samples":
                            val = f"PAR-L/{val}"
                            c.execute("SELECT COUNT(*) FROM SampleMaster WHERE SID LIKE %s", (f"%{val}%",))
                            ylbl="Samples"
                        elif category == "Tests":
                            c.execute("SELECT TID FROM SampleMaster WHERE SID LIKE %s", (f"%{val}%",))
                            tids = c.fetchall()
                            tids_list = [int(num) for item in tids for num in item[0].replace(" ", "").split(",")]
                            count = len(tids_list)
                            month_index = y.index(year)
                            x[month_index] = count
                            ylbl="Tests"
                            continue
                        elif category == "Revenue":
                            c.execute("SELECT AmountEstimated FROM CustomerMaster WHERE SID LIKE %s AND PaymentType != 'Not Paid'", (f"%{val}%",))
                            fees = c.fetchall()
                            fees_list = [item[0] for item in fees]
                            count = sum(fees_list)
                            month_index = y.index(year)
                            x[month_index] = count
                            ylbl="Revenue"
                            continue
                        result = c.fetchone()
                        count = result[0] if result and result[0] is not None else 0
                        month_index = y.index(year)
                        x[month_index] = count
            y=[str(year) for year in y]
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoModChartMonth(self, value):
        self.executor.submit(self.update_chart_month, value)

    def update_chart_month(self, value):
        try:
            self.yearComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            xlbl="Month"
            ylbl=""
            x = [0] * 12
            y = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_noTonames = {
                '01': 'Jan',
                '02': 'Feb',
                '03': 'Mar',
                '04': 'Apr',
                '05': 'May',
                '06': 'Jun',
                '07': 'Jul',
                '08': 'Aug',
                '09': 'Sep',
                '10': 'Oct',
                '11': 'Nov',
                '12': 'Dec'
            }
            conn = create_connection()
            c = conn.cursor()
            if self.testComboBox and self.testComboBox.currentText() != "" and self.testComboBox.currentText() != "Select":
                category = self.testComboBox.currentText()
                c.execute("SELECT TID FROM TestMaster WHERE TestName LIKE %s", (f"%{category}%",))
                reTid=c.fetchone()[0]
                for month in self.months:
                    val = f"{value}-{month}"
                    c.execute("SELECT COUNT(*) FROM SampleMaster WHERE SID LIKE %s AND TID LIKE %s", (f"%{val}%",f"%{reTid}%"))
                    result = c.fetchone()
                    count = result[0] if result and result[0] is not None else 0
                    month_index = y.index(month_noTonames.get(month))
                    x[month_index] = count
                ylbl=category
            else:
                category = self.categoryComboBox.currentText()
                for month in self.months:
                    val = f"{value}-{month}"
                    if category == "Customers":
                        c.execute("SELECT COUNT(*) FROM CustomerMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Customers"
                    elif category == "Samples":
                        val = f"PAR-L/{val}"
                        c.execute("SELECT COUNT(*) FROM SampleMaster WHERE SID LIKE %s", (f"%{val}%",))
                        ylbl="Samples"
                    elif category == "Tests":
                        c.execute("SELECT TID FROM SampleMaster WHERE SID LIKE %s", (f"%{val}%",))
                        tids = c.fetchall()
                        tids_list = [int(num) for item in tids for num in item[0].replace(" ", "").split(",")]
                        count = len(tids_list)
                        month_index = y.index(month_noTonames.get(month))
                        x[month_index] = count
                        ylbl="Tests"
                        continue
                    elif category == "Revenue":
                        c.execute("SELECT AmountEstimated FROM CustomerMaster WHERE SID LIKE %s AND PaymentType != 'Not Paid'", (f"%{val}%",))
                        fees = c.fetchall()
                        fees_list = [item[0] for item in fees]
                        count = sum(fees_list)
                        month_index = y.index(month_noTonames.get(month))
                        x[month_index] = count
                        ylbl="Revenue"
                        continue
                    result = c.fetchone()
                    count = result[0] if result and result[0] is not None else 0
                    month_index = y.index(month_noTonames.get(month))
                    x[month_index] = count

            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_plot(self, labels, values, xlabel, ylabel):
        try:
            self.axes.cla()
            self.canvas.draw()
            self.axes.plot(labels, values, marker='o', linestyle='-',color='#26648E')
            self.axes.set_facecolor('#E5ECF6')
            self.axes.tick_params(axis='x', rotation=45)
            self.axes.set_xlabel(xlabel)
            self.axes.set_ylabel(ylabel)
            self.fig.subplots_adjust(bottom=0.239)
            self.canvas.draw()
            self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,labels,xlabel,ylabel))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def hover(self, event,labels,xlbl,ylbl):
        try:
            if labels=='' or xlbl=='' or ylbl=='':
                self.axes.set_title('')
            elif event.inaxes == self.axes:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    rounded_x = round(x)
                    if 0 <= rounded_x < len(labels):
                        xlabel = labels[rounded_x]
                    else:
                        rounded_x = max(0, min(len(labels) - 1, int(x)))
                        xlabel = labels[rounded_x]
                    self.axes.set_title(f'{xlbl} : {xlabel}  {ylbl} : {y:.0f}')
                else:
                    self.axes.set_title('')
            else:
                self.axes.set_title('')
            self.fig.canvas.draw()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoModChartDaily(self, yearValue,monthValue):
        self.executor.submit(self.update_chart_daily, yearValue,monthValue)

    def update_chart_daily(self, yearValue,monthValue):
        try:
            self.yearComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            xlbl="Day"
            ylbl=""
            month_namesTonum = {
                'January': '01',
                'February': '02',
                'March': '03',
                'April': '04',
                'May': '05',
                'June': '06',
                'July': '07',
                'August': '08',
                'September': '09',
                'October': '10',
                'November': '11',
                'December': '12'
            }
            value = month_namesTonum.get(monthValue)
            yearMonthValue = f"{yearValue}-{value}"

            days_in_month = {
                '01': 31, '03': 31, '05': 31, '07': 31, '08': 31, '10': 31, '12': 31,
                '04': 30, '06': 30, '09': 30, '11': 30,
                '02': 29 if self.checkLeapYear(int(yearValue)) else 28
            }
            days = days_in_month[value]
            x = [0] * days
            y = [str(day) for day in range(1, days + 1)]
            conn = create_connection()
            c = conn.cursor()
            if self.testComboBox and self.testComboBox.currentText() != "" and self.testComboBox.currentText() != "Select":
                category = self.testComboBox.currentText()
                c.execute("SELECT TID FROM TestMaster WHERE TestName LIKE %s", (f"%{category}%",))
                reTid=c.fetchone()[0]
                for day in y:
                    val = f"{yearMonthValue}-{day.zfill(2)}"
                    c.execute("SELECT COUNT(*) FROM SampleMaster WHERE SID LIKE %s AND TID LIKE %s", (f"%{val}%",f"%{reTid}%"))
                    count = c.fetchone()[0]
                    month_index = y.index(day)
                    x[month_index] = count
                ylbl=category
            else:
                category = self.categoryComboBox.currentText()
                for day in y:
                    val = f"{yearMonthValue}-{day.zfill(2)}"
                    if category == "Customers":
                        c.execute("SELECT COUNT(*) FROM CustomerMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Customers"
                    elif category == "Samples":
                        val = f"PAR-L/{val}"
                        c.execute("SELECT COUNT(*) FROM SampleMaster WHERE SID LIKE %s", (f"%{val}%",))
                        ylbl="Samples"
                    elif category == "Tests":
                        c.execute("SELECT TID FROM SampleMaster WHERE SID LIKE %s", (f"%{val}%",))
                        tids = c.fetchall()
                        tids_list = [int(num) for item in tids for num in item[0].replace(" ", "").split(",")]
                        count = len(tids_list)
                        day_index = y.index(day)
                        x[day_index] = count
                        ylbl="Tests"
                        continue
                    elif category == "Revenue":
                        c.execute("SELECT AmountEstimated FROM CustomerMaster WHERE SID LIKE %s AND PaymentType != 'Not Paid'", (f"%{val}%",))
                        fees = c.fetchall()
                        fees_list = [item[0] for item in fees]
                        count = sum(fees_list)
                        day_index = y.index(day)
                        x[day_index] = count
                        ylbl="Revenue"
                        continue
                    result = c.fetchone()
                    count = result[0] if result and result[0] is not None else 0
                    day_index = y.index(day)
                    x[day_index] = count

            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            
    def checkLeapYear(self,year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class ResetPasswordApp(QtWidgets.QDialog, DraggableMixin,RstPassword_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(ResetPasswordApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.resetButton.clicked.connect(self.resetPass)
        self.cancelButton.clicked.connect(self.gotoMenu)
        self.resetButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.resetPass()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.gotoMenu()
        else:
            super(ResetPasswordApp, self).keyPressEvent(event)

    def highlightButton(self):
        originalStyleSheet = self.resetButton.styleSheet()
        self.resetButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.resetButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoMenu(self):
        menuWindow=AdminMenuApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(menuWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def resetPass(self):
        try:
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(46, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;"
            self.usernameLineEdit.setStyleSheet(style)
            self.passwordLineEdit.setStyleSheet(style)
            self.cnfmPasswordLineEdit.setStyleSheet(style)


            uname=self.usernameLineEdit.text().strip()
            pwd=self.passwordLineEdit.text()
            if not uname:
                self.highlightError(self.usernameLineEdit)
                self.highlightButton()
                return
            if len(pwd) < 8 or len(pwd) > 15:
                self.highlightError(self.passwordLineEdit)
                self.highlightButton()
                return
            cfmpwd=self.cnfmPasswordLineEdit.text()
            if len(cfmpwd) < 8 or len(cfmpwd) > 15:
                self.highlightError(self.cnfmPasswordLineEdit)
                self.highlightButton()
                return
            if pwd != cfmpwd:
                self.highlightError(self.passwordLineEdit)
                self.highlightError(self.cnfmPasswordLineEdit)
                self.highlightButton()
                return
            try:
                conn=create_connection()
                c=conn.cursor()
                queryToLc = "UPDATE LoginCredentials SET Password = %s WHERE Username = %s"
                c.execute(queryToLc, (pwd,uname))
                log_db_operation(c,self.Eid,f"has updated password for {uname}")
                conn.commit()
                c.close()
                conn.close()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoMenu()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

class SignUpApp(QtWidgets.QDialog, DraggableMixin,Signup_Ui_Form):
    rol=None
    def __init__(self,Eid,Ename,Erole):
        super(SignUpApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.receipientRadioButton.toggled.connect(self.gotoDetail)
        self.labTechnicianRadioButton.toggled.connect(self.gotoDetail)
        self.technicalManagerRadioButton.toggled.connect(self.gotoDetail)
        self.accountManagerRadioButton.toggled.connect(self.gotoDetail)
        self.adminRadioButton.toggled.connect(self.gotoDetail)
        self.registerButton.clicked.connect(self.addUser)
        self.cancelButton.clicked.connect(self.gotoMenu)
        self.registerButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.addUser()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.gotoMenu()
        else:
            super(SignUpApp, self).keyPressEvent(event)

    def highlightButton(self):
        originalStyleSheet = self.registerButton.styleSheet()
        self.registerButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.registerButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)
    
    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoMenu(self):
        menuWindow=AdminMenuApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(menuWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoDetail(self):
        if self.sender().isChecked():
            SignUpApp.rol = self.sender().text()

    def addUser(self):
        try:
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(46, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;"
            self.nameLineEdit.setStyleSheet(style)
            self.doBLineEdit.setStyleSheet(style)
            self.MnoLineEdit.setStyleSheet(style)
            self.addressLineEdit.setStyleSheet(style)
            self.usernameLineEdit.setStyleSheet(style)
            self.passwordLineEdit.setStyleSheet(style)
            self.cnfmPasswordLineEdit.setStyleSheet(style)


            name=self.nameLineEdit.text().strip()
            if not name or any(char.isdigit() for char in name):
                self.highlightError(self.nameLineEdit)
                self.highlightButton()
                return
            role=SignUpApp.rol
            if role==None:
                self.highlightButton()
                return
            dob=self.DoBDateEdit.date().toString("yyyy-MM-dd")
            if not dob:
                self.highlightError(self.doBLineEdit)
                self.highlightButton()
                return
            gen=self.genderComboBox.currentText()
            if self.genderComboBox.currentIndex()==-1:
                self.highlightError(self.genderComboBox)
                self.highlightButton()
                return
            mno=self.MnoLineEdit.text().strip()
            if len(mno)!=10:
                self.highlightError(self.MnoLineEdit)
                self.highlightButton()
                return
            address=self.addressLineEdit.text().strip()
            if not address:
                self.highlightError(self.addressLineEdit)
                self.highlightButton()
                return
            uname=self.usernameLineEdit.text().strip()
            if len(uname) < 5 or len(uname) > 20:
                self.highlightError(self.usernameLineEdit)
                self.highlightButton()
                return
            pwd=self.passwordLineEdit.text()
            if len(pwd) < 8 or len(pwd) > 15:
                self.highlightError(self.passwordLineEdit)
                self.highlightButton()
                return
            cfmpwd=self.cnfmPasswordLineEdit.text()
            if len(cfmpwd) < 8 or len(cfmpwd) > 15:
                self.highlightError(self.cnfmPasswordLineEdit)
                self.highlightButton()
                return
            if pwd != cfmpwd:
                self.highlightError(self.passwordLineEdit)
                self.highlightError(self.cnfmPasswordLineEdit)
                self.highlightButton()
                return
            doj = datetime.datetime.now().strftime("%Y %m %d")
            try:
                conn=create_connection()
                c=conn.cursor()
                queryToEm = "INSERT INTO EmployeeMaster (Name,Role,DoB,Gender,MobileNo,Address,DoJ) VALUES (%s, %s,%s, %s,%s, %s,%s)"
                c.execute(queryToEm, (name,role,dob,gen,mno,address,doj))
                log_db_operation(c,self.Eid,f"has added new user {name}")
                queryForEid = "SELECT EID FROM EmployeeMaster WHERE Name = %s and Role = %s and DoB = %s and Gender = %s and MobileNo = %s and Address = %s"
                c.execute(queryForEid,(name,role,dob,gen,mno,address))
                retrievedEid=c.fetchone()
                queryToLc = "INSERT INTO LoginCredentials (EID,Username, Password) VALUES (%s, %s, %s)"
                c.execute(queryToLc, (retrievedEid,uname,pwd))
                conn.commit()
                c.close()
                conn.close()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoMenu()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

class mainAdminSaleApp(QtWidgets.QMainWindow,AdminSale_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminSaleApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.reloadButton.clicked.connect(self.gotoReload)
        self.menuButton.clicked.connect(self.gotoMenu)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.addItemButton.clicked.connect(self.gotoAddItem)
        self.removeItemButton.clicked.connect(self.gotoRemoveItem)
        self.importButton.clicked.connect(self.gotoImport)
        self.exportButton.clicked.connect(self.gotoExport)
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)
        self.saleOrdersButton.clicked.connect(self.gotoSalesOrders)
        self.purchaseOrderButton.clicked.connect(self.gotoPurchaseOrders)
        self.tableWidget.cellChanged.connect(self.itemChanged)
        self.viewSalesAnalysisButton.clicked.connect(self.gotoAnalysis)
        self.templateButton.clicked.connect(self.gotoDownload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            query = "SELECT Date,ItemCode,ItemName,HSN,SalePrice,PurchasePrice,StockQuantity,GSTIN,TaxRate,InclusiveOfTax,ExpDate,MfgDate,AdditionalInfo FROM ItemMaster ORDER BY Date DESC;"
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRows(tablerow, row)
            c.close()
            conn.close()
          
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRows(self,tablerow,row):
        try:
            item0=QtWidgets.QTableWidgetItem(str(row[0]))
            item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,0,item0)

            item1=QtWidgets.QTableWidgetItem(str(row[1]))
            item1.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,1,item1)

            item2=QtWidgets.QTableWidgetItem(str(row[2]))
            item2.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,2,item2)

            item3=QtWidgets.QTableWidgetItem(str(row[3]))
            item3.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,3,item3)

            item4=QtWidgets.QTableWidgetItem(f"₹ {str(row[4])}")
            item4.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,4,item4)

            item5=QtWidgets.QTableWidgetItem(f"₹ {str(row[5])}")
            item5.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,5,item5)

            item6=QtWidgets.QTableWidgetItem(str(row[6]))
            item6.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,6,item6)

            item7=QtWidgets.QTableWidgetItem(str(row[7]))
            item7.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,7,item7)

            item8=QtWidgets.QTableWidgetItem(str(row[8]))
            item8.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,8,item8)

            item9=QtWidgets.QTableWidgetItem(str(row[9]))
            item9.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,9,item9)

            item10=QtWidgets.QTableWidgetItem(str(row[10]))
            item10.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,10,item10)

            item11=QtWidgets.QTableWidgetItem(str(row[11]))
            item11.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,11,item11)

            item12=QtWidgets.QTableWidgetItem(str(row[12]))
            item12.setFlags(QtCore.Qt.ItemFlag.ItemIsEditable|QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow,12,item12)

            if int(row[6]) < 2:
                for col in range(13):
                    self.tableWidget.item(tablerow, col).setForeground(QtGui.QColor('red'))

            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def itemChanged(self, row,column):
        try:
            self.tableWidget.blockSignals(True)
            item_name = self.tableWidget.item(row, 3).text()
            if column == 2:
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")  
                new_itemname = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET ItemName = %s , Date = %s WHERE ItemCode = %s", (new_itemname,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has renamed Item name from {item_name} to {new_itemname}")
                conn.commit()
                c.close()
                conn.close()
            if column == 3:
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")  
                new_itemhsn = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET HSN = %s , Date = %s WHERE ItemCode = %s", (new_itemhsn,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has changed HSN for {item_name} to {new_itemhsn}")
                conn.commit()
                c.close()
                conn.close()

            if column == 4:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_saleprice = self.tableWidget.item(row,column).text()
                new_saleprice=''.join(re.findall(r'\d+\.?\d*', new_saleprice))
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET SalePrice = %s , Date = %s WHERE ItemCode = %s", (float(new_saleprice),todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Sellig price for {item_name} to {new_saleprice}")
                conn.commit()
                c.close()
                conn.close()

            if column == 5:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_purchaseprice = self.tableWidget.item(row,column).text()
                new_purchaseprice=''.join(re.findall(r'\d+\.?\d*', new_purchaseprice))
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET PurchasePrice = %s , Date = %s WHERE ItemCode = %s", (float(new_purchaseprice),todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Purchase price for {item_name} to {new_purchaseprice}")
                conn.commit()
                c.close()
                conn.close()
            
            if column == 6:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_stockqty = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET StockQuantity = %s , Date = %s WHERE ItemCode = %s", (new_stockqty,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Stock for {item_name} to {new_stockqty}")
                conn.commit()
                c.close()
                conn.close()

            if column == 7:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_gstin = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET GSTIN = %s , Date = %s WHERE ItemCode = %s", (str(new_gstin),todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated GSTIN for {item_name} to {new_gstin}")
                conn.commit()
                c.close()
                conn.close()

            if column == 8:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemtax = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET TaxRate = %s , Date = %s WHERE ItemCode = %s", (new_itemtax,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Tax rate for {item_name} to {new_itemtax}")
                conn.commit()
                c.close()
                conn.close()
                
            if column == 9:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemiot = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET InclusiveOfTax = %s , Date = %s WHERE ItemCode = %s", (new_itemiot,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Inclusive of tax for {item_name} to {new_itemiot}")
                conn.commit()
                c.close()
                conn.close()

            if column == 10:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemexp = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET ExpDate = %s , Date = %s WHERE ItemCode = %s", (new_itemexp,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Exp date for {item_name} to {new_itemexp}")
                conn.commit()
                c.close()
                conn.close()
            
            if column == 11:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemmfg = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET MfgDate = %s , Date = %s WHERE ItemCode = %s", (new_itemmfg,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Mfg for {item_name} to {new_itemmfg}")
                conn.commit()
                c.close()
                conn.close()

            if column == 12:  
                todayDate=datetime.datetime.now().strftime("%Y-%m-%d")
                new_itemaf = self.tableWidget.item(row,column).text()
                item_id = self.tableWidget.item(row, 1).text()
                conn = create_connection()
                c = conn.cursor() 
                c.execute("UPDATE ItemMaster SET AdditionalInfo = %s , Date = %s WHERE ItemCode = %s", (new_itemaf,todayDate,item_id))
                log_db_operation(c,self.Eid,f"has updated Additional info for {item_name} to {new_itemaf}")
                conn.commit()
                c.close()
                conn.close()
            self.gotoReload()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoDownload(self):
        headers = ["Date", "Item Code", "Item Name", "HSN", "Sale Price", "Purchase Price","Stock Quantity","GSTIN","Tax Rate","Inclusive of Tax","Exp Date","Mfg Date","Additional Info"]
        df = pd.DataFrame(columns=headers)
        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "CSV files (*.csv)")
        if save_path:
            if not save_path.endswith('.csv'):
                save_path += '.csv'
            df.to_csv(save_path, index=False)
            QtWidgets.QMessageBox.information(self, "Success", f"Template file saved to {save_path}")
        else:
            print("Export canceled by user.")

    def gotoImport(self):
        try:
            path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME'), 'CSV or Excel Files (*.csv *.xls *.xlsx)')[0]
            if path.endswith('.csv'):
                self.all_data = pd.read_csv(path)
            elif path.endswith('.xls') or path.endswith('.xlsx'):
                self.all_data = pd.read_excel(path)
            else:
                return

            required_columns = {'adet', 'cdeeimot', 'aeeimmnt', 'hns', 'aceeilprs', 'acceehipprrsu','aciknoqstttuy','ginst','aaerttx','acefiilnostuvx','adeeptx','adefgmt'}
            if not required_columns.issubset(set(map(lambda x: ''.join(sorted(x.lower().replace(' ', ''))), self.all_data.columns))):
                QtWidgets.QMessageBox.critical(self, "Error", "Invalid Format: Required columns are missing")
                return
            
            conn = create_connection()
            c = conn.cursor()
            for i in range(len(self.all_data.index)):
                raw_date = None
                formatted_date = None
                itemCode = None
                itemSale = None
                itemPurchase = None                
                for j in range(len(self.all_data.columns)):
                    column_name = ''.join(sorted(self.all_data.columns[j].lower().replace(' ', '')))
                    cell_value = self.all_data.iat[i, j]

                    if column_name == 'adet':  # Date column
                        raw_date = str(cell_value)
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        else:
                            formatted_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    if column_name == 'cdeeimot':  # Item Code column
                        itemCode = cell_value
                        c.execute("SELECT COUNT(*) FROM ItemMaster WHERE ItemCode = %s", (itemCode,))
                        count = c.fetchone()[0]
                        if count == 0:
                            c.execute("""
                                INSERT INTO ItemMaster (Date, ItemCode)
                                VALUES (%s,%s)
                            """, (str(formatted_date), str(itemCode)))
                            conn.commit()
                    if column_name == 'aeeimmnt':  # Item Name column
                        c.execute("SELECT ID FROM ItemMaster WHERE ItemCode = %s",(itemCode,))
                        rId,=c.fetchone()
                        c.execute("""
                                UPDATE ItemMaster
                                SET ItemName = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'hns':  # HSN column
                        c.execute("""
                                UPDATE ItemMaster
                                SET HSN = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'aceeilprs':  # Sale Price column
                        itemSale = float(re.findall(r'\d+\.?\d*', str(cell_value))[0]) if re.findall(r'\d+\.?\d*', str(cell_value)) else 0.0
                        c.execute("""
                                UPDATE ItemMaster
                                SET SalePrice = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (float(itemSale), itemCode,rId))
                    if column_name == 'acceehipprrsu':  # Purchase Price column
                        itemPurchase = float(re.findall(r'\d+\.?\d*', str(cell_value))[0]) if re.findall(r'\d+\.?\d*', str(cell_value)) else 0.0
                        c.execute("""
                                UPDATE ItemMaster
                                SET PurchasePrice = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (float(itemPurchase), itemCode,rId))
                    if column_name == 'aciknoqstttuy':  # Stock Quantity column
                        c.execute("""
                                UPDATE ItemMaster
                                SET StockQuantity = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (int(cell_value), itemCode,rId))
                    if column_name == 'ginst':  # GSTIN column
                        c.execute("""
                                UPDATE ItemMaster
                                SET GSTIN = %s
                                WHERE ItemCode = %s  AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'aaerttx':  # Tax Rate column
                        c.execute("""
                                UPDATE ItemMaster
                                SET TaxRate = %s
                                WHERE ItemCode = %s  AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'acefiilnostuvx':  # Inclusive of Tax column
                        c.execute("""
                                UPDATE ItemMaster
                                SET InclusiveOfTax = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))
                    if column_name == 'adeeptx':  # Exp Date column
                        raw_date = str(cell_value)
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        c.execute("""
                                UPDATE ItemMaster
                                SET ExpDate = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(formatted_date), itemCode,rId))
                    if column_name == 'adefgmt':  # Mfg Date column
                        raw_date = str(cell_value)
                        if re.match(r'\d{2}-\d{2}-\d{4}', raw_date):
                            try:
                                parsed_date = datetime.datetime.strptime(raw_date, "%d-%m-%Y")
                                formatted_date = parsed_date.strftime("%Y-%m-%d")
                            except ValueError as ve:
                                QtWidgets.QMessageBox.critical(self, "Error", f"{ve}")
                        elif re.match(r'\d{4}-\d{2}-\d{2}', raw_date):
                            formatted_date = raw_date
                        c.execute("""
                                UPDATE ItemMaster
                                SET MfgDate = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(formatted_date), itemCode,rId))
                    if column_name in ['aaaddfiiiilmnnnooortt', 'aaddfiiilnnoot']:  # Additional Info column
                        c.execute("""
                                UPDATE ItemMaster
                                SET AdditionalInfo = %s
                                WHERE ItemCode = %s AND ID = %s
                            """, (str(cell_value), itemCode,rId))

                    conn.commit()
            log_db_operation(c,self.Eid,f"has imported new Items")
            conn.commit()
            c.close()
            conn.close() 
            QtWidgets.QMessageBox.information(self, "Success", "File imported")
            self.gotoReload()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoAddItem(self):
        AddItemWindow=AddItemApp(self.Eid,self.Ename,self.Erole)
        if not(AddItemWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoRemoveItem(self):
        RemoveItemWindow=RemoveItemApp(self.Eid,self.Ename,self.Erole)
        if not(RemoveItemWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                query = "SELECT Date,ItemCode,ItemName,HSN,SalePrice,PurchasePrice,StockQuantity,GSTIN,TaxRate,InclusiveOfTax,ExpDate,MfgDate,AdditionalInfo FROM ItemMaster WHERE Date LIKE %s or ItemName LIKE %s or ItemCode = %s or HSN LIKE %s"
                c.execute(query, (f"%{searchData}%",f"%{searchData}%",searchData,f"%{searchData}%"))
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRows(tablerow, row)

            self.tableWidget.blockSignals(False)
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoMenu(self):
        menuWindow=AdminMenuApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(menuWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoSalesOrders(self):
        AdminSalesOrdersWindow=mainAdminSalesOrdersApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminSalesOrdersWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoPurchaseOrders(self):
        AdminPurchaseOrdersWindow=mainAdminPurchaseOrdersApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminPurchaseOrdersWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoAnalysis(self):
        AdminSaleAnalysisWindow=mainAdminSaleAnalyseApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminSaleAnalysisWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class DetailsApp(QtWidgets.QDialog, DraggableMixin,DetailsUi_Form):
    def __init__(self,Eid,Ename,Erole):
        super(DetailsApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.loadData()
        self.saveButton.clicked.connect(self.gotoSave)
        self.cancelButton.clicked.connect(self.gotoMenu)
        self.saveButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoSave()
        else:
            super(SignUpApp, self).keyPressEvent(event)

    def loadData(self):
        conn = create_connection()
        c = conn.cursor()
        c.execute("SELECT Name, Phno, Address, District, State, Email, Password FROM CompanyDetails ORDER BY ID DESC")
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            CName, CPhno, CAddress, CDistrict, CState, CEmail, CPassword = result
            self.nameLineEdit.setText(CName)
            self.phnoLineEdit.setText(CPhno)
            self.addressLineEdit.setText(CAddress)
            self.districtLineEdit.setText(CDistrict)
            self.stateLineEdit.setText(CState)
            self.emailLineEdit.setText(CEmail)
            self.passwordLineEdit.setText(CPassword)

    def highlightButton(self):
        originalStyleSheet = self.saveButton.styleSheet()
        self.saveButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.saveButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)
    
    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoMenu(self):
        menuWindow=AdminMenuApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(menuWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoSave(self):
        try:
            global CName, CPhno, CAddress, CDistrict, CState, CEmail, CPassword
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(46, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;"
            self.nameLineEdit.setStyleSheet(style)
            self.phnoLineEdit.setStyleSheet(style)
            self.districtLineEdit.setStyleSheet(style)
            self.addressLineEdit.setStyleSheet(style)
            self.emailLineEdit.setStyleSheet(style)
            self.passwordLineEdit.setStyleSheet(style)
            self.stateLineEdit.setStyleSheet(style)


            name=self.nameLineEdit.text()
            if not name:
                self.highlightError(self.nameLineEdit)
                self.highlightButton()
                return
            phno=self.phnoLineEdit.text()
            if not phno:
                self.highlightError(self.phnoLineEdit)
                self.highlightButton()
                return
            email=self.emailLineEdit.text()
            if not email:
                self.highlightError(self.emailLineEdit)
                self.highlightButton()
                return
            pwd=self.passwordLineEdit.text()
            if not pwd:
                self.highlightError(self.passwordLineEdit)
                self.highlightButton()
                return
            address=self.addressLineEdit.text()
            if not address:
                self.highlightError(self.addressLineEdit)
                self.highlightButton()
                return
            dist=self.districtLineEdit.text().strip()
            if not dist:
                self.highlightError(self.districtLineEdit)
                self.highlightButton()
                return
            state=self.stateLineEdit.text().strip()
            if not state:
                self.highlightError(self.stateLineEdit)
                self.highlightButton()
                return
            
            try:
                conn=create_connection()
                c=conn.cursor()
                c.execute("INSERT INTO CompanyDetails (Name,Phno,Address,District,State,Email,Password) VALUES (%s, %s,%s, %s,%s, %s,%s)", (name,phno,address,dist,state,email,pwd))
                log_db_operation(c,self.Eid,f"has updated Company details")
                conn.commit()
                c.close()
                conn.close()
                CName=name
                CPhno=phno
                CAddress=address
                CDistrict=dist
                CState=state
                CEmail=email
                CPassword=pwd
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoMenu()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.gotoMenu()
        else:
            super(DetailsApp, self).keyPressEvent(event)  

class LogsApp(QtWidgets.QDialog, DraggableMixin,LogsUi_Form):
    def __init__(self,Eid,Ename,Erole):
        super(LogsApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.loadData()
        self.closeButton.clicked.connect(self.gotoMenu)
        self.closeButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            query = "SELECT Details FROM Logs"
            c.execute("SELECT COUNT(*) FROM Logs")
            row_count, = c.fetchone()
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet(" QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;} ")
            tablerow = 0
            try:
                c.execute(query)
                inference = c.fetchall()
                if inference:           
                    for row in inference:
                        item0=QtWidgets.QTableWidgetItem(str(row[0]))
                        item0.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable|QtCore.Qt.ItemFlag.ItemIsEnabled)
                        self.tableWidget.setItem(tablerow,0,item0)
                        tablerow += 1
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoMenu(self):
        menuWindow=AdminMenuApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(menuWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.gotoMenu()
        else:
            super(LogsApp, self).keyPressEvent(event)  

class AddItemApp(QtWidgets.QDialog, DraggableMixin,AddItem_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(AddItemApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.okButton.clicked.connect(self.gotoAddItem)
        self.cancelButton.clicked.connect(self.gotoSale)
        self.okButton.setFocus()
        self.inclusiveOfTaxComboBox.currentTextChanged.connect(self.gotoDisableTaxRate)
        conn = create_connection()
        c = conn.cursor()
        c.execute("""
            SELECT Id
            FROM ItemMaster 
            ORDER BY Id DESC LIMIT 1
        """)
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            last_id = int(result[0])
            new_id = last_id + 1
        else:
            new_id = 1
        self.itemCodeLineEdit.setText(f"{new_id:03d}")

    def gotoDisableTaxRate(self):
        if self.inclusiveOfTaxComboBox.currentText()=="No":
            self.taxRateLineEdit.setDisabled(True)
            self.taxRateLineEdit.clear()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoAddItem()
        else:
            super(AddItemApp, self).keyPressEvent(event)
 
    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoAddItem(self):
        try:
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:#984063; color:rgb(0, 0, 0); padding-bottom:7px;"
            self.itemNameLineEdit.setStyleSheet(style)
            self.itemCodeLineEdit.setStyleSheet(style)
            self.hsnLineEdit.setStyleSheet(style)
            self.salePriceLineEdit.setStyleSheet(style)
            self.purchasePriceLineEdit.setStyleSheet(style)
            self.stockQuantityLineEdit.setStyleSheet(style)
            self.mfgDateLineEdit.setStyleSheet(style)
            self.expDateLineEdit.setStyleSheet(style)
            self.taxRateLineEdit.setStyleSheet(style)
            self.GSTINLineEdit.setStyleSheet(style)
            itemName=self.itemNameLineEdit.text().strip()
            if not itemName or any(char.isdigit() for char in itemName):
                self.highlightError(self.itemNameLineEdit)
                self.highlightButton()
                return
            itemCode=self.itemCodeLineEdit.text().strip()
            if not itemCode:
                self.highlightError(self.itemCodeLineEdit)
                self.highlightButton()
                return
            itemHSN=self.hsnLineEdit.text().strip() or ""
            salePrice=self.salePriceLineEdit.text().strip()
            salePrice=''.join(re.findall(r'\d+\.?\d*', salePrice))
            if not salePrice or salePrice.isalpha():
                self.highlightError(self.salePriceLineEdit)
                self.highlightButton()
                return
            purchasePrice=self.purchasePriceLineEdit.text().strip()
            purchasePrice=''.join(re.findall(r'\d+\.?\d*', purchasePrice))
            if not purchasePrice or purchasePrice.isalpha():
                self.highlightError(self.purchasePriceLineEdit)
                self.highlightButton()
                return
            stockQuantity=self.stockQuantityLineEdit.text().strip()
            if not stockQuantity or stockQuantity.isalpha():
                self.highlightError(self.stockQuantityLineEdit)
                self.highlightButton()
                return
            mfg=self.mfgDateEdit.date().toString("yyyy-MM-dd")
            if not mfg:
                self.highlightError(self.mfgDateLineEdit)
                self.highlightButton()
                return
            exp=self.expDateEdit.date().toString("yyyy-MM-dd")
            if not exp:
                self.highlightError(self.expDateLineEdit)
                self.highlightButton()
                return
            taxRate=self.taxRateLineEdit.text().strip()
            gstIn=self.GSTINLineEdit.text().strip()
            ioft=self.inclusiveOfTaxComboBox.currentText()
            if not ioft:
                self.highlightError(self.inclusiveOfTaxComboBox)
                self.highlightButton()
                return
            addinfo=self.addFieldLineEdit.text().strip() or ""
            dateToday=datetime.datetime.now().strftime("%Y-%m-%d")

            try:
                conn=create_connection()
                c=conn.cursor()
                c.execute("INSERT INTO ItemMaster(Date,ItemCode,ItemName,HSN,SalePrice,PurchasePrice,StockQuantity,GSTIN,TaxRate,InclusiveOfTax,ExpDate,MfgDate,AdditionalInfo) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(dateToday,itemCode,itemName,itemHSN,float(salePrice),float(purchasePrice),stockQuantity,str(gstIn),taxRate,ioft,exp,mfg,addinfo))
                log_db_operation(c,self.Eid,f"has added new Item {itemName}")
                conn.commit()
                c.close()
                conn.close()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoSale()   
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoSale(self):
        self.reject()

class RemoveItemApp(QtWidgets.QDialog, DraggableMixin,RemoveItem_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(RemoveItemApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.removeButton.clicked.connect(self.gotoRemoveItem)
        self.cancelButton.clicked.connect(self.gotoSale)
        self.removeButton.setFocus()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoRemoveItem()
        else:
            super(RemoveItemApp, self).keyPressEvent(event)

    def highlightButton(self):
        originalStyleSheet = self.removeButton.styleSheet()
        self.removeButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.removeButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def gotoRemoveItem(self):
        try:
            conn=create_connection()
            c=conn.cursor()
            style="background-color:rgba(0, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:#984063; color:rgb(0, 0, 0); padding-bottom:7px;"
            self.itemNameLineEdit.setStyleSheet(style)
            self.itemCodeLineEdit.setStyleSheet(style)
            self.hsnLineEdit.setStyleSheet(style)
            itemName=self.itemNameLineEdit.text().strip()
            if not itemName or any(char.isdigit() for char in itemName):
                self.highlightError(self.itemNameLineEdit)
                self.highlightButton()
                return
            itemCode=self.itemCodeLineEdit.text().strip()
            if not itemCode:
                self.highlightError(self.itemCodeLineEdit)
                self.highlightButton()
                return
            itemHSN=self.hsnLineEdit.text().strip() or ""

            try:
                if itemHSN and itemHSN!="":
                    c.execute(
                        "DELETE FROM ItemMaster WHERE ItemCode = %s AND ItemName = %s AND HSN = %s",
                        (itemCode, itemName,itemHSN)
                    )
                else:
                    c.execute(
                        "DELETE FROM ItemMaster WHERE ItemCode = %s AND ItemName = %s",
                        (itemCode, itemName)
                    )
                conn.commit()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            c.close()
            conn.close()
            self.gotoSale()  
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoSale(self):
        self.reject()

class mainAdminSalesOrdersApp(QtWidgets.QMainWindow,AdminSalesOrders_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminSalesOrdersApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        self.smtp_server_conn = None
        
        
        self.loadData()
        self.reloadButton.clicked.connect(self.gotoReload)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.addSaleButton.clicked.connect(self.gotoAddSale)
        self.exportButton.clicked.connect(self.gotoExport)
        self.itemsButton.clicked.connect(self.gotoItems)
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            query = """
                SELECT OrderNo, OrderDate, OrderTime, Party, Email,ContactNo,BillingAddress, State, Items, HSNCode, Qty, Price, Tax, TaxAmount,Total,PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                FROM SalesMaster
                ORDER BY ID DESC;
                """
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRow(tablerow, row)
            c.close()
            conn.close()
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRow(self,tablerow,row):
        for col in range(23):
            if col in {17, 18, 19,20}:
                text = f"₹ {row[col]}"
            elif col == 16:
                text = f"{row[col]} %"
            elif col == 21:
                self.addPreviewButton(tablerow, col, "Preview", str(row[17]), self.Ename, self.Erole)
                continue
            elif col == 22:
                self.addSendButton(tablerow, col, "Send", str(row[17]), self.Ename, self.Erole)
                continue
            else:
                cell_text = str(row[col])
                if ', ' in cell_text and col!=6:
                    item = ListViewInCellWidget(cell_text)
                    self.tableWidget.setCellWidget(tablerow, col, item)
                    continue
                else:
                    text = cell_text
            
            item = QtWidgets.QTableWidgetItem(text)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, col, item)
            self.tableWidget.resizeRowToContents(tablerow)
            self.tableWidget.update()

    def addPreviewButton(self, row, col, text, Id, Ename, Erole):
        button = QtWidgets.QPushButton(str(text))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(12)
        font.setBold(True)
        button.setFont(font)
        button.setObjectName("cellPreviewButton")
        button.setProperty('row', row)
        button.clicked.connect(self.gotoPreview)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.tableWidget.setCellWidget(row, col, container)
        self.tableWidget.resizeRowToContents(row)

    def addSendButton(self, row, col, text, Id, Ename, Erole):
        button = QtWidgets.QPushButton(str(text))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(12)
        font.setBold(True)
        button.setFont(font)
        button.setObjectName("cellSendButton")
        button.setProperty('row', row)
        button.clicked.connect(self.gotoSendMail)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.tableWidget.setCellWidget(row, col, container)
        self.tableWidget.resizeRowToContents(row)

    def getCellWidgetText(self, row, col):
        widget = self.tableWidget.cellWidget(row, col)
        if widget and isinstance(widget, ListViewInCellWidget):
            return widget.getText()
        elif self.tableWidget.item(row, col):
            return self.tableWidget.item(row, col).text()
        else:
            return ''

    def gotoPreview(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT Name, Phno, Address, District, State, Email FROM CompanyDetails ORDER BY ID DESC")
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                CName, CPhno, CAddress, CDistrict, CState, CEmail = result
            else:
                CName, CPhno, CAddress, CDistrict, CState, CEmail = '', '', '', '', '', ''
            button = self.sender()
            row = button.property('row')  

            orderDate = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ''
            orderTime = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ''
            orderNo = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ''
            todayDate = datetime.datetime.now().strftime('%Y-%m-%d')
            Party = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ''
            ContactNo = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ''
            Email = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ''
            BillingAddress = self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else ''
            State = self.tableWidget.item(row, 7).text() if self.tableWidget.item(row, 7) else ''

            items_str = self.getCellWidgetText(row, 8) 
            hsn_str = self.getCellWidgetText(row, 9)
            qty_str = self.getCellWidgetText(row, 10)
            price_str = self.getCellWidgetText(row, 11)
            tax_str = self.getCellWidgetText(row, 12)
            taxAmount_str = self.getCellWidgetText(row, 13)
            total_str = self.getCellWidgetText(row, 14)


            items = items_str.split(', ') if ', ' in items_str else [items_str]
            hsn_codes = hsn_str.split(', ') if ', ' in hsn_str else [hsn_str]
            qtys = qty_str.split(', ') if ', ' in qty_str else [qty_str]
            prices = price_str.split(', ') if ', ' in price_str else [price_str]
            taxes = tax_str.split(', ') if ', ' in tax_str else [tax_str]
            taxAmounts = taxAmount_str.split(', ') if ', ' in taxAmount_str else [taxAmount_str]
            totals = total_str.split(', ') if ', ' in total_str else [total_str]

            lengths = [len(items), len(hsn_codes), len(qtys), len(prices), len(taxes), len(taxAmounts), len(totals)]
            if len(set(lengths)) != 1:
                raise ValueError(f"Mismatch in list lengths: {lengths}")

            item_details = []
            for i in range(len(items)):
                item_details.append({
                    'sno': i + 1,
                    'item': items[i],
                    'hsn': hsn_codes[i],
                    'qty': qtys[i],
                    'price': prices[i],
                    'tax': taxes[i],
                    'taxAmount': taxAmounts[i],
                    'total': totals[i]
                })
            Discount = self.tableWidget.item(row, 16).text() if self.tableWidget.item(row, 16) else ''
            Total = self.tableWidget.item(row, 17).text() if self.tableWidget.item(row, 17) else ''
            PaymentType = self.tableWidget.item(row, 15).text() if self.tableWidget.item(row, 15) else ''
            AdvAmount = self.tableWidget.item(row, 18).text() if self.tableWidget.item(row, 18) else ''
            CurrentBalance = self.tableWidget.item(row, 19).text() if self.tableWidget.item(row, 19) else ''

            data = {
                'CName': CName,
                'CPhno': CPhno,
                'CEmail': CEmail,
                'CAddress': CAddress,
                'CDistrict': CDistrict,
                'CState': CState,
                'orderDate': orderDate,
                'orderTime': orderTime,
                'orderNo': orderNo,
                'todayDate': todayDate,
                'Party': Party,
                'ContactNo': ContactNo,
                'Email': Email,
                'BillingAddress': BillingAddress,
                'State': State,
                'items': item_details,
                'Discount': Discount,
                'Total': Total,
                'PaymentType': PaymentType,
                'AdvAmount': AdvAmount,
                'CurrentBalance': CurrentBalance
            }

            env = Environment(loader=FileSystemLoader(resource_path('')))
            template = env.get_template('Sales.html')
            output_text = template.render(data)

            output_html = 'Sale Invoice.html'
            with open(output_html, 'w', encoding='utf-8') as file:
                file.write(output_text)
                file_path = resource_path(output_html)
            
            webbrowser.open(f'file://{file_path}')
            time.sleep(5)
            try:
                while True:
                    os.remove(file_path)
                    break
            except PermissionError:
                time.sleep(5)


        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoSendMail(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT Name, Phno, Address, District, State, Email, Password FROM CompanyDetails ORDER BY ID DESC")
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                CName, CPhno, CAddress, CDistrict, CState, CEmail, CPassword = result
            else:
                CName, CPhno, CAddress, CDistrict, CState, CEmail, CPassword = '', '', '', '', '', '', ''
            button = self.sender()
            row = button.property('row')  

            orderDate = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ''
            orderTime = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ''
            orderNo = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ''
            todayDate = datetime.datetime.now().strftime('%Y-%m-%d')
            Party = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ''
            ContactNo = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ''
            Email = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ''
            BillingAddress = self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else ''
            State = self.tableWidget.item(row, 7).text() if self.tableWidget.item(row, 7) else ''

            items_str = self.getCellWidgetText(row, 8) 
            hsn_str = self.getCellWidgetText(row, 9)
            qty_str = self.getCellWidgetText(row, 10)
            price_str = self.getCellWidgetText(row, 11)
            tax_str = self.getCellWidgetText(row, 12)
            taxAmount_str = self.getCellWidgetText(row, 13)
            total_str = self.getCellWidgetText(row, 14)


            items = items_str.split(', ') if ', ' in items_str else [items_str]
            hsn_codes = hsn_str.split(', ') if ', ' in hsn_str else [hsn_str]
            qtys = qty_str.split(', ') if ', ' in qty_str else [qty_str]
            prices = price_str.split(', ') if ', ' in price_str else [price_str]
            taxes = tax_str.split(', ') if ', ' in tax_str else [tax_str]
            taxAmounts = taxAmount_str.split(', ') if ', ' in taxAmount_str else [taxAmount_str]
            totals = total_str.split(', ') if ', ' in total_str else [total_str]

            lengths = [len(items), len(hsn_codes), len(qtys), len(prices), len(taxes), len(taxAmounts), len(totals)]
            if len(set(lengths)) != 1:
                raise ValueError(f"Mismatch in list lengths: {lengths}")

            item_details = []
            for i in range(len(items)):
                item_details.append({
                    'sno': i + 1,
                    'item': items[i],
                    'hsn': hsn_codes[i],
                    'qty': qtys[i],
                    'price': prices[i],
                    'tax': taxes[i],
                    'taxAmount': taxAmounts[i],
                    'total': totals[i]
                })
            Discount = self.tableWidget.item(row, 16).text() if self.tableWidget.item(row, 16) else ''
            Total = self.tableWidget.item(row, 17).text() if self.tableWidget.item(row, 17) else ''
            PaymentType = self.tableWidget.item(row, 15).text() if self.tableWidget.item(row, 15) else ''
            AdvAmount = self.tableWidget.item(row, 18).text() if self.tableWidget.item(row, 18) else ''
            CurrentBalance = self.tableWidget.item(row, 19).text() if self.tableWidget.item(row, 19) else ''

            data = {
                'CName': CName,
                'CPhno': CPhno,
                'CEmail': CEmail,
                'CAddress': CAddress,
                'CDistrict': CDistrict,
                'CState': CState,
                'orderDate': orderDate,
                'orderTime': orderTime,
                'orderNo': orderNo,
                'todayDate': todayDate,
                'Party': Party,
                'ContactNo': ContactNo,
                'Email': Email,
                'BillingAddress': BillingAddress,
                'State': State,
                'items': item_details,
                'Discount': Discount,
                'Total': Total,
                'PaymentType': PaymentType,
                'AdvAmount': AdvAmount,
                'CurrentBalance': CurrentBalance
            }

            env = Environment(loader=FileSystemLoader(resource_path('')))
            template = env.get_template('Sales.html')
            output_text = template.render(data)

            self.send_email_with_invoice(Email,CEmail,CPassword,output_text)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            
    def send_email_with_invoice(self,to_address,CEmail,CPassword, invoice):      
        msg = MIMEMultipart()
        msg['From'] = CEmail
        msg['To'] = to_address
        msg['Subject'] = 'Your Purchase Confirmation and Invoice'

        html_content = f"""
                        <html>
                        <head>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                            }}
                            .container {{
                                width: 100%;
                                margin: 0 auto;
                                padding: 20px;
                                background-color: #f9f9f9;
                            }}
                            .content {{
                                background-color: #ffffff;
                                padding: 20px;
                                border: 1px solid #dddddd;
                            }}
                            h1 {{
                                color: #333333;
                            }}
                            p {{
                                color: #666666;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                padding: 10px;
                                border: 1px solid #dddddd;
                            }}
                        </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="content">
                                    {invoice}
                                </div>
                            </div>
                        </body>
                        </html>
                        """
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            if check_internet_connection() and self.smtp_server_conn is None:
                try:
                    self.smtp_server_conn = smtplib.SMTP('smtp.gmail.com',587)
                    self.smtp_server_conn.starttls()
                    self.smtp_server_conn.login(CEmail,CPassword)
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            elif check_internet_connection() and self.smtp_server_conn is not None:
                try:
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "No internet connection. Please check your network settings.")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    widget = self.tableWidget.cellWidget(row, col)
                    if widget and isinstance(widget, ListViewInCellWidget):
                        df.at[row, columnHeaders[col]] = widget.getText()
                    else:
                        if self.tableWidget.item(row, col):
                            df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()
                        else:
                            df.at[row, columnHeaders[col]]= ""

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoAddSale(self):
        AddSaleWindow=AddSaleApp(self.Eid,self.Ename,self.Erole)
        if not(AddSaleWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                parameters = (
                        f"%{searchData}%", f"%{searchData}%", 
                        searchData, f"%{searchData}%", searchData, 
                        searchData, f"%{searchData}%", f"%{searchData}%", 
                        f"%{searchData}%", f"%{searchData}%", f"%{searchData}%", 
                        searchData, searchData, searchData, 
                        searchData, searchData,searchData,searchData,searchData
                    )

                query = """
                        SELECT OrderNo,OrderDate, OrderTime,  Party,Email,ContactNo, BillingAddress,State ,Items, HSNCode, Qty, Price, Tax,TaxAmount,Total ,PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                        FROM SalesMaster 
                        WHERE OrderDate LIKE %s 
                        OR Party LIKE %s 
                        OR OrderNo::text = %s 
                        OR BillingAddress LIKE %s 
                        OR OrderTime = %s 
                        OR State = %s 
                        OR Items LIKE %s 
                        OR HSNCode LIKE %s 
                        OR Qty LIKE %s 
                        OR Price LIKE %s 
                        OR Tax = %s 
                        OR TaxAmount = %s 
                        OR Total = %s 
                        OR PaymentType = %s 
                        OR Discount::text = %s 
                        OR TotalAmount::text = %s 
                        OR AdvAmount::text = %s 
                        OR TotalBalance::text = %s
                        OR CurrentBalance::text = %s
                        """
                c.execute(query, parameters)
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
 
    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoItems(self):
        ItemsWindow=mainAdminSaleApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(ItemsWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class AddSaleApp(QtWidgets.QDialog, DraggableMixin,AddSale_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(AddSaleApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.comboBoxes = []
        self.oldBalance=0.0
        self.loadData()
        self.partyLineEdit.editingFinished.connect(self.showBalAdd)
        self.searchLineEdit.textChanged.connect(self.filterComboBoxItems)
        self.discountLineEdit.textChanged.connect(self.updateDiscountedAmount)
        if self.advanceAmountLineEdit.textChanged:
            self.advanceAmountLineEdit.textChanged.connect(self.updateBalanceAmount)
        self.addRowButton.clicked.connect(self.AddRow)
        self.removeRowButton.clicked.connect(self.RemoveRow)
        self.okButton.clicked.connect(self.gotoAddSale)
        self.cancelButton.clicked.connect(self.gotoSalesOrders)
        self.okButton.setFocus()
        self.smtp_server_conn = None
        
        self.initializeFirstRow()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoAddSale()
        else:
            super(AddSaleApp, self).keyPressEvent(event)

    def loadData(self):
        self.dateLabel.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.timeLabel.setText(datetime.datetime.now().strftime("%I:%M %p"))
        conn = create_connection()
        c = conn.cursor()
        c.execute("""
            SELECT OrderNo
            FROM SalesMaster 
            ORDER BY OrderNo DESC LIMIT 1
        """)
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            last_order_no = int(result[0])
            new_order_no = last_order_no + 1
        else:
            new_order_no = 1
        self.orderNoLineEdit.setText(f"{new_order_no:03d}")

    def filterComboBoxItems(self):
        try:
            search_text = self.searchLineEdit.text().strip()
            for comboBox in self.comboBoxes:
                for i in range(comboBox.count()):
                    item = comboBox.model().item(i)
                    item_text = item.text()
                    comboBox.view().setRowHidden(i, search_text not in item_text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def itemChanged(self, spinBox):
        try: 
            self.tableWidget.blockSignals(True)
            row = self.tableWidget.indexAt(spinBox.pos()).row()
            quantity_item = spinBox.value()
            if quantity_item is not None and int(quantity_item)>0:
                quantity = int(quantity_item)
                price_item = self.tableWidget.item(row, 3)
                price = float(price_item.text()) if price_item and price_item.text()!='' else 0.0
                
                tax_item = self.tableWidget.item(row, 4)
                tax_rate_text = tax_item.text().strip('%') if tax_item and tax_item!="NA" else '0'
                tax_rate_numeric = float(re.search(r'\d+', tax_rate_text).group()) / 100 if re.search(r'\d+', tax_rate_text) else 0.0
                
                tax_amount = price * quantity * tax_rate_numeric
                
                total_amount = price * quantity + tax_amount
                
                tax_amount_item = self.tableWidget.item(row, 5)
                total_amount_item = self.tableWidget.item(row, 6)

                if tax_amount_item:
                    tax_amount_item.setText(f"{tax_amount:.2f}")
                if total_amount_item:
                    total_amount_item.setText(f"{total_amount:.2f}")

                total_amount_sum = sum(float(self.tableWidget.item(row, 6).text()) for row in range(self.tableWidget.rowCount()) if self.tableWidget.item(row, 6))
                self.totalLineEdit.setText(f"₹ {total_amount_sum:.2f}")
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def showBalAdd(self):
        try:
            party_name = self.partyLineEdit.text().strip()
            if party_name:
                conn = create_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT TotalBalance, BillingAddress ,Email,ContactNo
                    FROM SalesMaster 
                    WHERE Party LIKE %s 
                    ORDER BY ID DESC LIMIT 1
                """, (f"%{party_name}%",))
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    self.oldBalance, address,email,contact = result
                    self.balanceLabel.setText(f"Balance : ₹ {self.oldBalance}")
                    self.addressTextEdit.setPlainText(address)
                    self.emailLineEdit.setText(str(email))
                    self.contactLineEdit.setText(str(contact))
                else:
                    self.oldBalance=0.0
                    self.balanceLabel.setText("Old Balance : ₹ 0.0")
                    self.addressTextEdit.clear()
                    self.emailLineEdit.clear()
                    self.contactLineEdit.clear()
            else:
                self.oldBalance=0.0
                self.balanceLabel.clear()
                self.addressTextEdit.clear()
                self.emailLineEdit.clear()
                self.contactLineEdit.clear()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightAddRowButton(self):
        originalStyleSheet = self.addRowButton.styleSheet()
        self.addRowButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.addRowButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightRemoveRowButton(self):
        originalStyleSheet = self.removeRowButton.styleSheet()
        self.removeRowButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.removeRowButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def initializeFirstRow(self):
        try:
            self.tableWidget.setRowCount(1)
            items = self.fetchItemsFromDatabase()

            comboBox = QtWidgets.QComboBox()
            self.font = QtGui.QFont()
            self.font.setFamily("Dubai")
            self.font.setPointSize(12)
            comboBox.setFont(self.font)
            comboBox.setPlaceholderText("Select Item")
            comboBox.addItems(items)
            comboBox.currentTextChanged.connect(lambda text, combo=comboBox: self.updateColumnValues(combo))

            self.comboBoxes.append(comboBox)
            self.tableWidget.blockSignals(True)
            self.tableWidget.setCellWidget(0, 0, comboBox)
            for col in range(7):
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(0, col, item)
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def AddRow(self):
        try:
            if self.tableWidget.rowCount() > 0:
                last_row_combo = self.tableWidget.cellWidget(self.tableWidget.rowCount() - 1, 0)
                if not last_row_combo or last_row_combo.currentIndex() == -1:
                    self.highlightAddRowButton()
                    return
                
            self.searchLineEdit.clear()
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

            items = self.fetchItemsFromDatabase() 

            comboBox = QtWidgets.QComboBox()
            self.font = QtGui.QFont()
            self.font.setFamily("Dubai")
            self.font.setPointSize(12)
            comboBox.setFont(self.font)
            comboBox.setPlaceholderText("Select Item")
            comboBox.addItems(items)
            comboBox.currentTextChanged.connect(lambda text,combo=comboBox: self.updateColumnValues(combo))
            
            self.comboBoxes.append(comboBox)
            self.tableWidget.blockSignals(True)
            self.tableWidget.setCellWidget(row_position, 0, comboBox)
            for col in range(7):
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(row_position, col, item)
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def fetchItemsFromDatabase(self):
        items = []
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT ItemName FROM ItemMaster ORDER BY ItemName ASC")
            rows = c.fetchall()
            c.close()
            conn.close()
            
            for row in rows:
                item_name = row[0]
                items.append(item_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
        return items

    def updateColumnValues(self, comboBox):
        item_name=None
        self.tableWidget.blockSignals(True)
        row_position = self.tableWidget.indexAt(comboBox.pos()).row()
        item_name = comboBox.currentText()
        spinbox = QtWidgets.QSpinBox()
        spinbox.setMinimum(1)
        spinbox.setFont(self.font)
        self.tableWidget.setCellWidget(row_position, 2, spinbox)
        spinbox.valueChanged.connect(lambda value,spin=spinbox: self.itemChanged(spin))

        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT HSN, SalePrice,StockQuantity, TaxRate, InclusiveOfTax FROM ItemMaster WHERE ItemName=%s", (item_name,))
            row = c.fetchone()
            c.close()
            conn.close()

            if row:
                self.tableWidget.item(row_position, 1).setText('') 
                self.tableWidget.item(row_position, 3).setText('') 
                self.tableWidget.item(row_position, 4).setText('') 
                self.tableWidget.item(row_position, 5).setText('') 
                self.tableWidget.item(row_position, 6).setText('') 
                hsn, sale_price,stock_qty, tax_rate ,inclusive_of_tax= row
                sale_price=float(sale_price)
                self.tableWidget.item(row_position, 1).setText(str(hsn))
                if stock_qty>0:
                    spinbox.setMaximum(int(stock_qty))
                    self.tableWidget.item(row_position, 3).setText(str(sale_price))


                    if inclusive_of_tax == "Yes":
                        tax_rate_numeric = float(re.search(r'\d+', tax_rate).group()) / 100
                        self.tableWidget.item(row_position, 4).setText(str(tax_rate))
                    else:
                        self.tableWidget.item(row_position, 4).setText("NA")
                        tax_rate_numeric=0.0
                    
                    
                    tax_amount = sale_price  * tax_rate_numeric
                    
                    total_amount = sale_price + tax_amount
                    
                    self.tableWidget.item(row_position, 5).setText(str(f"{tax_amount:.2f}"))
                    
                    self.tableWidget.item(row_position, 6).setText(str(f"{total_amount:.2f}"))
                    self.updateTotalAmount()
                else:
                    spinbox.setMaximum(0)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        self.tableWidget.blockSignals(False)
    
    def updateTotalAmount(self):
        try:
            total = 0.0
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 6)
                if item and item.text() and item.text()!='':
                    total += float(item.text())
                else:
                    total += 0.0
            self.totalLineEdit.setText(str(f"₹ {total:.2f}"))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def updateDiscountedAmount(self):
        try:
            discount_text = self.discountLineEdit.text().strip()

            if discount_text.endswith('%'):
                discount_text = discount_text[:-1].strip() or discount_text.rstrip('%')
                if discount_text:
                    discount_percentage = float(discount_text) / 100
            elif discount_text in ['',' '] or discount_text.isspace():
                discount_percentage=0.0
            else:
                discount_percentage = float(discount_text) / 100
            self.tableWidget.blockSignals(True)
            total_amount_sum = sum(float(self.tableWidget.item(row, 6).text()) for row in range(self.tableWidget.rowCount()))
            self.tableWidget.blockSignals(False)
            discounted_amount = total_amount_sum * (1 - discount_percentage)
            balance_amount=discounted_amount+self.oldBalance
            
            self.totalLineEdit.setText(f"₹ {discounted_amount:.2f}")
            self.balanceAmountLineEdit.setText(f"₹ {balance_amount:.2f}")
            self.currentBalanceAmountLineEdit.setText(f"₹ {discounted_amount:.2f}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def updateBalanceAmount(self):
        try:
            advance_amount_text = self.advanceAmountLineEdit.text().strip()
            total_amount_text = self.totalLineEdit.text().strip()

            total_amount_text = total_amount_text.replace('₹ ', '').strip()

            if total_amount_text:
                total_amount = float(total_amount_text)
            else:
                print("Error: Total amount must contain only numeric characters.")
                return
            
            if advance_amount_text == '' or advance_amount_text.isspace() or advance_amount_text == None:
                advance_amount = 0.0
            elif advance_amount_text:
                advance_amount = float(advance_amount_text)
            else:
                print("Error: Advance amount must contain only numeric characters.")
                return
            balance_amount = max(total_amount - advance_amount + self.oldBalance,0)
            currbalance = max(total_amount - advance_amount,0)
            self.balanceAmountLineEdit.setText(f"₹ {balance_amount:.2f}")
            self.currentBalanceAmountLineEdit.setText(f"₹ {currbalance:.2f}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def RemoveRow(self):
        self.tableWidget.blockSignals(True)
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if selected_rows:
            for selected_row in selected_rows:
                self.tableWidget.removeRow(selected_row.row())
            self.updateTotalAmount()
        else:
            self.highlightRemoveRowButton()
        self.tableWidget.blockSignals(False)

    def gatherSalesData(self):
        try:
            items = []
            hsns = []
            qtys = []
            prices = []
            taxes = []
            taxesamt = []
            taxtotal = []

            for row in range(self.tableWidget.rowCount()):
                item_combo = self.tableWidget.cellWidget(row, 0)
                hsn_item = self.tableWidget.item(row, 1)
                qty_spinbox = self.tableWidget.cellWidget(row, 2)
                price_item = self.tableWidget.item(row, 3)
                tax_item = self.tableWidget.item(row, 4)
                tax_amt_item = self.tableWidget.item(row, 5)
                total_item = self.tableWidget.item(row, 6)

                items.append(item_combo.currentText() if item_combo else '')
                hsns.append(hsn_item.text() if hsn_item else '')
                qtys.append(qty_spinbox.value() if qty_spinbox else '')
                prices.append(price_item.text() if price_item else '')
                taxes.append(tax_item.text() if tax_item else '')
                taxesamt.append(tax_amt_item.text() if tax_amt_item else '')
                taxtotal.append(total_item.text() if total_item else '')

            return [items, hsns, qtys, prices, taxes, taxesamt, taxtotal]
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            return []

    def gotoAddSale(self):
        try:
            party = self.partyLineEdit.text().strip()
            ba = self.addressTextEdit.toPlainText().strip()
            cno = self.contactLineEdit.text()
            eml = self.emailLineEdit.text().strip()
            if not bool(re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", eml)):
                self.emailLineEdit.clear()
                self.highlightButton()
                return
            orderNo = self.orderNoLineEdit.text()
            orderdate = self.dateLabel.text()
            ordertime = self.timeLabel.text()
            state = self.soSComboBox.currentText()
            payment = self.paymentTypeComboBox.currentText()
            discount = int(self.discountLineEdit.text().rstrip('%'))
            total = self.totalLineEdit.text()
            numeric_total = float(''.join(re.findall(r'\d+\.?\d*', total)))
            adcAmt = self.advanceAmountLineEdit.text()
            numeric_adcAmt = float(''.join(re.findall(r'\d+\.?\d*', adcAmt)))
            balance = self.balanceAmountLineEdit.text()
            currbalance = self.currentBalanceAmountLineEdit.text()
            numeric_balance = float(''.join(re.findall(r'\d+\.?\d*', balance)))
            numeric_current_balance = float(''.join(re.findall(r'\d+\.?\d*', currbalance)))

            sales_data = self.gatherSalesData()

            if not party or not ba or not cno or not eml or not orderNo or not state or not payment or not sales_data[0] or not sales_data[2]:
                self.highlightButton()
                return

            try:
                conn = create_connection()
                c = conn.cursor()
                c.execute("INSERT INTO SalesMaster (Party,Email,ContactNo, BillingAddress, OrderNo, OrderDate,OrderTime,State, Items, HSNCode, Qty, Price, Tax, TaxAmount,Total,PaymentType, Discount, TotalAmount, AdvAmount, TotalBalance,CurrentBalance) VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                        (party, eml, cno, ba, orderNo, orderdate, ordertime, state, ', '.join(sales_data[0]), ', '.join(sales_data[1]), ', '.join(map(str, sales_data[2])), ', '.join(sales_data[3]), ', '.join(sales_data[4]), ', '.join(sales_data[5]), ', '.join(sales_data[6]), payment, discount, numeric_total, numeric_adcAmt, numeric_balance, numeric_current_balance))

                for item, qty in zip(sales_data[0], sales_data[2]):
                    c.execute("UPDATE ItemMaster SET StockQuantity = StockQuantity - %s WHERE ItemName = %s", (qty, item.strip()))
                log_db_operation(c,self.Eid,f"has enrolled new Sale to {party}")
                conn.commit()
                c.execute("SELECT Name, Phno, Address, District, State, Email, Password FROM CompanyDetails ORDER BY ID DESC")
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    CName, CPhno, CAddress, CDistrict, CState, CEmail, CPassword = result
                else:
                    CName, CPhno, CAddress, CDistrict, CState, CEmail, CPassword = '', '', '', '', '', '', ''
                
                data = {
                    'CName': CName,
                    'CPhno': CPhno,
                    'CEmail': CEmail,
                    'CAddress': CAddress,
                    'CDistrict': CDistrict,
                    'CState': CState,
                    'orderDate': orderdate,
                    'orderTime': ordertime,
                    'orderNo': orderNo,
                    'todayDate': datetime.datetime.now().strftime('%Y-%m-%d'),
                    'Party': party,
                    'ContactNo': cno,
                    'Email': eml,
                    'BillingAddress': ba,
                    'State': state,
                    'items': [{'sno': i + 1, 'item': sales_data[0][i], 'hsn': sales_data[1][i], 'qty': sales_data[2][i], 'price': sales_data[3][i], 'tax': sales_data[4][i], 'taxAmount': sales_data[5][i], 'total': sales_data[6][i]} for i in range(len(sales_data[0]))],
                    'Discount': f"{discount}%",
                    'Total': total,
                    'PaymentType': payment,
                    'AdvAmount': adcAmt,
                    'CurrentBalance': currbalance
                }

                env = Environment(loader=FileSystemLoader(resource_path('')))
                template = env.get_template('Sales.html')
                output_text = template.render(data)

                self.send_email_with_invoice(eml,CEmail,CPassword ,output_text)

            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoSalesOrders()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def send_email_with_invoice(self,to_address, CEmail,CPassword,invoice):      
        msg = MIMEMultipart()
        msg['From'] = CEmail
        msg['To'] = to_address
        msg['Subject'] = 'Your Purchase Confirmation and Invoice'

        html_content = f"""
                        <html>
                        <head>
                        <style>
                            body {{
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                            }}
                            .container {{
                                width: 100%;
                                margin: 0 auto;
                                padding: 20px;
                                background-color: #f9f9f9;
                            }}
                            .content {{
                                background-color: #ffffff;
                                padding: 20px;
                                border: 1px solid #dddddd;
                            }}
                            h1 {{
                                color: #333333;
                            }}
                            p {{
                                color: #666666;
                            }}
                            table {{
                                width: 100%;
                                border-collapse: collapse;
                            }}
                            th, td {{
                                padding: 10px;
                                border: 1px solid #dddddd;
                            }}
                        </style>
                        </head>
                        <body>
                            <div class="container">
                                <div class="content">
                                    {invoice}
                                </div>
                            </div>
                        </body>
                        </html>
                        """
        
        msg.attach(MIMEText(html_content, 'html'))

        try:
            if check_internet_connection() and self.smtp_server_conn is None:
                try:
                    self.smtp_server_conn = smtplib.SMTP('smtp.gmail.com',587)
                    self.smtp_server_conn.starttls()
                    self.smtp_server_conn.login(CEmail,CPassword)
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            elif check_internet_connection() and self.smtp_server_conn is not None:
                try:
                    self.smtp_server_conn.sendmail(CEmail, to_address, msg.as_string())
                    QtWidgets.QMessageBox.information(self, "Success", f"Confirmation Mail sent to {to_address}")
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Error", f"Failed to send email: {e}")
            else:
                QtWidgets.QMessageBox.critical(self, "Error", "No internet connection - Send Confirmation Manually")
                return
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoSalesOrders(self):
        self.reject()

class mainAdminPurchaseOrdersApp(QtWidgets.QMainWindow,AdminPurchaseOrders_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminPurchaseOrdersApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))
        
        self.loadData()
        self.reloadButton.clicked.connect(self.gotoReload)
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.addPurchaseButton.clicked.connect(self.gotoAddPurchase)
        self.exportButton.clicked.connect(self.gotoExport)
        self.itemsButton.clicked.connect(self.gotoItems)
        self.searchButton.clicked.connect(self.gotoSearch)
        self.searchLineEdit.editingFinished.connect(self.gotoSearch)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)

    def loadData(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            query = """
                SELECT OrderNo, OrderDate, OrderTime, Party, Email,ContactNo, BillingAddress, State, Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                FROM PurchaseMaster
                ORDER BY ID DESC;
                """
            c.execute(query)
            inference = c.fetchall()
            row_count = len(inference)
            self.tableWidget.setRowCount(row_count)
            self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

            for tablerow, row in enumerate(inference):
                self.populateRow(tablerow, row)
            c.close()
            conn.close()
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def populateRow(self,tablerow,row):
        for col in range(22):
            if col in {17, 18, 19,20}:
                text = f"₹ {row[col]}"
            elif col == 16:
                text = f"{row[col]} %"
            elif col == 21:
                self.addPreviewButton(tablerow, col, "Preview", str(row[17]), self.Ename, self.Erole)
                continue
            else:
                cell_text = str(row[col])
                if ', ' in cell_text and col!=6:
                    item = ListViewInCellWidget(cell_text)
                    self.tableWidget.setCellWidget(tablerow, col, item)
                    continue
                else:
                    text = cell_text
            
            item = QtWidgets.QTableWidgetItem(text)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tableWidget.setItem(tablerow, col, item)
            self.tableWidget.update()
            self.tableWidget.resizeRowToContents(tablerow)

    def addPreviewButton(self, row, col, text, Id, Ename, Erole):
        button = QtWidgets.QPushButton(str(text))
        font = QtGui.QFont()
        font.setFamily("Dubai")
        font.setPointSize(12)
        font.setBold(True)
        button.setFont(font)
        button.setObjectName("cellPreviewButton")
        button.setProperty('row', row)
        button.clicked.connect(self.gotoPreview)
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(button)
        layout.setContentsMargins(0, 0, 0, 0)
        container = QtWidgets.QWidget()
        container.setLayout(layout)
        self.tableWidget.setCellWidget(row, col, container)
        self.tableWidget.resizeRowToContents(row)

    def getCellWidgetText(self, row, col):
        widget = self.tableWidget.cellWidget(row, col)
        if widget and isinstance(widget, ListViewInCellWidget):
            return widget.getText()
        elif self.tableWidget.item(row, col):
            return self.tableWidget.item(row, col).text()
        else:
            return ''

    def gotoPreview(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT Name, Phno, Address, District, State, Email FROM CompanyDetails ORDER BY ID DESC")
            result = c.fetchone()
            c.close()
            conn.close()
            if result:
                CName, CPhno, CAddress, CDistrict, CState, CEmail = result
            else:
                CName, CPhno, CAddress, CDistrict, CState, CEmail = '', '', '', '', '', ''
            button = self.sender()
            row = button.property('row')  

            orderDate = self.tableWidget.item(row, 1).text() if self.tableWidget.item(row, 1) else ''
            orderTime = self.tableWidget.item(row, 2).text() if self.tableWidget.item(row, 2) else ''
            orderNo = self.tableWidget.item(row, 0).text() if self.tableWidget.item(row, 0) else ''
            todayDate = datetime.datetime.now().strftime('%Y-%m-%d')
            Party = self.tableWidget.item(row, 3).text() if self.tableWidget.item(row, 3) else ''
            ContactNo = self.tableWidget.item(row, 5).text() if self.tableWidget.item(row, 5) else ''
            Email = self.tableWidget.item(row, 4).text() if self.tableWidget.item(row, 4) else ''
            BillingAddress = self.tableWidget.item(row, 6).text() if self.tableWidget.item(row, 6) else ''
            State = self.tableWidget.item(row, 7).text() if self.tableWidget.item(row, 7) else ''

            items_str = self.getCellWidgetText(row, 8) 
            hsn_str = self.getCellWidgetText(row, 9)
            qty_str = self.getCellWidgetText(row, 10)
            price_str = self.getCellWidgetText(row, 11)
            tax_str = self.getCellWidgetText(row, 12)
            taxAmount_str = self.getCellWidgetText(row, 13)
            total_str = self.getCellWidgetText(row, 14)


            items = items_str.split(', ') if ', ' in items_str else [items_str]
            hsn_codes = hsn_str.split(', ') if ', ' in hsn_str else [hsn_str]
            qtys = qty_str.split(', ') if ', ' in qty_str else [qty_str]
            prices = price_str.split(', ') if ', ' in price_str else [price_str]
            taxes = tax_str.split(', ') if ', ' in tax_str else [tax_str]
            taxAmounts = taxAmount_str.split(', ') if ', ' in taxAmount_str else [taxAmount_str]
            totals = total_str.split(', ') if ', ' in total_str else [total_str]

            lengths = [len(items), len(hsn_codes), len(qtys), len(prices), len(taxes), len(taxAmounts), len(totals)]
            if len(set(lengths)) != 1:
                raise ValueError(f"Mismatch in list lengths: {lengths}")

            item_details = []
            for i in range(len(items)):
                item_details.append({
                    'sno': i + 1,
                    'item': items[i],
                    'hsn': hsn_codes[i],
                    'qty': qtys[i],
                    'price': prices[i],
                    'tax': taxes[i],
                    'taxAmount': taxAmounts[i],
                    'total': totals[i]
                })
            Discount = self.tableWidget.item(row, 16).text() if self.tableWidget.item(row, 16) else ''
            Total = self.tableWidget.item(row, 17).text() if self.tableWidget.item(row, 17) else ''
            PaymentType = self.tableWidget.item(row, 15).text() if self.tableWidget.item(row, 15) else ''
            AdvAmount = self.tableWidget.item(row, 18).text() if self.tableWidget.item(row, 18) else ''
            CurrentBalance = self.tableWidget.item(row, 19).text() if self.tableWidget.item(row, 19) else ''

            data = {
                'CName': CName,
                'CPhno': CPhno,
                'CEmail': CEmail,
                'CAddress': CAddress,
                'CDistrict': CDistrict,
                'CState': CState,
                'orderDate': orderDate,
                'orderTime': orderTime,
                'orderNo': orderNo,
                'todayDate': todayDate,
                'Party': Party,
                'ContactNo': ContactNo,
                'Email': Email,
                'BillingAddress': BillingAddress,
                'State': State,
                'items': item_details,
                'Discount': Discount,
                'Total': Total,
                'PaymentType': PaymentType,
                'AdvAmount': AdvAmount,
                'CurrentBalance': CurrentBalance
            }

            env = Environment(loader=FileSystemLoader(resource_path('')))
            template = env.get_template('Purchases.html')
            output_text = template.render(data)
            
            output_html = 'Purchase Invoice.html'
            with open(output_html, 'w', encoding='utf-8') as file:
                file.write(output_text)
                file_path = resource_path(output_html)
            
            webbrowser.open(f'file://{file_path}')
            time.sleep(5)
            try:
                while True:
                    os.remove(file_path)
                    break
            except PermissionError:
                time.sleep(5)

        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoExport(self):
        try:
            columnHeaders = []

            for j in range(self.tableWidget.model().columnCount()):
                columnHeaders.append(self.tableWidget.horizontalHeaderItem(j).text())

            df = pd.DataFrame(columns=columnHeaders)

            for row in range(self.tableWidget.rowCount()):
                for col in range(self.tableWidget.columnCount()):
                    widget = self.tableWidget.cellWidget(row, col)
                    if widget and isinstance(widget, ListViewInCellWidget):
                        df.at[row, columnHeaders[col]] = widget.getText()
                    else:
                        if self.tableWidget.item(row, col):
                            df.at[row, columnHeaders[col]] = self.tableWidget.item(row, col).text()
                        else:
                            df.at[row, columnHeaders[col]]= ""

            save_path, _ = QtWidgets.QFileDialog.getSaveFileName(None, "Save File", os.path.expanduser('~'), "Excel files (*.xlsx)")
            if save_path:
                df.to_excel(save_path, index=False)
                QtWidgets.QMessageBox.information(self, "Success", f"File saved to {save_path}")
                print(f"File saved to {save_path}")
            else:
                print("Export canceled by user.")
            print('Excel file exported')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoAddPurchase(self):
        AddPurchaseWindow=AddPurchaseApp(self.Eid,self.Ename,self.Erole)
        if not(AddPurchaseWindow.exec()) == QtWidgets.QDialog.rejected:
            self.gotoReload()

    def gotoSearch(self):
        try:
            searchData=self.searchLineEdit.text().strip()
            self.tableWidget.blockSignals(True)
            self.tableWidget.clearContents()
            conn=create_connection()
            c=conn.cursor()
            if not searchData:
                self.gotoReload()
            else:
                parameters = (
                        f"%{searchData}%", f"%{searchData}%", 
                        searchData, f"%{searchData}%", searchData, 
                        searchData, f"%{searchData}%", f"%{searchData}%", 
                        f"%{searchData}%", f"%{searchData}%", f"%{searchData}%", 
                        searchData, searchData, searchData, 
                        searchData, searchData,searchData,searchData,searchData
                    )

                query = """
                        SELECT OrderNo,OrderDate, OrderTime,  Party,Email,ContactNo, BillingAddress,State ,Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, CurrentBalance,TotalBalance,ID
                        FROM PurchaseMaster 
                        WHERE OrderDate LIKE %s 
                        OR Party LIKE %s 
                        OR OrderNo::text = %s 
                        OR BillingAddress LIKE %s 
                        OR OrderTime = %s 
                        OR State = %s 
                        OR Items LIKE %s 
                        OR HSNCode LIKE %s 
                        OR Qty LIKE %s 
                        OR Price LIKE %s 
                        OR Tax = %s 
                        OR TaxAmount = %s 
                        OR Total = %s 
                        OR PaymentType = %s 
                        OR Discount::text = %s 
                        OR TotalAmount::text = %s 
                        OR AdvAmount::text = %s 
                        OR TotalBalance::text = %s
                        OR CurrentBalance::text = %s
                        """
                c.execute(query, parameters)
                inference = c.fetchall()
                row_count = len(inference)
                self.tableWidget.setRowCount(row_count)
                self.tableWidget.setStyleSheet("QTableWidget::item {border: 1px solid transparent; padding: 0px 2px;}")

                for tablerow, row in enumerate(inference):
                    self.populateRow(tablerow, row)
            c.close()
            conn.close()
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def gotoReload(self):
        self.searchLineEdit.clear()
        self.tableWidget.blockSignals(True)
        self.tableWidget.clearContents()
        self.loadData()
        self.tableWidget.blockSignals(False)

    def gotoItems(self):
        ItemsWindow=mainAdminSaleApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(ItemsWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

class AddPurchaseApp(QtWidgets.QDialog, DraggableMixin,AddPurchase_Ui_Form):
    def __init__(self,Eid,Ename,Erole):
        super(AddPurchaseApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.comboBoxes = []
        self.oldBalance=0.0
        self.loadData()
        self.partyLineEdit.editingFinished.connect(self.showBalAdd)
        self.searchLineEdit.textChanged.connect(self.filterComboBoxItems)
        self.discountLineEdit.textChanged.connect(self.updateDiscountedAmount)
        if self.advanceAmountLineEdit.textChanged:
            self.advanceAmountLineEdit.textChanged.connect(self.updateBalanceAmount)
        self.addRowButton.clicked.connect(self.AddRow)
        self.removeRowButton.clicked.connect(self.RemoveRow)
        self.okButton.clicked.connect(self.gotoAddPurchase)
        self.cancelButton.clicked.connect(self.gotoPurchaseOrders)
        self.okButton.setFocus()
        
        self.initializeFirstRow()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.widget.width()
        current_widget_height = self.widget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.widget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Return or event.key() == QtCore.Qt.Key.Key_Enter:
            self.gotoAddPurchase()
        else:
            super(AddPurchaseApp, self).keyPressEvent(event)

    def loadData(self):
        self.dateLabel.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
        self.timeLabel.setText(datetime.datetime.now().strftime("%I:%M %p"))
        conn = create_connection()
        c = conn.cursor()
        c.execute("""
            SELECT OrderNo
            FROM PurchaseMaster 
            ORDER BY OrderNo DESC LIMIT 1
        """)
        result = c.fetchone()
        c.close()
        conn.close()
        if result:
            last_order_no = int(result[0])
            new_order_no = last_order_no + 1
        else:
            new_order_no = 1
        self.orderNoLineEdit.setText(f"{new_order_no:03d}")

    def filterComboBoxItems(self):
        try:
            search_text = self.searchLineEdit.text().strip()
            for comboBox in self.comboBoxes:
                for i in range(comboBox.count()):
                    item = comboBox.model().item(i)
                    item_text = item.text()
                    comboBox.view().setRowHidden(i, search_text not in item_text)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def itemChanged(self, spinBox):
        try:
            self.tableWidget.blockSignals(True)
            row = self.tableWidget.indexAt(spinBox.pos()).row()
            quantity_item = spinBox.value()
            if quantity_item is not None:
                quantity = int(quantity_item)
                
                price_item = self.tableWidget.item(row, 3)
                price = float(price_item.text()) if price_item and price_item.text()!='' else 0.0
                
                tax_item = self.tableWidget.item(row, 4)
                tax_rate_text = tax_item.text().strip('%') if tax_item and tax_item!="NA" else '0'
                tax_rate_numeric = float(re.search(r'\d+', tax_rate_text).group()) / 100 if re.search(r'\d+', tax_rate_text) else 0.0
                
                tax_amount = price * quantity * tax_rate_numeric
                
                total_amount = price * quantity + tax_amount
                
                tax_amount_item = self.tableWidget.item(row, 5)
                total_amount_item = self.tableWidget.item(row, 6)

                if tax_amount_item:
                    tax_amount_item.setText(f"{tax_amount:.2f}")
                if total_amount_item:
                    total_amount_item.setText(f"{total_amount:.2f}")

                total_amount_sum = sum(float(self.tableWidget.item(row, 6).text()) for row in range(self.tableWidget.rowCount()))
                self.totalLineEdit.setText(f"₹ {total_amount_sum:.2f}")
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def showBalAdd(self):
        try:
            party_name = self.partyLineEdit.text().strip()
            if party_name:
                conn = create_connection()
                c = conn.cursor()
                c.execute("""
                    SELECT TotalBalance, BillingAddress ,Email,ContactNo
                    FROM PurchaseMaster 
                    WHERE Party LIKE %s 
                    ORDER BY ID DESC LIMIT 1
                """, (f"%{party_name}%",))
                result = c.fetchone()
                c.close()
                conn.close()
                if result:
                    self.oldBalance, address,email,contact = result
                    self.balanceLabel.setText(f"Old Balance : ₹ {self.oldBalance}")
                    self.addressTextEdit.setPlainText(address)
                    self.emailLineEdit.setText(str(email))
                    self.contactLineEdit.setText(str(contact))
                else:
                    self.oldBalance=0.0
                    self.balanceLabel.setText("Old Balance : ₹ 0.0")
                    self.addressTextEdit.clear()
                    self.emailLineEdit.clear()
                    self.contactLineEdit.clear()
            else:
                self.oldBalance=0.0
                self.balanceLabel.clear()
                self.addressTextEdit.clear()
                self.emailLineEdit.clear()
                self.contactLineEdit.clear()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
     
    def highlightButton(self):
        originalStyleSheet = self.okButton.styleSheet()
        self.okButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.okButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)
    
    def highlightError(self,error):
        originalStyleSheet = error.styleSheet()
        error.setStyleSheet("background-color:rgba(255, 0, 0, 0); border:2px solid rgba(0, 0, 0, 0); border-bottom-color:rgba(255, 82, 101, 200); color:rgb(0, 0, 0); padding-bottom:7px;")
        error.clear()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: error.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightAddRowButton(self):
        originalStyleSheet = self.addRowButton.styleSheet()
        self.addRowButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.addRowButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def highlightRemoveRowButton(self):
        originalStyleSheet = self.removeRowButton.styleSheet()
        self.removeRowButton.setStyleSheet("background-color: #CB0000;")
        timer = QtCore.QTimer(self)
        timer.timeout.connect(lambda: self.removeRowButton.setStyleSheet(originalStyleSheet))
        timer.setSingleShot(True)
        timer.start(2000)

    def initializeFirstRow(self):
        try:
            self.tableWidget.setRowCount(1)
            items = self.fetchItemsFromDatabase()

            comboBox = QtWidgets.QComboBox()
            self.font = QtGui.QFont()
            self.font.setFamily("Dubai")
            self.font.setPointSize(12)
            comboBox.setFont(self.font)
            comboBox.setPlaceholderText("Select Item")
            comboBox.addItems(items)
            comboBox.currentTextChanged.connect(lambda text, combo=comboBox: self.updateColumnValues(combo))


            self.comboBoxes.append(comboBox)
            self.tableWidget.blockSignals(True)
            self.tableWidget.setCellWidget(0, 0, comboBox)
            for col in range(7):
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(0, col, item)
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def AddRow(self):
        try:
            if self.tableWidget.rowCount() > 0:
                last_row_combo = self.tableWidget.cellWidget(self.tableWidget.rowCount() - 1, 0)
                if not last_row_combo or last_row_combo.currentIndex() == -1:
                    self.highlightAddRowButton()
                    return
                
            self.searchLineEdit.clear()
            row_position = self.tableWidget.rowCount()
            self.tableWidget.insertRow(row_position)

            items = self.fetchItemsFromDatabase() 

            comboBox = QtWidgets.QComboBox()
            self.font = QtGui.QFont()
            self.font.setFamily("Dubai")
            self.font.setPointSize(12)
            comboBox.setFont(self.font)
            comboBox.setPlaceholderText("Select Item")
            comboBox.addItems(items)
            comboBox.currentTextChanged.connect(lambda text,combo=comboBox: self.updateColumnValues(combo))
            
            self.comboBoxes.append(comboBox)
            self.tableWidget.blockSignals(True)
            self.tableWidget.setCellWidget(row_position, 0, comboBox)
            for col in range(7):
                item = QtWidgets.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(row_position, col, item)
            self.tableWidget.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def fetchItemsFromDatabase(self):
        items = []
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT ItemName FROM ItemMaster ORDER BY ItemName ASC")
            rows = c.fetchall()
            c.close()
            conn.close()
            
            for row in rows:
                item_name = row[0]
                items.append(item_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
        return items
    
    def updateColumnValues(self, comboBox):
        item_name=None
        self.tableWidget.blockSignals(True)
        row_position = self.tableWidget.indexAt(comboBox.pos()).row()
        item_name = comboBox.currentText()
        spinbox = QtWidgets.QSpinBox()
        spinbox.setMinimum(1)
        spinbox.setMaximum(999999)
        spinbox.setFont(self.font)
        self.tableWidget.setCellWidget(row_position, 2, spinbox)
        spinbox.valueChanged.connect(lambda value,spin=spinbox: self.itemChanged(spin))


        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT HSN, PurchasePrice,TaxRate, InclusiveOfTax FROM ItemMaster WHERE ItemName=%s", (item_name,))
            row = c.fetchone()
            c.close()
            conn.close()

            if row:
                self.tableWidget.item(row_position, 1).setText('') 
                self.tableWidget.item(row_position, 3).setText('') 
                self.tableWidget.item(row_position, 4).setText('') 
                self.tableWidget.item(row_position, 5).setText('') 
                self.tableWidget.item(row_position, 6).setText('') 
                hsn, purchase_price,tax_rate, inclusive_of_tax  = row
                self.tableWidget.item(row_position, 1).setText(str(hsn))

                price_item = self.tableWidget.item(row_position, 3)
                tax_item = self.tableWidget.item(row_position, 4)

                price_item.setText(str(purchase_price))
                price_item.setFlags(price_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

                if inclusive_of_tax == "Yes":
                    tax_item.setText(str(tax_rate))
                else:
                    tax_item.setText("NA")
                    tax_rate="0"
                tax_item.setFlags(tax_item.flags() | QtCore.Qt.ItemFlag.ItemIsEditable)

                self.tableWidget.itemDelegate().closeEditor.connect(self.onItemEditingFinished)
                self.calculateAndSetAmounts(row_position, purchase_price, tax_rate)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        self.tableWidget.blockSignals(False)
    
    def onItemEditingFinished(self, editor, hint):
        try:
            index = self.tableWidget.currentIndex()
            if index.column() == 3:
                row_position = index.row()
                price_item = self.tableWidget.item(row_position, 3)
                if price_item:
                    purchase_price = float(price_item.text())
                    tax_item = self.tableWidget.item(row_position, 4)
                    tax_rate = tax_item.text().strip()
                    self.calculateAndSetAmounts(row_position, purchase_price, tax_rate)
            elif index.column()==4:
                row_position = index.row()
                purchase_price = self.tableWidget.item(row_position, 3)
                tax_item = self.tableWidget.item(row_position, 4)
                if purchase_price and tax_item:
                    purchase_price = float(purchase_price.text())      
                    tax_item = tax_item.text()
                    self.calculateAndSetAmounts(row_position, purchase_price, tax_item)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def calculateAndSetAmounts(self, row_position, purchase_price, tax_rate):
        try:
            if tax_rate != "0" and re.search(r'\d+', tax_rate):
                tax_rate_numeric = float(re.search(r'\d+', tax_rate).group()) / 100
            else:
                tax_rate_numeric = 0


            spin_box = self.tableWidget.cellWidget(row_position, 2)
            quantity = spin_box.value() if spin_box else 1

            tax_amount = purchase_price * quantity * tax_rate_numeric
            total_amount = purchase_price * quantity + tax_amount

            gst_item = self.tableWidget.item(row_position, 5)
            total_amount_item = self.tableWidget.item(row_position, 6)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

        if gst_item:
            gst_item.setText(f"{tax_amount:.2f}")
        if total_amount_item:
            total_amount_item.setText(f"{total_amount:.2f}")
        self.updateTotalAmount()
    
    def updateTotalAmount(self):
        try:
            total = 0.0
            for row in range(self.tableWidget.rowCount()):
                item = self.tableWidget.item(row, 6)
                if item and item.text():
                    total += float(item.text())
                else:
                    total += 0.0
            self.totalLineEdit.setText(str(f"₹ {total:.2f}"))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def updateDiscountedAmount(self):
        try:
            discount_text = self.discountLineEdit.text().strip()

            if discount_text.endswith('%'):
                discount_text = discount_text[:-1].strip() or discount_text.rstrip('%')
                if discount_text:
                    discount_percentage = float(discount_text) / 100
            elif discount_text in ['',' '] or discount_text.isspace():
                discount_percentage=0.0
            else:
                discount_percentage = float(discount_text) / 100
            self.tableWidget.blockSignals(True)
            total_amount_sum = sum(float(self.tableWidget.item(row, 6).text()) for row in range(self.tableWidget.rowCount()))
            self.tableWidget.blockSignals(False)
            discounted_amount = total_amount_sum * (1 - discount_percentage)
            balance_amount=discounted_amount+self.oldBalance
            
            self.totalLineEdit.setText(f"₹ {discounted_amount:.2f}")
            self.balanceAmountLineEdit.setText(f"₹ {balance_amount:.2f}")
            self.currentBalanceAmountLineEdit.setText(f"₹ {discounted_amount:.2f}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
    
    def updateBalanceAmount(self):
        try:
            advance_amount_text = self.advanceAmountLineEdit.text().strip()
            total_amount_text = self.totalLineEdit.text().strip()

            total_amount_text = total_amount_text.replace('₹ ', '').strip()

            if total_amount_text:
                total_amount = float(total_amount_text)
            else:
                print("Error: Total amount must contain only numeric characters.")
                return
            
            if advance_amount_text == '' or advance_amount_text.isspace():
                advance_amount = 0.0
            elif advance_amount_text:
                advance_amount = float(advance_amount_text)
            else:
                print("Error: Advance amount must contain only numeric characters.")
                return
            balance_amount = max(total_amount - advance_amount + self.oldBalance,0)
            currbalance = max(total_amount - advance_amount,0)
            self.balanceAmountLineEdit.setText(f"₹ {balance_amount:.2f}")
            self.currentBalanceAmountLineEdit.setText(f"₹ {currbalance:.2f}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def RemoveRow(self):
        self.tableWidget.blockSignals(True)
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if selected_rows:
            for selected_row in selected_rows:
                self.tableWidget.removeRow(selected_row.row())
            self.updateTotalAmount()
        else:
            self.highlightRemoveRowButton()
        self.tableWidget.blockSignals(False)

    def gatherPurchaseData(self):
        try:
            items = []
            hsns = []
            qtys = []
            prices = []
            taxes = []
            taxesamt = []
            taxtotal = []

            self.tableWidget.blockSignals(True)
            for row in range(self.tableWidget.rowCount()):
                item_combo = self.tableWidget.cellWidget(row, 0)
                hsn_item = self.tableWidget.item(row, 1)
                qty_spinbox = self.tableWidget.cellWidget(row, 2)
                price_item = self.tableWidget.item(row, 3)
                tax_item = self.tableWidget.item(row, 4)
                tax_amt_item = self.tableWidget.item(row, 5)
                total_item = self.tableWidget.item(row, 6)

                items.append(item_combo.currentText() if item_combo else '')
                hsns.append(hsn_item.text() if hsn_item else '')
                qtys.append(qty_spinbox.value() if qty_spinbox else '')
                prices.append(price_item.text() if price_item else '')
                taxes.append(tax_item.text() if tax_item else '')
                taxesamt.append(tax_amt_item.text() if tax_amt_item else '')
                taxtotal.append(total_item.text() if total_item else '')

            self.tableWidget.blockSignals(False)
            return [items, hsns, qtys, prices, taxes, taxesamt, taxtotal]
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.tableWidget.blockSignals(False)
            return []

    def gotoAddPurchase(self):
        try:
            party=self.partyLineEdit.text().strip()
            ba=self.addressTextEdit.toPlainText().strip()
            cno=self.contactLineEdit.text()
            eml=self.emailLineEdit.text().strip()
            if not bool(re.match(r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*$", eml)):
                self.emailLineEdit.clear()
                self.highlightButton()
                return
            orderNo=self.orderNoLineEdit.text()
            orderdate=self.dateLabel.text()
            ordertime=self.timeLabel.text()
            state=self.soSComboBox.currentText()

            payment=self.paymentTypeComboBox.currentText()
            discount=self.discountLineEdit.text().rstrip('%')
            total=self.totalLineEdit.text()
            numeric_total = ''.join(re.findall(r'\d+\.?\d*', total))
            adcAmt=self.advanceAmountLineEdit.text()
            numeric_adcAmt = ''.join(re.findall(r'\d+\.?\d*', adcAmt))
            balance=self.balanceAmountLineEdit.text()
            currbalance=self.currentBalanceAmountLineEdit.text()
            numeric_balance = ''.join(re.findall(r'\d+\.?\d*', balance))
            numeric_current_balance = ''.join(re.findall(r'\d+\.?\d*', currbalance))

            purchase_data =self.gatherPurchaseData()

            if not party or not ba or not cno or not eml or not orderNo or not state or not payment or not purchase_data[0] or not purchase_data[2]:
                self.highlightButton()
                return
            
            try:
                conn=create_connection()
                c=conn.cursor()
                c.execute("INSERT INTO PurchaseMaster (Party, Email,ContactNo,BillingAddress, OrderNo, OrderDate,OrderTime,State, Items, HSNCode, Qty, Price, Tax,TaxAmount,Total, PaymentType, Discount, TotalAmount, AdvAmount, TotalBalance,CurrentBalance) VALUES (%s,%s,%s,%s,%s,%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)", 
                    (party,eml,cno, ba, orderNo,orderdate,ordertime, state,', '.join(purchase_data[0]), ', '.join(purchase_data[1]), ', '.join(map(str, purchase_data[2])), ', '.join(purchase_data[3]), ', '.join(purchase_data[4]), ', '.join(purchase_data[5]), ', '.join(purchase_data[6]), payment, discount, numeric_total, numeric_adcAmt, numeric_balance,numeric_current_balance))
                
                for item, qty,price,tax in zip(purchase_data[0], purchase_data[2], purchase_data[3], purchase_data[4]):
                    item = item.strip()
                    qty = int(qty)
                    price =float(price)
                    tax = tax.strip()
                    c.execute("UPDATE ItemMaster SET StockQuantity = StockQuantity + %s,PurchasePrice = %s,TaxRate = %s WHERE ItemName = %s", (qty,price,tax,item))
                log_db_operation(c,self.Eid,f"has enrolled new purchase from {party}")
                conn.commit()
                c.close()
                conn.close()
            except psycopg2.Error as e:
                QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            self.gotoPurchaseOrders()   
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoPurchaseOrders(self):
        self.reject()

class mainAdminSaleAnalyseApp(QtWidgets.QMainWindow,AdminSaleAnalysis_Ui_MainWindow):
    def __init__(self,Eid,Ename,Erole):
        super(mainAdminSaleAnalyseApp,self).__init__()
        self.setupUi(self)
        self.Eid=Eid
        self.Ename=Ename
        self.Erole=Erole
        self.nameLabel.setText(str(self.Ename))
        self.roleLabel.setText(str(self.Erole))

        self.executor = ThreadPoolExecutor(max_workers=10)
         
        self.logOutButton.clicked.connect(self.gotoLogout)
        self.debounce_timer = QtCore.QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(self.on_combobox_change)

        self.yearComboBox.currentTextChanged.connect(lambda: self.debounce_selection("year"))
        self.monthComboBox.currentTextChanged.connect(lambda: self.debounce_selection("month"))
        self.dailyComboBox.currentTextChanged.connect(lambda: self.debounce_selection("daily"))
        self.categoryComboBox.currentTextChanged.connect(self.update_chart)
        self.viewItemsButton.clicked.connect(self.gotoItems)

        self.itemComboBox = None
        self.reloadButton.clicked.connect(self.gotoReload)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.gotoReload)
        self.timer.start(60 * 60 * 1000)

        self.fetch_dates_and_items()

    def resizeEvent(self, event):
        window_width = self.width()
        window_height = self.height()

        current_widget_width = self.centralwidget.width()
        current_widget_height = self.centralwidget.height()

        window_center_x = window_width / 2
        window_center_y = window_height / 2

        
        offset_x = window_center_x - (current_widget_width / 2)
        offset_y = window_center_y - (current_widget_height / 2)

        self.centralwidget.setGeometry(
            int(offset_x),
            int(offset_y),
            current_widget_width,
            current_widget_height
        )

        super().resizeEvent(event)
 
    def gotoReload(self):
        self.categoryComboBox.blockSignals(True)
        self.yearComboBox.blockSignals(True)
        self.monthComboBox.blockSignals(True)
        self.dailyComboBox.blockSignals(True)
        self.categoryComboBox.setCurrentIndex(-1)
        self.yearComboBox.setCurrentIndex(-1)
        self.monthComboBox.setCurrentIndex(-1)
        self.dailyComboBox.setCurrentIndex(-1)
        self.categoryComboBox.blockSignals(False)
        self.monthComboBox.blockSignals(False)
        self.yearComboBox.blockSignals(False)
        self.dailyComboBox.blockSignals(False)
        if self.itemComboBox:
            self.horizontalLayout_2.removeWidget(self.itemComboBox)
            self.itemComboBox.deleteLater()
            self.itemComboBox = None
        self.axes.cla()
        self.canvas.draw()
        self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,'','',''))

    def gotoItems(self):
        AdminSaleWindow=mainAdminSaleApp(self.Eid,self.Ename,self.Erole)
        widget.addWidget(AdminSaleWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

    def debounce_selection(self, combo_type):
        self.selected_combo_type = combo_type
        self.debounce_timer.start(100)

    def on_combobox_change(self):
        try:
            if self.selected_combo_type == "year":
                self.gotoModChartYear(self.yearComboBox.currentText())
            elif self.selected_combo_type == "month":
                self.gotoModChartMonth(self.monthComboBox.currentText())
            elif self.selected_combo_type == "daily":
                if self.monthComboBox.currentText() == "" or self.monthComboBox.currentText() == "Select":
                    QtWidgets.QMessageBox.warning(self, "Selection Error", "Please select a month before choosing a day.")
                else:
                    self.gotoModChartDaily(self.monthComboBox.currentText(), self.dailyComboBox.currentText())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def fetch_dates_and_items(self):
        try:
            conn = create_connection()
            c = conn.cursor()
            c.execute("SELECT OrderDate FROM SalesMaster")
            sales_dates = [record[0] for record in c.fetchall()]

            c.execute("SELECT OrderDate FROM PurchaseMaster")
            purchases_dates = [record[0] for record in c.fetchall()]

            c.execute("SELECT Date FROM ItemMaster")
            item_dates = [record[0] for record in c.fetchall()]

            self.dates_by_category = {
                "Sales": sales_dates,
                "Purchases": purchases_dates,
                "Items": item_dates,
                "In stock": item_dates,
                "Sale price": item_dates,
                "Purchase price": item_dates
            }

            c.execute("SELECT ItemName FROM ItemMaster")
            self.items = [record[0] for record in c.fetchall()]

            c.close()
            conn.close()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def group_years(self, years):
        try:
            grouped_years = []
            while years:
                group = []
                min_year = int(years[0])
                for i in range(min_year, min_year + 7):
                    if str(i) in years:
                        years.remove(str(i))
                    group.append(str(i))
                if len(group) > 1:
                    formatted_group = f"{min_year}-{group[-1]}"
                else:
                    formatted_group = group[0] 
                grouped_years.append(formatted_group)
            return grouped_years
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_chart(self):
        try:
            category = self.categoryComboBox.currentText()
            self.yearComboBox.blockSignals(True)
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.yearComboBox.clear()
            self.monthComboBox.setCurrentIndex(-1)
            self.monthComboBox.clear()
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)

            self.axes.cla()
            self.canvas.draw()
        
            self.years=[]
            self.manyYears=[]
            self.months=[]
            self.dates=[]

            self.years = sorted({date[:4] for date in self.dates_by_category[category]},reverse=True)
            self.manyYears = sorted({date[:4] for date in self.dates_by_category[category]})
            self.months = sorted({date[5:7] for date in self.dates_by_category[category]})
            self.dates = sorted({date[8:10] for date in self.dates_by_category[category]})

            self.monthComboBox.addItems(self.years)
            self.years = [int(x) for x in self.years]
            self.yearComboBox.addItems(self.group_years(self.manyYears))
        
            if category in ["In stock","Sale price","Purchase price","Sales","Purchases"]:
                self.add_test_combobox()
            else:
                self.remove_test_combobox()


            self.update_charts_based_on_selection()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")

    def add_test_combobox(self):
        try:
            if self.itemComboBox is None:
                self.itemComboBox = QtWidgets.QComboBox(parent=self.horizontalLayoutWidget_2)
                self.itemComboBox.setMaximumSize(QtCore.QSize(290, 16777215))
                font = QtGui.QFont()
                font.setFamily("Dubai")
                font.setPointSize(12)
                self.itemComboBox.setFont(font)
                self.itemComboBox.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
                self.itemComboBox.setAcceptDrops(False)
                self.itemComboBox.setEditable(False)
                self.itemComboBox.setInsertPolicy(QtWidgets.QComboBox.InsertPolicy.InsertAtBottom)
                self.itemComboBox.setPlaceholderText("Item Names")
                self.horizontalLayout_2.addWidget(self.itemComboBox)
                self.itemComboBox.currentTextChanged.connect(self.update_charts_based_on_selection)

            self.itemComboBox.blockSignals(True)
            self.itemComboBox.clear()
            self.itemComboBox.addItem("Select")
            self.itemComboBox.addItems(self.items)
            self.itemComboBox.blockSignals(False)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
           
    def remove_test_combobox(self):
        if self.itemComboBox:
            self.horizontalLayout_2.removeWidget(self.itemComboBox)
            self.itemComboBox.deleteLater()
            self.itemComboBox = None

    def update_charts_based_on_selection(self):
        try:
            yearly = self.yearComboBox.currentText()
            monthly = self.monthComboBox.currentText()
            daily = self.dailyComboBox.currentText()

            if yearly and not monthly and not daily:
                self.executor.submit(self.gotoModChartYear, yearly)
            if monthly and not daily and not yearly:
                self.executor.submit(self.gotoModChartMonth, monthly)
            if monthly and daily and not yearly:
                self.executor.submit(self.gotoModChartDaily, monthly, daily)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def get_year_range(self,group_year):
        try:
            if not group_year or "-" not in group_year:
                return [] 

            start_year, end_year = group_year.split("-")
            start_year = int(start_year)
            end_year = int(end_year)

            year_range = list(range(start_year, end_year + 1))
            return year_range
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
          
    def gotoModChartYear(self,value):
        self.executor.submit(self.update_chart_year, value)

    def update_chart_year(self, value):
        try:
            self.monthComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.monthComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.monthComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            xlbl="Year"
            ylbl=""
            x = [0] * 7
            y = self.get_year_range(value)
            conn = create_connection()
            c = conn.cursor()
            if self.itemComboBox and self.itemComboBox.currentText() != "" and self.itemComboBox.currentText() != "Select":
                category = self.categoryComboBox.currentText()
                item=self.itemComboBox.currentText()
                for year in self.years:
                    if year in y:
                        val = f"{year}-"
                        if category == "In stock":
                            c.execute("SELECT StockQuantity FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                            ylbl="In Stock"
                        elif category == "Sale price":
                            c.execute("SELECT SalePrice FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                            ylbl="Sale Price"
                        elif category == "Purchase price":
                            c.execute("SELECT PurchasePrice FROM ItemMaster WHERE Date LIKE %s AND ItemName =%s", (f"%{val}%",item))
                            ylbl="Purchase Price"
                        elif category == "Sales":
                            c.execute("SELECT COUNT(*) FROM SalesMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                            ylbl="Sales"
                        elif category == "Purchases":
                            c.execute("SELECT COUNT(*) FROM PurchaseMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                            ylbl="Purchases"
                        result = c.fetchone()
                        count = result[0] if result else 0
                        day_index = y.index(year)
                        x[day_index] = count
                ylbl = f"{item} {ylbl}"
            else:
                category = self.categoryComboBox.currentText()
                for year in self.years:
                    if year in y:
                        val = f"{year}-"
                        if category == "Items":
                            c.execute("SELECT COUNT(ItemName) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                            ylbl="Items"
                        elif category == "In stock":
                            c.execute("SELECT SUM(StockQuantity) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                            ylbl="In Stock"
                        elif category == "Sale price":
                            c.execute("SELECT SUM(SalePrice) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                            ylbl="Sale Price"
                        elif category == "Purchase price":
                            c.execute("SELECT SUM(PurchasePrice) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                            ylbl="Purchase Price"
                        elif category == "Sales":
                            c.execute("SELECT Items FROM SalesMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                            items=c.fetchall()
                            items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                            count=len(items_list)
                            year_index = y.index(year)
                            x[year_index] = count
                            ylbl="Sales"
                            continue
                        elif category == "Purchases":
                            c.execute("SELECT Items FROM PurchaseMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                            items=c.fetchall()
                            items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                            count=len(items_list)
                            year_index = y.index(year)
                            x[year_index] = count
                            ylbl="Purchases"
                            continue
                        result = c.fetchone()
                        count = result[0] if result and result[0] is not None else 0
                        year_index = y.index(year)
                        x[year_index] = count
            y=[str(year) for year in y]
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def gotoModChartMonth(self, value):
        self.executor.submit(self.update_chart_month, value)

    def update_chart_month(self, value):
        try:
            self.yearComboBox.blockSignals(True)
            self.dailyComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.dailyComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            self.dailyComboBox.blockSignals(False)
            xlbl="Month"
            ylbl=""
            x = [0] * 12
            y = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            month_noTonames = {
                '01': 'Jan',
                '02': 'Feb',
                '03': 'Mar',
                '04': 'Apr',
                '05': 'May',
                '06': 'Jun',
                '07': 'Jul',
                '08': 'Aug',
                '09': 'Sep',
                '10': 'Oct',
                '11': 'Nov',
                '12': 'Dec'
            }
            conn = create_connection()
            c = conn.cursor()
            if self.itemComboBox and self.itemComboBox.currentText() != "" and self.itemComboBox.currentText() != "Select":
                category = self.categoryComboBox.currentText()
                item=self.itemComboBox.currentText()
                for month in self.months:
                    val = f"{value}-{month}"
                    if category == "In stock":
                        c.execute("SELECT StockQuantity FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                        ylbl="In Stock"
                    elif category == "Sale price":
                        c.execute("SELECT SalePrice FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                        ylbl="Sale Price"
                    elif category == "Purchase price":
                        c.execute("SELECT PurchasePrice FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                        ylbl="Purchase Price"
                    elif category == "Sales":
                        c.execute("SELECT COUNT(*) FROM SalesMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Sales"
                    elif category == "Purchases":
                        c.execute("SELECT COUNT(*) FROM PurchaseMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Purchases"
                    result = c.fetchone()
                    count = result[0] if result else 0
                    month_index = y.index(month_noTonames.get(month))
                    x[month_index] = count
                ylbl = f"{item} {ylbl}"
            else:
                category = self.categoryComboBox.currentText()
                for month in self.months:
                    val = f"{value}-{month}"
                    if category == "Items":
                            c.execute("SELECT COUNT(ItemName) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                            ylbl="Items"
                    elif category == "In stock":
                        c.execute("SELECT SUM(StockQuantity) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="In Stock"
                    elif category == "Sale price":
                        c.execute("SELECT SUM(SalePrice) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Sale Price"
                    elif category == "Purchase price":
                        c.execute("SELECT SUM(PurchasePrice) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Purchase Price"
                    elif category == "Sales":
                        c.execute("SELECT Items FROM SalesMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        month_index = y.index(month_noTonames.get(month))
                        x[month_index] = count
                        ylbl="Sales"
                        continue
                    elif category == "Purchases":
                        c.execute("SELECT Items FROM PurchaseMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        month_index = y.index(month_noTonames.get(month))
                        x[month_index] = count
                        ylbl="Purchases"
                        continue
                    result = c.fetchone()
                    count = result[0] if result and result[0] is not None else 0
                    month_index = y.index(month_noTonames.get(month))
                    x[month_index] = count
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def update_plot(self, labels, values, xlabel, ylabel):
        try:
            self.axes.cla()
            self.canvas.draw()
            self.axes.plot(labels, values, marker='o', linestyle='-',color='#26648E')
            self.axes.set_facecolor('#E5ECF6')
            self.axes.tick_params(axis='x', rotation=45)
            self.axes.set_xlabel(xlabel)
            self.axes.set_ylabel(ylabel)
            self.fig.subplots_adjust(bottom=0.239)
            self.canvas.draw()
            self.fig.canvas.mpl_connect('motion_notify_event', lambda event: self.hover(event,labels,xlabel,ylabel))
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
        
    def hover(self, event,labels,xlbl,ylbl):
        try:
            if labels=='' or xlbl=='' or ylbl=='':
                self.axes.set_title('')
            elif event.inaxes == self.axes:
                x, y = event.xdata, event.ydata
                if x is not None and y is not None:
                    rounded_x = round(x)
                    if 0 <= rounded_x < len(labels):
                        xlabel = labels[rounded_x]
                    else:
                        rounded_x = max(0, min(len(labels) - 1, int(x)))
                        xlabel = labels[rounded_x]
                    self.axes.set_title(f'{xlbl} : {xlabel}  {ylbl} : {y:.0f}')
                else:
                    self.axes.set_title('')
            else:
                self.axes.set_title('')
            self.fig.canvas.draw()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
                
    def gotoModChartDaily(self, yearValue,monthValue):
        self.executor.submit(self.update_chart_daily, yearValue,monthValue)

    def update_chart_daily(self, yearValue,monthValue):
        try:
            self.yearComboBox.blockSignals(True)
            self.yearComboBox.setCurrentIndex(-1)
            self.yearComboBox.blockSignals(False)
            xlbl="Day"
            ylbl=""
            month_namesTonum = {
                'January': '01',
                'February': '02',
                'March': '03',
                'April': '04',
                'May': '05',
                'June': '06',
                'July': '07',
                'August': '08',
                'September': '09',
                'October': '10',
                'November': '11',
                'December': '12'
            }
            value = month_namesTonum.get(monthValue)
            yearMonthValue = f"{yearValue}-{value}"

            days_in_month = {
                '01': 31, '03': 31, '05': 31, '07': 31, '08': 31, '10': 31, '12': 31,
                '04': 30, '06': 30, '09': 30, '11': 30,
                '02': 29 if self.checkLeapYear(int(yearValue)) else 28
            }
            days = days_in_month[value]
            x = [0] * days
            y = [str(day) for day in range(1, days + 1)]
            conn = create_connection()
            c = conn.cursor()
            if self.itemComboBox and self.itemComboBox.currentText() != "" and self.itemComboBox.currentText() != "Select":
                category = self.categoryComboBox.currentText()
                item=self.itemComboBox.currentText()
                for day in y:
                    val = f"{yearMonthValue}-{day.zfill(2)}"
                    if category == "In stock":
                        c.execute("SELECT StockQuantity FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                        ylbl="In Stock"
                    elif category == "Sale price":
                        c.execute("SELECT SalePrice FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                        ylbl="Sale Price"
                    elif category == "Purchase price":
                        c.execute("SELECT PurchasePrice FROM ItemMaster WHERE Date LIKE %s AND ItemName = %s", (f"%{val}%",item))
                        ylbl="Purchase Price"
                    elif category == "Sales":
                        c.execute("SELECT COUNT(*) FROM SalesMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Sales"
                    elif category == "Purchases":
                        c.execute("SELECT COUNT(*) FROM PurchaseMaster WHERE OrderDate LIKE %s AND Items LIKE %s", (f"%{val}%",f"%{item}%"))
                        ylbl="Purchases"
                    result = c.fetchone()
                    count = result[0] if result else 0
                    day_index = y.index(day)
                    x[day_index] = count
                ylbl = f"{item} {ylbl}"
            else:
                category = self.categoryComboBox.currentText()
                for day in y:
                    val = f"{yearMonthValue}-{day.zfill(2)}"
                    if category == "Items":
                        c.execute("SELECT COUNT(ItemName) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Items"
                    elif category == "In stock":
                        c.execute("SELECT SUM(StockQuantity) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="In Stock"
                    elif category == "Sale price":
                        c.execute("SELECT SUM(SalePrice) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Sale Price"
                    elif category == "Purchase price":
                        c.execute("SELECT SUM(PurchasePrice) FROM ItemMaster WHERE Date LIKE %s", (f"%{val}%",))
                        ylbl="Purchase Price"
                    elif category == "Sales":
                        c.execute("SELECT Items FROM SalesMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        day_index = y.index(day)
                        x[day_index] = count
                        ylbl="Sales"
                        continue
                    elif category == "Purchases":
                        c.execute("SELECT Items FROM PurchaseMaster WHERE OrderDate LIKE %s", (f"%{val}%",))
                        items=c.fetchall()
                        items_list=[v for item in items if items for v in item[0].replace(" ", "").split(",")]
                        count=len(items_list)
                        day_index = y.index(day)
                        x[day_index] = count
                        ylbl="Purchases"
                        continue
                    result = c.fetchone()
                    count = result[0] if result and result[0] is not None else 0
                    day_index = y.index(day)
                    x[day_index] = count
            c.close()
            conn.close()
            self.update_plot(y, x,xlabel=xlbl,ylabel=ylbl)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"{e}")
            
    def checkLeapYear(self,year):
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    def gotoLogout(self):
        conn=create_connection()
        c=conn.cursor()
        log_db_operation(c,self.Eid,"has logged out")
        conn.commit()
        c.close()
        conn.close()
        loginWindow=loginApp()
        widget.addWidget(loginWindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
        self.close()

if __name__=="__main__":
    app=QtWidgets.QApplication(sys.argv)
    widget=QtWidgets.QStackedWidget()
    main=loginApp()
    widget.addWidget(main)
    widget.setWindowTitle("PAR Group Management")
    icon = QtGui.QIcon("PAR Logo.png")
    widget.setWindowIcon(icon)
    widget.showMaximized()
    sys.exit(app.exec())
