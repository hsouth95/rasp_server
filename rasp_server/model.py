import inspect
class Entity():
    def get_attributes(self):
        return inspect.getmembers(self)

class User(Entity):
    """A basic User class."""
    def __init__(self, nickname):
        self.nickname = nickname
