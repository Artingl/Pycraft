from PyQt5 import QtGui

from src.functions import roundPos
from src.game.Cube import Cube


class MKEvent:
    def __init__(self):
        self.id = 7

    # ['bedrock', 'brick', 'coal_ore', 'cobblestone', 'diamond_ore', 'dirt', 'emerald_ore', 'glass', 'glowstone',
    # 'gold_ore', 'grass', 'gravel', 'iron_ore', 'lapis_ore', 'leaves_oak', 'log_oak', 'nocolor', 'planks_oak',
    # 'redstone_ore', 'sand', 'sandstone', 'stone']

    def update(self, glClass):
        playerSpd = 0.04
        cameraSpd = 0.5

        if not glClass.getFocus() or glClass.pause:
            return
        glClass.pause = not glClass.getFocus()
        winCenter = glClass.getCenter()
        mouseMove = [QtGui.QCursor.pos().x() - winCenter[0], QtGui.QCursor.pos().y() - winCenter[1]]
        QtGui.QCursor.setPos(winCenter[0], winCenter[1])

        glClass.player.updatePos(playerSpd)

        if glClass.mouseDown == 2:
            res = glClass.cubes.hitTest(glClass.player.pos, glClass.player.get_sight_vector())[1]
            if res:
                res2 = res[0], res[1] + 1, res[2]
                if roundPos(res) != roundPos(glClass.player.pos) and \
                        roundPos(res2) != roundPos(glClass.player.pos):
                    if res in glClass.cubes.fluids:
                        glClass.cubes.remove(res)
                        glClass.cubes.add(res, glClass.ids[glClass.getInventoryIdBlock()], True)
                    else:
                        glClass.cubes.add(res, glClass.ids[glClass.getInventoryIdBlock()], True)
        if glClass.mouseDown == 1:
            res = glClass.cubes.hitTest(glClass.player.pos, glClass.player.get_sight_vector())[0]
            if res:
                res2 = res[0], res[1] + 1, res[2]
                if roundPos(res) != roundPos(glClass.player.pos) and \
                        roundPos(res2) != roundPos(glClass.player.pos):
                    glClass.cubes.remove(res)

        r1 = mouseMove[0] * cameraSpd
        r2 = mouseMove[1] * cameraSpd
        if glClass.player.rot[0] > 90:
            glClass.player.rot[0] = 90
        if glClass.player.rot[0] < -90:
            glClass.player.rot[0] = -90

        glClass.player.mouse_motion(r1, r2)
        glClass.mouseDown = None
