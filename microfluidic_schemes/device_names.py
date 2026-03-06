import schemdraw
import schemdraw.elements as elm

keywords = [
    "Diode", "Schott", "Diac", "Zener", "TVS",
    "Crystal", "Xtal", "Reson",
    "Motor", "Amm", "Meter", "Test", "Terminal", "Dot",
    "Switch", "Contact",
    "And", "Xor", "Logic", "Gate"
]

names = sorted([n for n in dir(elm) if any(k.lower() in n.lower() for k in keywords)])
print("schemdraw.elements matches:")
print("\n".join(names))

# 逻辑门有的版本在 schemdraw.logic
try:
    import schemdraw.logic as logic
    names2 = sorted([n for n in dir(logic) if any(k.lower() in n.lower() for k in ["And", "Xor", "Or", "Not", "Nand", "Nor", "Xnor"])])
    print("\nschemdraw.logic matches:")
    print("\n".join(names2))
except Exception as e:
    print("\nNo schemdraw.logic module in this version:", e)
