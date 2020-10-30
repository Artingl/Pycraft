class Cube:
    def __init__(self, p, t, alpha):
        self.p, self.t, self.alpha = p, t, alpha
        self.shown = {'left': False, 'right': False, 'bottom': False, 'top': False, 'back': False, 'front': False}
        self.faces = {'left': None, 'right': None, 'bottom': None, 'top': None, 'back': None, 'front': None}
