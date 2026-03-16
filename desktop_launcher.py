import sys
import os
import subprocess
import time

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl


def main():

    # get correct folder after installation
    if getattr(sys, 'frozen', False):
        BASE_DIR = os.path.dirname(sys.executable)
    else:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # start Django server
    subprocess.Popen(
        [sys.executable, "manage.py", "runserver", "127.0.0.1:8000"],
        cwd=BASE_DIR
    )

    # wait server to start
    time.sleep(30)

    app = QApplication(sys.argv)

    browser = QWebEngineView()
    browser.load(QUrl("http://127.0.0.1:8000"))
    browser.setWindowTitle("Sales Management")
    browser.show()

    sys.exit(app.exec_())


if __name__ == "__main__":

    main()
