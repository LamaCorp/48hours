from physics import Space

class Level:    
    def __init__(self, level='level_0'):
        self.name = level
        self.space = Space(gravity=(0, 1))
        # TODO: load it

    def render(self, surf):
        pass
        #TODO: draw the map
