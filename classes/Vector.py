import math

class Vector:
    def __init__(self, x: float, y: float, z: float):
        self.vec = [x, y, z]

    def __repr__(self):
        return '{self.__class__.__name__}(x={self.vec[0]}, y={self.vec[1]}, z={self.vec[2]})'.format(self=self)

    @property
    def x(self):
        return self.vec[0]

    @property
    def y(self):
        return self.vec[1]

    @property
    def z(self):
        return self.vec[2]

    def __mul__(self, other):
        return Vector(self.x*other, self.y*other, self.z*other)

    __rmul__ = __mul__

    def __add__(self, other):
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return Vector(self.x-other.x, self.y-other.y, self.z-other.z)

    def distance(self, other):
        return math.sqrt((self.x-other.x)**2 + (self.y-other.y)**2 + (self.z-other.z)**2)

    # def __getattribute__(self, name):
    #     if name in ['x', 'y', 'z']:
    #         return self.vec['xyz'.index(name)]
    #     else:
    #         raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")