class CueInfo:
    def __init__(self, start_time, duration, trans_in=0.5, trans_out=0.5):
        self.start = start_time
        self.duration = duration
        self.transition_in = trans_in
        self.transition_out = trans_out

        self.pos_keyframes = [[0,0,0]] # x, y, time
        self.shapes = []

    @property
    def end(self):
        return self.start + self.duration


class Shape:
    def __init__(self):
        self.relative_center_pos = [0, 0]
        self.size = [0, 0]

        self.color = "#FFFFFF"
        self.opacity = "FF"

    @property
    def hex_color(self):
        return self.color + self.opacity