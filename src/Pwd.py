from PyQt5.QtCore import QThread, pyqtSignal

from tools import Tools
tools = Tools()
tools.updateOsEnviron()
from unrar import rarfile
rarfile.b = lambda x: x.encode("cp1254")


class Pwd(QThread):
    progressBarSignal = pyqtSignal(int)
    addMessageSignal = pyqtSignal(str)
    statusBarSignal = pyqtSignal(str)

    def __init__(self, mainClass):
        super().__init__()

        

        self.mainClass = mainClass
        self.lock = True
        self.found = False
        self.password = None
        self.str = self.mainClass.passwordGenerationString
        self.ll = self.mainClass.lowerLimit
        self.ul = self.mainClass.upperLimit
        self.wordlistMode = self.mainClass.wordlistCheckboxClickedState
        self.extractTo = self.mainClass.createdDirName
        self.rarFile = self.mainClass.rarFile
        self.pwdCount = 0
        self.aborted = False
        self.lastTried = None

        if self.mainClass.info[1][1] == "Yes":
            self.rarFileExists = False
        else:
            self.rarFileExists = True
        

    def run(self):
        if not self.wordlistMode:
            for i in range(self.ll, self.ul + 1):
                if not self.lock:
                    self.aborted = True
                    break
                self.loop(i, i, '')
        else:
            try:
                with open(self.mainClass.wordlistPath, encoding="utf-8") as f:
                    for line in f:
                        if not self.lock:
                            self.aborted = True
                            break
                        pwd = line.strip()
                        if pwd:
                            self.pwdCount += 1  
                            found, status = self.tryPassword(pwd)  
                            self.lastTried = pwd
                            self.calculateAndSetProgress()    
                            if status == 1:
                                self.lock = False
                                self.addMessageSignal.emit("Aborting...")
                                self.aborted = True
                                break
                            elif found:
                                self.found = True
                                self.password = pwd
                                self.lock = False
                                break

            except Exception as e:
                self.addMessageSignal.emit(f"An unexpected error occured: {str(e)}")
    
    def loop(self, orignumber, number, str):
        if not self.lock:
            self.aborted = True
            return
        if number > 0:
            for i in self.str:
                if not self.lock:
                    self.aborted = True
                    break
                n = str+i
                if (len(n) == orignumber):
                    self.pwdCount += 1
                    found, status = self.tryPassword(n)
                    self.lastTried = n
                    self.calculateAndSetProgress()
                    
                    if status == 1:
                        self.lock = False
                        self.addMessageSignal.emit("Aborting...")
                        break
                    elif found:
                        self.found = True
                        self.password = n
                        self.lock = False
                        break

                self.loop(orignumber, number - 1, n)
    
    def calculateAndSetProgress(self):
        maxNum = 0
        if self.wordlistMode:
            maxNum = self.mainClass.numberOfWords
        else:
            maxNum = self.mainClass.numberOfCombinations

        percent = (float(self.pwdCount) / maxNum) * 100 
        self.progressBarSignal.emit(int(percent))
        self.statusBarSignal.emit(f"{self.pwdCount}/{maxNum}... Trying {self.lastTried}")

    def tryPassword(self, pwd):
        if self.rarFileExists:
            try:
                self.rarFile.extract(path = self.extractTo, member = self.mainClass.sampleFile, pwd = pwd)
            except RuntimeError as e:
                if str(e) == "Bad password for File":
                    return (False, 0)
                else:
                    self.addMessageSignal.emit(f"Unknown RuntimeError occurred: {str(e)}")
                    return (False, 1)
            except Exception as e:
                self.addMessageSignal.emit(f"Unknown error occurred: {str(e)}")
                return (False, 1)
            else:
                return (True, 0)
        
        else:
            try:
                rarFile = rarfile.RarFile(self.mainClass.rarPath, pwd = pwd)
            except RuntimeError as e:
                if str(e) == "Bad password for Archive":
                    return (False, 0)
                else:
                    self.addMessageSignal.emit(f"Unknown RuntimeError occurred: {str(e)}")
                    return (False, 1)
            except Exception as e:
                self.addMessageSignal.emit(f"Unknown error occurred: {str(e)}")
                return (False, 1)
            else:
                return (True, 0)
