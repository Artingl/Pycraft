from PyQt5.QtCore import Qt

# Folders
worldsFolder = "../worlds/"
texturePacksFolder = "../textures/"

# Ui
FOV = 70
renderDistance = 1000

# Game
playerName = "Tan4or"
seed = 1000
chunkSize = 6
maxWorldSize = 256
maxWorldHeight = 50

# Player
playerGravity = 1.8
playerFlyingSpeed = 10
playerMovingSpeed = 1.3
playerJumpSpeed = (4 * playerGravity) ** .5

# Keyboard
pauseButton = Qt.Key_Escape
flyingButton = Qt.Key_F
inventoryButton = Qt.Key_E
selectInventoryCell1 = Qt.Key_1
selectInventoryCell2 = Qt.Key_2
selectInventoryCell3 = Qt.Key_3
selectInventoryCell4 = Qt.Key_4
selectInventoryCell5 = Qt.Key_5
selectInventoryCell6 = Qt.Key_6
selectInventoryCell7 = Qt.Key_7
selectInventoryCell8 = Qt.Key_8
selectInventoryCell9 = Qt.Key_9

# Other
mountainsHeight = 8
