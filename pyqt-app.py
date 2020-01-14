
import os
import sys, subprocess
# from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QLabel, QLineEdit
# from PyQt5.QtCore import Qt
import sys
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import *
# from PyQt5 import QWidgets

def main(): 
    app = QApplication(sys.argv) 
    w = MyWindow() 
    w.show() 
    sys.exit(app.exec_()) 

class TestListView(QListWidget):
    dropped = pyqtSignal(list)

#Subprocess's Popen command with piped output and active shell
def Popen(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            shell=True).communicate()[0].rstrip()

class MyWindow(QWidget): 
    def __init__(self, *args): 
        QWidget.__init__(self, *args) 
 
        # create objects
        label = QLabel(self.tr("Enter command and press Return"))
        self.le = QLineEdit()
        self.te = QTextEdit()

        # layout
        layout = QVBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(self.le)
        layout.addWidget(self.te)
        self.setLayout(layout) 

        # create connection
        # self.connect(self.le, SIGNAL("returnPressed(void)"),
        #              self.run_command)
        self.le.returnPressed.connect(self.run_command)



    def run_command(self):
        cmd = str(self.le.text())
        print (cmd)
        # stdouterr = os.popen4(cmd)[1].read()
        stdouterr = Popen(cmd)
        self.te.setText(str(stdouterr))
  
if __name__ == "__main__": 
    main()

'''
from PyQt5.QtCore import QProcess
process = QProcess()
process.start('driverquery')
process.waitForStarted()
process.waitForFinished():
process.waitForReadyRead()
tasklist = process.readAll()
process.close()
tasklist = str(tasklist).strip().split("\\r\\n")
print(tasklist)
'''
# import sys
# from PyQt5.PyGui import *
# class MyBrowser(QWidget):
#     def __init__(self, parent = None):
#         super(MyBrowser, self).__init__(parent)
#         self.createLayout()
#         self.createConnection()
#     def search(self):
#         address = str(self.addressBar.text())
#         if address:
#             if address.find('://') == -1:
#                 address = 'http://' + address
#             url = QUrl(address)
#             kwargs = {}
#             self.webView.load(self, url)
#     def createLayout(self):
#         self.setWindowTitle("keakon's browser")
#         self.addressBar = QLineEdit()
#         self.goButton = QPushButton("&GO")
#         bl = QHBoxLayout()
#         bl.addWidget(self.addressBar)
#         bl.addWidget(self.goButton)
#         self.webView = QWebView()
#         layout = QVBoxLayout()
#         layout.addLayout(bl)
#         layout.addWidget(self.webView)
#         self.setLayout(layout)
#     def createConnection(self):
#         self.addressBar.returnPressed.connect(self.search)
#         self.addressBar.returnPressed.connect(self.addressBar.selectAll)
#         self.goButton.clicked.connect(self.search)
#         self.goButton.clicked.connect(self.addressBar.selectAll)
# app = QApplication(sys.argv)
# browser = MyBrowser()
# browser.show()
# sys.exit(app.exec_())

