from PyQt5.QtCore import Qt

# Folders
from src.functions import translateSeed

worldsFolder = "../worlds/"
texturePacksFolder = "../textures/"

# Ui
FOV = 100
renderDistance = 32

# World
seed = translateSeed("6546454")
chunkSize = 4
maxWorldSize = 32
maxWorldHeight = 256
maxPlantsHeight = 7
mountainsHeight = 5
biome = "forest"
all_biomes = ["forest", "desert", "ocean", "taiga", "mountains"]

# Player
playerName = "Tan4or"
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
