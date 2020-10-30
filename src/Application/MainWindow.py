import threading
import time

from PyQt5 import QtCore, uic, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtWidgets import QLabel, QPushButton, QStackedLayout, QWidget

from src.OpenGL.scene import GLWidget


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Pycraft')
        self.setFocus()

        self.fontDB = QtGui.QFontDatabase()
        self.fontDB.addApplicationFont("../ui/fonts/main.ttf")

        self.fps = 0
        self.loadGame()

        self.genTitle = None
        self.widg = QWidget()
        self.setCentralWidget(self.widg)

        self.initMenu()

        self.specialPressed = []

    def updateGeneratingWorld(self, t):
        proc = round(t[0] * 100 / t[1], 1)
        if t[2]:
            self.genTitle.setText(f"Generating world... ({proc}% of 100%)")
        else:
            self.genTitle.setText(f"Loading world... ({proc}% of 100%)")
        self.repaint()

    def update(self):
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.resizeCGL()
        if self.glWidget.pause:
            self.bg.setPixmap(self.repeatPixmap(QPixmap("../ui/textures/bg.png"), self.width(), self.height()))
            self.bg.resize(self.width(), self.height())
            self.btnGen.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)
            if self.genTitle:
                self.genTitle.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)

        self.start_time = time.time()
        self.glWidget.updateGL()
        if self.glWidget.pause:
            self.inventory.move(-100, -100)
            self.glWidget.setCursor(Qt.ArrowCursor)
        else:
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

    def initWorldGen(self):
        self.btnGen.setVisible(False)

        self.genTitle = QLabel(self.widg)
        self.genTitle.setText("Generating world... (0% of 100%)")
        self.genTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.genTitle.setFont(QtGui.QFont("Minecraft Rus", 14))
        self.genTitle.setStyleSheet("color: white")
        self.genTitle.setGeometry(self.width() // 2 - 300, self.height() // 2 - 50, 600, 100)
        self.genTitle.setVisible(True)

    def initMenu(self):
        self.bg = QLabel(self.widg)
        self.bg.setPixmap(self.repeatPixmap(QPixmap("../ui/textures/bg.png"), self.width(), self.height()))
        self.bg.resize(self.width(), self.height())

        self.btnGen = QPushButton(self.widg)
        # self.btnGen.setStyleSheet("background: url('https://i.ibb.co/rb2TWXL/bgbtn.png');")
        self.btnGen.setText("Create new world")
        self.btnGen.setFont(QtGui.QFont("Minecraft Rus", 14))
        self.btnGen.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)
        self.btnGen.clicked.connect(self.gen)

    def gen(self):
        self.initWorldGen()
        self.glWidget.pause = False
        self.glWidget.generateWorld()
        self.widg.setVisible(False)
        self.setFocus()
