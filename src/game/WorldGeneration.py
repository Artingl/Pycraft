from random import randint

from collections import deque
from src.game.Perlin import Perlin
from src.settings import seed, maxWorldSize, maxWorldHeight, chunkSize


class WorldGeneration:
    def __init__(self, gl):
        self.glClass = gl
        self.playerPos = (0, 0, 0)
        self.perlin = Perlin(seed)
        self.waterHeight = maxWorldHeight // 4 + randint(-15, 5)
        self.glClass.player.pos[1] = self.waterHeight

        self.queue = deque(sorted([(x, y) for x in range(-maxWorldSize, maxWorldSize)
                                   for y in range(-maxWorldSize, maxWorldSize)],
                                  key=lambda i: i[0] ** 2 + i[1] ** 2))
        self.stopThisShit = False

    def genWorldAtCords(self, xx, yy):
        X, Y = xx * (chunkSize - 1), yy * (chunkSize - 1)
        for i in list(range(X, X + chunkSize)):
            for j in list(range(Y, Y + chunkSize)):
                # for k in range(maxWorldHeight):
                y = int(self.perlin(i, j))
                self.glClass.cubes.add((i, y, j), 'grass', now=True)
                self.glClass.blocksLoaded += 1

                if self.playerPos == (0, 0, 0):
                    self.playerPos = (i, y + 2, j)

        self.glClass.chunksLoaded += 1

    def generateChunk(self):
        if self.stopThisShit:
            return

        if self.glClass.chunksLoaded == 5:
            self.glClass.player.pos = self.playerPos

        # if self.glClass.chunksLoaded >= int(len(self.queue.popleft()) // chunkSize) - 1:
        #    self.stopThisShit = True
        #    return

        self.genWorldAtCords(*self.queue.popleft())

    def spawnTree(self, x, y, z):
        pass

    def addGrass(self, pos):
        pass
