import time

from PyQt5 import QtCore, uic, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QLabel, QPushButton, QStackedLayout, QWidget

from src.OpenGL.scene import GLWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Pycraft')
        self.setFocus()

        self.fps = 0
        self.loadGame()

        self.mw = QWidget()
        self.setCentralWidget(self.mw)

        self.initMenu()

        self.specialPressed = []

    def updateGeneratingWorld(self, x, y):
        proc = x * 100 / y
        self.generateNewWorldBTN.setText(f"Generating world... ({proc}% of 100%)")
        self.repaint()

    def update(self):
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.resizeCGL()
        self.mwBg.setPixmap(self.repeatPixmap(QPixmap("../ui/textures/bg.png"), self.width(), self.height()))
        self.mwBg.resize(self.width(), self.height())
        self.generateNewWorldBTN.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)

        self.start_time = time.time()
        self.glWidget.updateGL()
        if self.glWidget.pause:
            self.inventory.move(-100, -100)
            self.glWidget.setCursor(Qt.ArrowCursor)
        else:
            self.mw.move(-self.mw.width(), -self.mw.height())
            self.inventory.move(self.width() // 2 - 182, self.height() - 50)
            self.glWidget.setCursor(Qt.BlankCursor)

        try:
            self.fps = round(1.0 / (time.time() - self.start_time))
        except:
            pass

    def loadGame(self):
        self.glWidget = GLWidget(self)
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.pause = True

        self.inventory = QLabel(self)
        self.inventory.setPixmap(QPixmap("../ui/textures/invernory.png"))
        self.inventory.setScaledContents(True)
        self.inventory.setGeometry(self.width() // 2 - 182, self.height() - 50, 364, 44)
        self.inventory.move(-100, -100)

        QtGui.QCursor.setPos(self.x() + self.width() // 2, self.y() + self.height() // 2)
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update)
        self.timer.start()

    def mousePressEvent(self, event):
        self.glWidget.mouseDown = event.button()

    def getFocus(self):
        return self.hasFocus()

    def repeatPixmap(self, pm, w, h):
        px = QPixmap(w, h)
        painter = QPainter(px)

        for i in range(0, w, pm.width()):
            for j in range(0, h, pm.height()):
                painter.drawPixmap(i, j, pm.width(), pm.height(), pm)
        painter.end()
        return px

    def initMenu(self):
        self.mwBg = QLabel(self.mw)
        self.mwBg.setPixmap(self.repeatPixmap(QPixmap("../ui/textures/bg.png"), self.width(), self.height()))
        self.mwBg.resize(self.width(), self.height())

        self.generateNewWorldBTN = QPushButton(self.mw)
        self.generateNewWorldBTN.setText("Create new world")
        self.generateNewWorldBTN.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)
        self.generateNewWorldBTN.clicked.connect(self.gen)

    def gen(self):
        self.glWidget.pause = False
        self.glWidget.generateWorld()
        self.mw.move(-self.mw.width(), -self.mw.height())
        self.setFocus()

