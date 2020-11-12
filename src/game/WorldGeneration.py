import random
from random import randint

from collections import deque

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication

from src.functions import getSum
from src.game.Biomes import Biomes, getBiomeByTemp
from src.game.Perlin import Perlin
from src.settings import seed, maxWorldSize, maxWorldHeight, chunkSize, all_biomes, maxPlantsHeight, mountainsHeight


class WorldGeneration:
    def __init__(self, gl):
        random.seed(seed)

        self.glClass = gl
        self.playerPos = (0, 0, 0)
        self.perlin = Perlin(seed + 999)
        self.perlinBiomes = Perlin((seed + 999) + (seed + 999), mh=4)
        self.waterHeight = 60
        self.glClass.player.pos[1] = self.waterHeight
        self.hWorldSize = 0
        self.biome = [0, 0, 0]

        self.spawnPlants = 0
        self.loading = deque()
        self.queue = deque(sorted([(x, y) for x in range(-maxWorldSize, maxWorldSize)
                                   for y in range(-maxWorldSize, maxWorldSize)],
                                  key=lambda i: i[0] ** 2 + i[1] ** 2))
        self.qLen = len(self.queue)
        self.stopThisShit = False

    def genWorldAtCords(self, xx, yy):
        X, Y = xx * (chunkSize - 1), yy * (chunkSize - 1)
        treeInChunk = False
        for i in list(range(X, X + chunkSize)):
            for j in list(range(Y, Y + chunkSize)):
                self.glClass.blocksLoaded += 1

                self.add((i, 0, j), "bedrock", bd=True)

                biomePerlin = self.perlinBiomes(i, j) * 3
                activeBiome = Biomes(getBiomeByTemp(biomePerlin))
                if activeBiome.biome == "mountains":
                    self.perlin.updateAvg(mountainsHeight * 2)
                else:
                    self.perlin.updateAvg(mountainsHeight)
                y = int(self.perlin(i, j))
                if y < -15:
                    y = -15
                y += self.waterHeight
                sandPos = -2

                for k in range(0, y):
                    if k > y - 10:
                        if y > self.waterHeight + sandPos:
                            self.add((i, k, j), activeBiome.getBiomeDirt())
                        else:
                            self.add((i, k, j), 'sand')
                    else:
                        self.add((i, k, j), activeBiome.getBiomeStone())

                if y > self.waterHeight + sandPos:
                    self.add((i, y, j), activeBiome.getBiomeGrass())
                else:
                    self.add((i, y, j), 'sand', rep=True)
                    if y < self.waterHeight - 1 + sandPos:
                        for k in range(y, self.waterHeight - 1 + sandPos):
                            self.add((i, k, j), 'water', rep=True)

                if "forest" == activeBiome.biome and self.glClass.cubes.cubes[(i, y, j)].name == \
                        activeBiome.getBiomeGrass() and y > self.waterHeight + sandPos:
                    if randint(0, 55) == randint(0, 55):
                        self.spawnTree(i, y, j)
                if "mountains" == activeBiome.biome and self.glClass.cubes.cubes[(i, y, j)].name == \
                        activeBiome.getBiomeGrass() and y > self.waterHeight + sandPos:
                    if randint(0, 55) == randint(0, 95):
                        self.spawnTree(i, y, j)
                if "desert" == activeBiome.biome and self.glClass.cubes.cubes[(i, y, j)].name == \
                        activeBiome.getBiomeGrass() and y > self.waterHeight + sandPos:
                    if randint(0, 55) == randint(0, 55):
                        self.spawnCactus(i, y, j)
                if "taiga" == activeBiome.biome and self.glClass.cubes.cubes[(i, y, j)].name == \
                        activeBiome.getBiomeGrass() and y > self.waterHeight + sandPos:
                    if randint(0, 55) == randint(0, 55):
                        self.spawnTaigaTree(i, y, j)

                if self.playerPos == (0, 0, 0):
                    self.playerPos = (i, y + 2, j)
        self.glClass.chunksLoaded += 1

    def add(self, p, t, bd=False, rep=False):
        if p in self.loading and not rep:
            return
        elif (p[1] < 1 or p[1] > maxWorldHeight) and not bd:
            return
        self.loading.append((p, t))
        self.glClass.cubes.add(p, t)

    def generateChunk(self):
        if self.stopThisShit or self.glClass.genTimer % 15 != 0:
            return

        if self.queue:
            if self.glClass.chunksLoaded == 1:
                self.glClass.player.pos = self.playerPos

            self.genWorldAtCords(*self.queue.popleft())

            while self.loading:
                pos, texture = self.loading.popleft()
                self.glClass.cubes.updateCube(self.glClass.cubes.cubes[pos])
        else:
            self.stopThisShit = True
            return

    def spawnTree(self, x, y, z):
        treeHeight = randint(5, 7)

        for i in range(y, y + treeHeight):
            self.add((x, i, z), 'log_oak')
        for i in range(x + -2, x + 3):
            for j in range(z + -2, z + 3):
                for k in range(y + treeHeight - 2, y + treeHeight):
                    self.add((i, k, j), 'leaves_oak')
        for i in range(treeHeight, treeHeight + 1):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    self.add((x + j, y + i, z + k), 'leaves_oak')
        cl = 2
        for i in range(treeHeight + 1, treeHeight + 2):
            for j in range(-1, 2):
                for k in range(-1, 2):
                    if cl % 2 != 0:
                        self.add((x + j, y + i, z + k), 'leaves_oak')
                    cl += 1
        self.add((x, y + treeHeight + 1, z), 'leaves_oak')

    def spawnTaigaTree(self, x, y, z):
        treeHeight = 7

        for i in range(y, y + treeHeight):
            self.add((x, i, z), 'log_oak')
        cl = 0
        for i in range(x + -3, x + 3):
            for j in range(z + -3, z + 3):
                if cl != 0 and cl != 5 and cl != 30 and cl != 35:
                    self.add((i, y + treeHeight - 3, j), 'leaves_taiga')
                cl += 1
        cl = 2
        for j in range(-1, 2):
            for k in range(-1, 2):
                if cl % 2 != 0:
                    self.add((x + j, y + treeHeight - 2, z + k), 'leaves_taiga')
                cl += 1
        cl = 2
        for j in range(-1, 2):
            for k in range(-1, 2):
                if cl % 2 != 0:
                    self.add((x + j, y + treeHeight, z + k), 'leaves_taiga')
                cl += 1

    def spawnCactus(self, x, y, z):
        cactusHeight = randint(2, 4)
        for i in range(y, y + cactusHeight):
            self.add((x, i, z), 'cactus')

    def addGrass(self, pos):
        pass
