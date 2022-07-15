from Ui_MainWindow import Ui_MainWindow
from Ui_About import Ui_Form
from Pwd import Pwd
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox

import sys, math, os
from tools import Tools

class MW(QtWidgets.QMainWindow):
    closeClicked = QtCore.pyqtSignal()
    def __init__(self):
        super().__init__()
    
    def closeEvent(self, event):
        self.closeClicked.emit()
   

class Main(object):
    rarFileSelected = False
    rarFile = None
    rarPath = None
    wordlistSelected = False
    wordlistPath = None
    numberOfWords = None
    numberOfCombinations = 0
    wordlistCheckboxClickedState = False
    process = None
    passwordGenerationString = None
    lowerLimit = 0
    upperLimit = 0
    TEMP_FOLDER_NAME = "temp"
    WORKING_DIR_NAME = "RarPassWorkingDir"
    WORKING_DIR_PATH = os.path.join(TEMP_FOLDER_NAME, WORKING_DIR_NAME)
    createdDirName = None
    sampleFile = None
    createdDirs = []

    def __init__(self):
        app = QtWidgets.QApplication(sys.argv)

        self._create_temp_dir()

        self.MainWindow = MW()
        self.MainWindow.closeClicked.connect(self._quit)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.MainWindow)
        self._connect_signals()

        self.upperWidgets = [self.ui.label, self.ui.lineEdit, self.ui.RARFileBrowsePushButton,\
                        self.ui.label_2, self.ui.lineEdit_2, self.ui.wordlistBrowsePushButton,\
                        self.ui.useWordlistCheckbox, self.ui.specialCharactersCheckbox, self.ui.digitsCheckbox,\
                        self.ui.lowerCaseCheckbox, self.ui.upperCaseCheckbox, self.ui.label_3,\
                        self.ui.lowerDigitLimitSpinBox, self.ui.label_4, self.ui.upperDigitLimitSpinBox,\
                        self.ui.possiblePasswordCombinationsLabel]


        self.setStatusBarText("Ready")
        self.MainWindow.show()
        sys.exit(app.exec_())

    def _connect_signals(self):
        self.ui.specialCharactersCheckbox.stateChanged.connect(self.calculatePossibleCombinations)
        self.ui.digitsCheckbox.stateChanged.connect(self.calculatePossibleCombinations)
        self.ui.lowerCaseCheckbox.stateChanged.connect(self.calculatePossibleCombinations)
        self.ui.upperCaseCheckbox.stateChanged.connect(self.calculatePossibleCombinations)
        self.ui.lowerDigitLimitSpinBox.valueChanged.connect(self.calculatePossibleCombinations)
        self.ui.upperDigitLimitSpinBox.valueChanged.connect(self.calculatePossibleCombinations)
        self.ui.useWordlistCheckbox.stateChanged.connect(self.wordlistCheckboxClicked)
        self.ui.RARFileBrowsePushButton.clicked.connect(self.rarFileBrowseClicked)
        self.ui.wordlistBrowsePushButton.clicked.connect(self.wordlistBrowseClicked)
        self.ui.startPushButton.clicked.connect(self.startProcess)
        self.ui.abortPushButton.clicked.connect(self.abortProcess)
        self.ui.actionClose.triggered.connect(self._quit)
        self.ui.actionAbout.triggered.connect(self._open_about_window)

    def _create_temp_dir(self):
        if not os.path.exists(self.TEMP_FOLDER_NAME):
            os.mkdir(self.TEMP_FOLDER_NAME)
        else:
            if not os.path.isdir(self.TEMP_FOLDER_NAME):
                counter = 2
                while os.path.exists(self.TEMP_FOLDER_NAME + str(counter)):
                    counter += 1
                self.TEMP_FOLDER_NAME += str(counter)
                self.WORKING_DIR_PATH = os.path.join(self.TEMP_FOLDER_NAME, self.WORKING_DIR_NAME)


    def calculatePossibleCombinations(self):
        Str = self.generatePasswordGenerationString()
        num = 0
        prefix = "Number of possible password combinations:\n"
        lowerLimit = self.ui.lowerDigitLimitSpinBox.value()
        upperLimit = self.ui.upperDigitLimitSpinBox.value()
        if (lowerLimit <= upperLimit) and (lowerLimit != 0 or upperLimit != 0):
            for i in range(lowerLimit, upperLimit + 1):
                if i != 0:
                    num += math.pow(len(Str), i)

        self.lowerLimit = lowerLimit
        self.upperLimit = upperLimit

        self.ui.possiblePasswordCombinationsLabel.setText(prefix + str(num))
        self.numberOfCombinations = int(num)
        self.passwordGenerationString = Str

    def generatePasswordGenerationString(self):
        passGenStr = ""
        if self.ui.specialCharactersCheckbox.isChecked():
            passGenStr += r"*-?,_!'^+%&/()=?<>{}[]£#$½\|~`" + '"'
        if self.ui.digitsCheckbox.isChecked():
            passGenStr += "0123456789"
        if self.ui.lowerCaseCheckbox.isChecked():
            passGenStr += "abcçdefghıijklmnoöprsştuüvyzwxq"
        if self.ui.upperCaseCheckbox.isChecked():
            passGenStr += "ABCÇDEFGHIİJKLMNOÖPRSŞTUÜVYZWXQ"
        return passGenStr
    
    def wordlistCheckboxClicked(self):
        elements = [self.ui.specialCharactersCheckbox, self.ui.digitsCheckbox, self.ui.lowerCaseCheckbox, \
                    self.ui.upperCaseCheckbox, self.ui.possiblePasswordCombinationsLabel, self.ui.label_3, \
                    self.ui.label_4, self.ui.lowerDigitLimitSpinBox, self.ui.upperDigitLimitSpinBox, \
                     self.ui.label_2, self.ui.lineEdit_2, self.ui.wordlistBrowsePushButton]

        states = []
        state = self.ui.useWordlistCheckbox.isChecked()
        for i in range(9):
            states.append(not state)
        for i in range(3):
            states.append(state)

        for i in range(len(states)):
            elements[i].setEnabled(states[i])

        self.wordlistCheckboxClickedState = state
    
    def rarFileBrowseClicked(self):
        filePath, _ = QFileDialog.getOpenFileName(self.MainWindow, "Choose a Password-Protected RAR File", "","RAR Files (*.rar);;All Files (*.*)")
        if filePath:
            self.createWorkingDir()
            try:
                self.addMessage(f"Selected RAR file: {filePath}")
                rarFile = rarfile.RarFile(filePath)
            except unrar.rarfile.BadRarFile:
                self.addMessage("ERROR!: This file is not a RAR file.")
            except RuntimeError as e:
                if str(e) == "Archive is encrypted, password required":
                    self.info = [["Is the file password-protected?", "Yes"], ["Are the filenames encrypted?", "Yes"]]
                    self.addMessage("The file has successfully been recognized as a RAR file.\nInformation:")
                    self.printInformation()
                    self.ui.lineEdit.setText(filePath)
                    self.rarPath = filePath
                    self.rarFile = None
                    self.rarFileSelected = True
                else:
                    self.addMessage("Unknown RuntimeError occurred: " + str(e))
            except Exception as e:
                self.addMessage("Unknown error occurred: " + str(e))
            else:
                self.addMessage("The file has successfully been recognized as a RAR file.\nInformation:")
                self.rarFileSelected = True
                self.rarFile = rarFile
                self.rarPath = filePath
                self.loadInformation()
                self.ui.lineEdit.setText(filePath)
    
    def wordlistBrowseClicked(self):
        filePath, _ = QFileDialog.getOpenFileName(self.MainWindow, "Choose a Wordlist File", "","txt Files (*.txt);;All Files (*.*)")
        if filePath:
            self.addMessage(f"Selected Wordlist file: {filePath}")
            try:
                with open(filePath, encoding="utf-8") as f:
                    self.numberOfWords = 0
                    for line in f:
                        line = line.strip()
                        if len(line) > 0:
                            self.numberOfWords += 1 
            except Exception as e:
                self.addMessage("Error while opening file:" + str(e))
            else:
                self.addMessage(f"{self.numberOfWords} non-empty lines have been detected.")
                self.wordlistPath = filePath
                self.wordlistSelected = True
                self.ui.lineEdit_2.setText(filePath)
            
    def _is_the_archive_password_protected(self):
        try:
            self.rarFile.extract(path = self.createdDirName, member = self.sampleFile)
        except RuntimeError as e:
            if str(e) == "File is encrypted, password required":
                return (True, 0, e)
            else:
                return (None, 1, e)
        except Exception as e:
            return (None, 1, e)
        else:
            return (False, 0, None)


    def _detect_sample_file(self):
        il = [f for f in self.rarFile.infolist() if f.file_size > 0]
        if len(il) == 0:
            self.sampleFile = self.rarFile.infolist()[0]
            self.addMessage("WARNING!: Either there is no file contained in the rar or all files in the rar are empty.\n" + 
                            "The file may have been detected as password-protected even though it is not.")
            return None

        minF = il[0]
        for i in range(1, len(il)):
            if il[i].file_size < minF.file_size:
                minF = il[i]
        
        self.sampleFile = minF

    def _open_about_window(self):
        self.aboutWindow = QtWidgets.QWidget()
        self.ui_aboutWindow = Ui_Form()
        self.ui_aboutWindow.setupUi(self.aboutWindow)
        self.ui_aboutWindow.pushButton.clicked.connect(self.aboutWindow.close)
        self.aboutWindow.show()
        

        

    def loadInformation(self):
        self.info = [["Is the file password-protected?", ""], ["Are the filenames encrypted?", "No"]]
        self._detect_sample_file()
        pwd_protected, err_status, exception_obj = self._is_the_archive_password_protected()
        if err_status != 0:
            self.addMessage(f"An unexpected error has occurred!: {str(exception_obj)}")
            self.clearChoice()
            return None
        else:
            if pwd_protected:
                self.info[0][1] = "Yes"
            else:
                self.info[0][1] = "No"
        self.info[1][1] = "No"
        self.printInformation()

    def clearChoice(self):
        self.rarFile = None
        self.rarFileSelected = None
        self.sampleFile = None
        self.rarPath = None
        self.ui.lineEdit.setText("")

    def printInformation(self):
        for question, answer in self.info:
            self.addMessage(question + ": " + answer)

    def startProcess(self):
        if not self.rarFileSelected:
            self.showErrorMessage("No RAR file has been selected!")
            
        else:
            if self.info[0][1] == "No":
                self.showErrorMessage("This RAR is not password-protected.")
            else:
                if self.wordlistCheckboxClickedState:
                    if not self.wordlistSelected:
                        self.showErrorMessage("No wordlist file has been selected!")
                    else:
                        self.start()

                else:
                    if self.numberOfCombinations == 0:
                        self.showErrorMessage("No possible password combination exists!\nPlease complete brute-force settings appropriately.")
                    else:
                        self.start()

    def createWorkingDir(self):
        self.createdDirName = None
        name = self.WORKING_DIR_PATH
        
        if os.path.exists(name):
            counter = 2
            while os.path.exists(name + str(counter)):
                counter += 1
            name = name + str(counter)
        
        try:
            os.mkdir(name)
            self.createdDirName = name
            self.addMessage(f"Working dir created: {os.path.abspath(name)}\nIt can be deleted safely only after the process is completed.")
            if not self.createdDirName in self.createdDirs:
                self.createdDirs.append(self.createdDirName)
        except Exception as e:
            self.addMessage(f"Error while creating the working dir: {os.path.abspath(name)}: {str(e)}\nProcess aborted.")
            return False
        
        return True

    def start(self):
        self.process = Pwd(self)
        self.process.progressBarSignal.connect(self.updateProgressBarValue)
        self.process.addMessageSignal.connect(self.addMessage)
        self.process.statusBarSignal.connect(self.setStatusBarText)
        self.process.finished.connect(self.afterProcessDoTasks)
        self.process.start()
        self.processStartedDoTasks()

    def updateProgressBarValue(self, percent):
        self.ui.progressBar.setValue(percent)

    def showErrorMessage(self, msg):
        errDialog = QMessageBox(self.MainWindow)
        errDialog.setIcon(QMessageBox.Critical)
        errDialog.setText(msg)
        errDialog.setWindowTitle("Error!")
        errDialog.exec_()
    
    def showInformation(self, title, msg):
        infDialog = QMessageBox(self.MainWindow)
        infDialog.setIcon(QMessageBox.Information)
        infDialog.setText(msg)
        infDialog.setWindowTitle(title)
        infDialog.exec_()

    def saveUpperWidgetsStates(self):
        self.upperWidgetsStates = []
        for i in self.upperWidgets:
            self.upperWidgetsStates.append(i.isEnabled())

    def disableAllUpperWidgets(self):
        for i in self.upperWidgets:
            i.setEnabled(False)

    def recoverUpperWidgetsStates(self):
        for i in range(len(self.upperWidgetsStates)):
            self.upperWidgets[i].setEnabled(self.upperWidgetsStates[i])

    def processStartedDoTasks(self):
        self.ui.startPushButton.setEnabled(False)
        self.ui.abortPushButton.setEnabled(True)
        self.saveUpperWidgetsStates()
        self.disableAllUpperWidgets()
    
    def afterProcessDoTasks(self):
        self.process.terminate()
        self.setStatusBarText("Ready")
        self.updateProgressBarValue(0)

        self.ui.startPushButton.setEnabled(True)
        self.ui.abortPushButton.setEnabled(False)
        self.recoverUpperWidgetsStates()

        self.deleteCreatedDir()
        
        if self.process.found:
            self.addMessage(f"SUCCESS!: Password found: {self.process.password}")
            self.showInformation("Process done!", f"Password: {self.process.password}")
        else:
            if self.process.aborted:
                self.addMessage("INFO: Process aborted. Password could not be found.")
                self.showInformation("Process aborted!", "Password could not be found.")
            else:
                self.addMessage(f"INFO: Password could not be found.")
                self.showInformation("Process done!", "Password could not be found.")

    def deleteCreatedDir(self):
        if self._can_be_deleted(self.createdDirName):
            os.rmdir(self.createdDirName)
            self.addMessage(f"The created working directory has successfully been deleted: {self.createdDirName}")
        else:
            msg = "The created working directory could not be deleted since "
            if not os.path.exists(self.createdDirName):
                msg += "it had already been deleted."
            else:
                msg += "it is not empty."

            self.addMessage(msg)
    
    def _can_be_deleted(self, path):
        # returns True if the specified path is an empty folder.
        return os.path.isdir(path) and not os.listdir(path)

    def _delete_dir(self, path):
        if self._can_be_deleted(path):
            os.rmdir(path)

    def _delete_created_dirs(self):
        for dir in self.createdDirs:
            self._delete_dir(dir)

    def abortProcess(self):
        if self.process:
            self.process.lock = False
            
    def setStatusBarText(self, text):
        self.ui.statusbar.showMessage(text)

    def addMessage(self, msg):
        self.ui.textEdit.append(msg)

    def setMessage(self, msg):
        self.ui.textEdit.setPlainText(msg)

    def _quit(self):
        self._delete_created_dirs()
        self.MainWindow.close()

if __name__ == "__main__":
    tools = Tools()
    tools.updateOsEnviron()
    from unrar import rarfile
    import unrar
    main = Main()
