class Step:

    # width of a document when displayed as 100%.
    WIDTH_100p = 1240
    PERCENT = 100
    LIST = [125, 100, 75, 50, 10]

    # aspect ration for A4 paper is h = w * 1.41
    # for 100
    # 100 => w = 1240, h = 1748
    # 50  => w = 620, h = 874

    def __init__(self, current=1):
        self.current = current

    @property
    def width(self):
        p = self.percent / 100
        return int(p * Step.WIDTH_100p)

    @property
    def is_thumbnail(self):
        return self.percent < 50

    @property
    def is_for_hocr(self):
        return not self.is_thumbnail

    @property
    def percent(self):
        return Step.LIST[self.current]

    def __str__(self):
        return f"Step(percent={self.percent}, width={self.width})"

    def __repr__(self):
        return self.__str__()


class Steps:
    def __init__(self):
        self.steps = [Step(0), Step(1), Step(2), Step(3), Step(4)]

    def __iter__(self):
        return iter(self.steps)
