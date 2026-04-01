import sys
from PyQt5.QtWidgets import QApplication
from gui.arayuz import Arayuz

app = QApplication(sys.argv)
window = Arayuz()
window.show()
sys.exit(app.exec_())