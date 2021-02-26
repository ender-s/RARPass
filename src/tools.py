import os, struct, platform

class Tools(object):
    def updateOsEnviron(self):
        OS = platform.system()
        if OS == "Windows":
            bit = self._detect_pythons_bit()
            if bit == 64:
                os.environ["UNRAR_LIB_PATH"] = r"..\dll\x64\UnRAR64.dll"
            elif bit == 32:
                os.environ["UNRAR_LIB_PATH"] = r"..\dll\x86\UnRAR.dll"
        elif OS == "Linux":
            os.environ["UNRAR_LIB_PATH"] = "/usr/lib/libunrar.so"
 
    def _detect_pythons_bit(self):
        return 8 * struct.calcsize("P")
