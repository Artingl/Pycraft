import PyQt5
from PyQt5.QtCore import Qt

from src.functions import translateSeed
import sqlite3


class Settings:
    # Folders
    worldsFolder = "../worlds/"
    texturePacksFolder = "../textures/"

    # Ui
    FOV = 100
    renderDistance = 32

    # World
    seed = translateSeed("54454533534")
    chunkSize = 4
    maxWorldSize = 16
    maxWorldHeight = 256
    maxPlantsHeight = 7
    mountainsHeight = 5

    # Player
    playerName = "Player"
    playerGravity = 1.4
    playerFlyingSpeed = 10
    playerMovingSpeed = 1.6
    playerJumpSpeed = (4 * playerGravity) ** .5

    # Keyboard
    pauseButton = Qt.Key_Escape
    flyingButton = Qt.Key_F
    inventoryButton = Qt.Key_E
    showInfo = Qt.Key_F3
    selectInventoryCell1 = Qt.Key_1
    selectInventoryCell2 = Qt.Key_2
    selectInventoryCell3 = Qt.Key_3
    selectInventoryCell4 = Qt.Key_4
    selectInventoryCell5 = Qt.Key_5
    selectInventoryCell6 = Qt.Key_6
    selectInventoryCell7 = Qt.Key_7
    selectInventoryCell8 = Qt.Key_8
    selectInventoryCell9 = Qt.Key_9

    alLSettings = "worldsFolder texturePacksFolder FOV renderDistance seed chunkSize maxWorldSize maxWorldHeight " \
                  "maxPlantsHeight mountainsHeight playerName playerGravity playerFlyingSpeed playerMovingSpeed " \
                  "playerJumpSpeed pauseButton flyingButton inventoryButton showInfo selectInventoryCell1 " \
                  "selectInventoryCell2 selectInventoryCell3 selectInventoryCell4 selectInventoryCell5 " \
                  "selectInventoryCell6 selectInventoryCell7 selectInventoryCell8 selectInventoryCell9".split()

    def __init__(self):
        self.lastBaseName = ""

    def load(self, fname):
        self.lastBaseName = fname
        con = sqlite3.connect(fname)
        cur = con.cursor()
        for i in self.alLSettings:
            val, vtype = cur.execute(f"""SELECT value,type FROM settings WHERE name = "{i}" """).fetchall()[0]
            if vtype == "int":
                val = int(val)
            if vtype == "str":
                val = str(val)
            if vtype == "float":
                val = float(val)
            if vtype == "Key":
                val = PyQt5.QtCore.Qt.Key(val)
            setattr(self, i, val)
        con.close()

    def update(self, instance, value):
        setattr(self, instance, value)
        con = sqlite3.connect(self.lastBaseName)
        cur = con.cursor()
        cur.execute(f"""UPDATE settings SET name="{instance}",value="{value}",type="{type(value).__name__}"
                        WHERE name="{instance}" """).fetchall()
        con.commit()
        con.close()

    def saveAllSettings(self, fname):
        self.lastBaseName = fname
        con = sqlite3.connect(fname)
        cur = con.cursor()
        cur.execute("""CREATE TABLE settings(name,value,type)""")
        for i in self.alLSettings:
            val = getattr(self, i)
            cur.execute(f"""INSERT INTO settings(name,value,type) VALUES("{i}","{val}","{type(val).__name__}")""")\
                .fetchall()
        con.commit()
        con.close()
