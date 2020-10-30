from OpenGL.GL import *

from src.game.Cube import Cube
from src.functions import normalize, cube_vertices, adjacent, grass_verts


class CubeHandler:
    def __init__(self, batch, block, opaque, alpha_textures):
        self.batch, self.block, self.alpha_textures, self.opaque = batch, block, alpha_textures, opaque
        self.cubes = {}

    def hitTest(self, p, vec, dist=6):
        m = 8
        x, y, z = p
        dx, dy, dz = vec
        dx /= m
        dy /= m
        dz /= m
        b = None
        for i in range(dist * m):
            c = normalize((x, y, z))
            if c in self.cubes:
                return c, b
            b = c
            x, y, z = x + dx, y + dy, z + dz
        return None, None

    def draw(self, v, t):
        return self.batch.add(4, GL_QUADS, t, ('v3f/static', v), ('t2f/static', (0, 0, 1, 0, 1, 1, 0, 1)))

    def updateCube(self, cube):
        if not any(cube.shown.values()):
            return
        v = cube_vertices(cube.p)
        f = 'left', 'right', 'bottom', 'top', 'back', 'front'
        for i in (0, 1, 2, 3, 4, 5):
            if cube.shown[f[i]]:
                if not cube.faces[f[i]]:
                    cube.faces[f[i]] = self.draw(v[i], cube.t[i])
            elif cube.faces[f[i]]:
                cube.faces[f[i]].delete()
                cube.faces[f[i]] = None

    def setAdj(self, cube, adj, state):
        x, y, z = cube.p
        X, Y, Z = adj
        d = X - x, Y - y, Z - z
        f = 'left', 'right', 'bottom', 'top', 'back', 'front'
        for i in (0, 1, 2):
            if d[i]:
                j = i + i
                a, b = [f[j + 1], f[j]][::d[i]]
                cube.shown[a] = state
                if not state and cube.faces[a]:
                    cube.faces[a].delete()
                    cube.faces[a] = None

    def add(self, p, t, now=False):
        if p in self.cubes:
            return
        cube = self.cubes[p] = Cube(p, self.block[t], t in self.alpha_textures)

        for adj in adjacent(*cube.p):
            if adj in self.cubes:
                if not cube.alpha or self.cubes[adj].alpha:
                    self.setAdj(self.cubes[adj], cube.p, False)
                if self.cubes[adj].alpha:
                    self.setAdj(cube, adj, True)
            else:
                self.setAdj(cube, adj, True)
        if now:
            self.updateCube(cube)

    def remove(self, p):
        if p in self.cubes:
            if str(self.cubes[p].t[0]) == "TextureGroup(id=4)":
                return

            cube = self.cubes.pop(p)

            for side, face in cube.faces.items():
                if face:
                    face.delete()

            for adj in adjacent(*cube.p):
                if adj in self.cubes:
                    self.setAdj(self.cubes[adj], cube.p, True)
                    self.updateCube(self.cubes[adj])
