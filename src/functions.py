import os
from random import randint

import pyglet
from OpenGL.raw.GL.VERSION.GL_1_0 import glTexParameteri, GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST
from PyQt5.QtGui import QPixmap


def translateSeed(seed):
    res = ""
    if seed == "":
        seed = str(randint(998, 43433))
    for i in seed:
        res += str(ord(i))
    while len(res) < 10:
        res += res[:-1]
    return int(res[0:10])


def cube_vertices(pos, n=0.5):
    x, y, z = pos
    v = tuple((x + X, y + Y, z + Z) for X in (-n, n) for Y in (-n, n) for Z in (-n, n))
    return tuple(tuple(k for j in i for k in v[j]) for i in
                 ((0, 1, 3, 2), (5, 4, 6, 7), (0, 4, 5, 1), (3, 7, 6, 2), (4, 0, 2, 6), (1, 5, 7, 3)))


def flatten(lst): return sum(map(list, lst), [])


def roundPos(pos):
    x, y, z = pos
    return round(x), round(y), round(z)


def getSum(s):
    res = 0
    for i in s:
        res += int(i)

    return res


def adjacent(x, y, z):
    for p in ((x - 1, y, z), (x + 1, y, z), (x, y - 1, z), (x, y + 1, z), (x, y, z - 1), (x, y, z + 1)): yield p


def load_textures(self):
    t = self.texture
    qtit = self.QTInventoryTextures
    qadd = {}
    dirs = ['textures']
    while dirs:
        d = dirs.pop(0)
        textures = os.listdir(d)
        for file in textures:
            if os.path.isdir(d + '/' + file):
                dirs += [d + '/' + file]
            else:
                if ".png" not in file:
                    continue

                n = file.split('.')[0]
                self.texture_dir[n] = d
                qadd[n] = QPixmap(d + '/' + file)
                image = pyglet.image.load(d + '/' + file)
                texture = image.get_mipmapped_texture()
                self.texture[n] = pyglet.graphics.TextureGroup(texture)
                glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    done = []
    items = sorted(self.texture_dir.items(), key=lambda i: i[0])
    for n1, d in items:
        n = n1.split(' ')[0]
        if n in done:
            continue
        done += [n]
        if d.startswith('textures/blocks'):
            qtit[len(self.ids)] = qadd[n1]
            self.ids += [n]
            if d == 'textures/blocks':
                self.block[n] = t[n], t[n], t[n], t[n], t[n], t[n]
            elif d == 'textures/blocks/tbs':
                self.block[n] = t[n + ' s'], t[n + ' s'], t[n + ' b'], t[n + ' t'], t[n + ' s'], t[n + ' s']
            elif d == 'textures/blocks/ts':
                self.block[n] = t[n + ' s'], t[n + ' s'], t[n + ' t'], t[n + ' t'], t[n + ' s'], t[n + ' s']

        # qtit[len(qtit) + 1] = QPixmap("textures/water.png")

        self.ids += ['water']
        flow, still = t['water_flow'], t['water_still']
        self.block['water'] = flow, flow, still, still, flow, flow

        # qtit[len(qtit) + 1] = QPixmap("textures/lava.png")

        self.ids += ['lava']
        flow, still = t['lava_flow'], t['lava_still']
        self.block['lava'] = flow, flow, still, still, flow, flow
