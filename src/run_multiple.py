#!/usr/bin/env python3

from PyQt4 import QtGui
import logging, sys

from main_window import MainWindow


logging.basicConfig(level=logging.DEBUG)


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
    
