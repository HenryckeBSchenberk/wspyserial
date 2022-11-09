from .protocol import package

class G0(package):
    def __init__(self, data):
        super().__init__(data, 1)

class M114(package):
    def __init__(self, data):
        super().__init__(data, 2)

class M119(package):
    def __init__(self, data):
        super().__init__(data, 6)

GCODES = {
    "G0": G0,
    "M114": M114,
    "M119": M119
}