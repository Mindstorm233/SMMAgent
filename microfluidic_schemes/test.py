import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing():
    elm.Resistor()
    elm.Capacitor()
    elm.Diode()

# 展示电路图
# d.draw()