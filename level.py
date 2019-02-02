from physics import Space

EMPTY = (0, "O", None)



class Level:
    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space()
        # TODO: load it

    def render(self, surf):
        pass
        # TODO: draw the map
