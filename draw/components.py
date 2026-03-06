import schemdraw.elements as elm
import schemdraw.logic as logic
from schemdraw.segments import Segment, SegmentCircle, SegmentText

class MeterM(elm.Element2Term):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        r = 0.35
        self.segments.append(Segment([(0, 0), (0.5-r, 0)]))
        self.segments.append(Segment([(0.5+r, 0), (1, 0)]))
        self.segments.append(SegmentCircle((0.5, 0), r))
        self.segments.append(SegmentText((0.5, 0), 'M'))

def standardize_interface(el):
    """确保元件拥有 end (输出) 和 start (默认输入) 锚点"""
    anchors = el.anchors.keys()
    if 'out' in anchors and 'end' not in anchors:
        el.anchors['end'] = el.anchors['out']
    if 'in1' in anchors and 'start' not in anchors:
        el.anchors['start'] = el.anchors['in1']
    if 'start' not in anchors:
        el.anchors['start'] = (0, 0)
    if 'end' not in anchors:
        el.anchors['end'] = (1, 0)
    return el

COMPONENTS_LIB = {
    "P1": lambda: elm.Diode(fill=True),
    "P2": lambda: elm.Diode(fill=True),
    "P3": lambda: elm.Diode(),
    "P4": lambda: elm.DiodeTVS(fill=True),
    "P5": lambda: elm.Button(),
    "P6": lambda: elm.Capacitor(),
    "P7": lambda: elm.Capacitor(),
    "P8": lambda: elm.Capacitor(),
    "M1": lambda: elm.Potentiometer(),
    "M2": lambda: elm.Potentiometer(),
    "M3": lambda: elm.Potentiometer(),
    "M4": lambda: logic.And(inputs=5),          # 5引脚与门
    "M5": lambda: logic.SchmittAnd(inputs=5),   # 5引脚施密特与门
    "M6": lambda: elm.Crystal(),
    "M7": lambda: elm.Crystal().color('red'),
    "I1": lambda: elm.Dot(open=True).color('red'),
    "I2": lambda: elm.Dot(open=True),
    "I3": lambda: elm.Dot(open=True).color('red'),
    "I4": lambda: elm.Dot(open=True),
    "I5": lambda: elm.Ground(),
    "I6": lambda: elm.Dot(),
    "I7": lambda: elm.Source(),
    "I8": lambda: MeterM(),
    "I9": lambda: elm.MeterA(),             
}
