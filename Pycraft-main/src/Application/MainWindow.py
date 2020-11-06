import threading
import time

from PyQt5 import QtCore, uic, QtGui
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QFont, QIcon
from PyQt5.QtWidgets import QLabel, QPushButton, QStackedLayout, QWidget

from src.OpenGL.scene import GLWidget
from src.styles import buttonStyle


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1280, 720)
        self.setWindowTitle('Pycraft')
        self.setFocus()

        self.fontDB = QtGui.QFontDatabase()
        self.fontDB.addApplicationFont("../ui/fonts/main.ttf")

        self.fps = 0
        self.hpPixmap = None
        self.loadGame()

        self.selectedSection = 1
        self.invList = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.hp = 15

        self.genTitle = None
        self.widg = QWidget()
        self.setCentralWidget(self.widg)

        self.initMenu()

        self.specialPressed = []

    def getInventoryIdBlock(self):
        return self.invList[self.selectedSection - 1]

    def updateGeneratingWorld(self, t):
        proc = round(t[0] * 100 / t[1], 1)
        if t[2]:
            self.genTitle.setText(f"Generating world... ({proc}% of 100%)")
        else:
            self.genTitle.setText(f"Loading terrain... ({proc}% of 100%)")
        self.repaint()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.glWidget.pause = not self.glWidget.pause
        if event.key() == Qt.Key_F:
            self.glWidget.player.flying = not self.glWidget.player.flying
        if event.key() == Qt.Key_E:
            self.showImventory()
        if event.key() == Qt.Key_1:
            self.selectedSection = 1
        if event.key() == Qt.Key_2:
            self.selectedSection = 2
        if event.key() == Qt.Key_3:
            self.selectedSection = 3
        if event.key() == Qt.Key_4:
            self.selectedSection = 4
        if event.key() == Qt.Key_5:
            self.selectedSection = 5
        if event.key() == Qt.Key_6:
            self.selectedSection = 6
        if event.key() == Qt.Key_7:
            self.selectedSection = 7
        if event.key() == Qt.Key_8:
            self.selectedSection = 8
        if event.key() == Qt.Key_9:
            self.selectedSection = 9

    def update(self):
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.resizeCGL()
        if self.glWidget.pause:
            self.bg.setPixmap(self.repeatPixmap(QPixmap("../ui/textures/bg.png"), self.width(), self.height()))
            self.bg.resize(self.width(), self.height())
            self.btnGen.move(self.width() // 2 - (self.btnGen.width() // 2),
                             self.height() // 2 - (self.btnGen.height() // 2))
            self.logo.move(self.width() // 2 - 381 // 2, self.height() // 9)
            if self.genTitle:
                self.genTitle.setGeometry(self.width() // 2 - 200, self.height() // 2 - 50, 400, 100)

        self.start_time = time.time()
        self.glWidget.updateGL()
        if self.glWidget.pause:
            self.inventory.move(-100, -100)
            self.inventorySel.move(-100, -100)
            self.glWidget.setCursor(Qt.ArrowCursor)
        else:
            self.SetPixmapInventory()
            self.updateHp()
            self.inventory.setGeometry(self.width() // 2 - 182, self.height() - 50, 364, 44)
            self.inventorySel.setGeometry(self.width() // 2 - 182 + (40 * (self.selectedSection - 1) + 2),
                                          self.height() - 48, 40, 40)
            self.glWidget.setCursor(Qt.BlankCursor)

        try:
            self.fps = round(1.0 / (time.time() - self.start_time))
        except:
            pass

    def showImventory(self):
        pass  # print(self.glWidget.QTInventoryTextures)

    def updateHp(self):
        if not self.hpPixmap:
            return

        curr = 0
        for i in range(self.hp):
            if i % 2 == 0:
                curr += 1
                self.hpPixmap[curr].setPixmap(QPixmap("../ui/textures/hp.png"))
            else:
                self.hpPixmap[curr].setPixmap(QPixmap("../ui/textures/halfhp.png"))

    def SetPixmapInventory(self):
        px = self.invPixmap
        painter = QPainter(px)
        for i in self.invList:
            painter.drawPixmap(44 // 2 - 8 + (40 * (i - 1) + 2),
                               44 // 2 - 8, 16, 16,
                               self.glWidget.QTInventoryTextures[i])
        painter.end()
        self.inventory.setPixmap(px)

    def loadGame(self):
        self.glWidget = GLWidget(self)
        self.glWidget.setGeometry(0, 0, self.width(), self.height())
        self.glWidget.pause = True

        self.invPixmap = QPixmap("../ui/textures/inventory.png")
        self.inventory = QLabel(self)
        self.inventory.setPixmap(self.invPixmap)
        self.inventory.move(-100, -100)

        self.inventorySel = QLabel(self)
        self.inventorySel.setPixmap(QPixmap("../ui/textures/inventorySel.png"))
        self.inventorySel.move(-100, -100)

        self.hpPixmap = []
        for i in range(10):
            lbl = QLabel()
            lbl.setPixmap(QPixmap("../ui/textures/hp.png"))
            lbl.setGeometry(self.width() // 2 - 182 + (i * 16), self.height() - 70, 12, 12)

            self.hpPixmap.append(lbl)

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
        self.logo.setVisible(False)

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

        self.logo = QLabel(self.widg)
        self.logo.setPixmap(QPixmap("../ui/textures/logo.png"))
        self.logo.move(self.width() // 2 - 381 // 2, self.height() // 9)

        self.btnGen = QPushButton(self.widg)
        # self.btnGen.setStyleSheet("background: url('https://i.ibb.co/rb2TWXL/bgbtn.png');")
        self.btnGen.setText("Create new world")
        self.btnGen.setFont(QtGui.QFont("Minecraft Rus", 12))
        self.btnGen.setGeometry(self.width() // 2 - 200, self.height() // 2 - 20, 400, 40)
        self.btnGen.clicked.connect(self.gen)
        self.btnGen.setStyleSheet(buttonStyle)

    def gen(self):
        self.initWorldGen()
        self.glWidget.pause = False
        self.glWidget.generateWorld()
        self.widg.setVisible(False)
        self.setFocus()
