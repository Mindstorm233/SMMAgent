import schemdraw
import schemdraw.elements as elm
from .components import COMPONENTS_LIB, standardize_interface
from .layout import generate_grid_coords

# Suggest adding this line at the top of the file (or in demo_run.py) so text renders correctly in the PDF.
# schemdraw.use_matplotlib()

class ChipRenderer:
    def __init__(self, json_data):
        self.instances = json_data.get("instances", [])
        self.connections = json_data.get("connections", [])
        self.d = schemdraw.Drawing()
        # Set the global font size
        self.d.config(fontsize=10)
        self.drawn_cache = {}
        self.input_trackers = {}

    def render(self):
        # 1. Layout: 5 columns, horizontal pitch 9 (reduced by half)
        pos_map = generate_grid_coords(self.instances, x_pitch=9, y_pitch=14)
        
        # 2. Draw components: label only inst_id
        for inst in self.instances:
            iid = str(inst.get("inst_id", ""))  # Strictly matches JSON's inst_id
            lib_id = inst.get("lib_id")
            pos = pos_map.get(iid)

            # Get component definition
            base_func = COMPONENTS_LIB.get(lib_id, lambda: elm.Rect(w=1.2, h=1.2))
            element = standardize_interface(base_func())
            
            # --- Key change: bind label during add, and show only iid ---
            # loc='top' places the text above the element automatically; ofst is the text-element spacing
            added_el = self.d.add(element.at(pos).color('black').label(iid, loc='top', ofst=0.3))
            
            self.drawn_cache[iid] = added_el
            self.input_trackers[iid] = 0

        # 3. Right-angle connections (Manhattan routing)
        for conn in self.connections:
            from_id, to_id = conn.get("from_inst"), conn.get("to_inst")
            start_el, end_el = self.drawn_cache.get(from_id), self.drawn_cache.get(to_id)
            
            if start_el and end_el:
                self.input_trackers[to_id] += 1
                idx = self.input_trackers[to_id]
                
                p_start = start_el.end
                port_name = f'in{idx}'
                p_end = getattr(end_el, port_name) if hasattr(end_el, port_name) else end_el.start

                # Compute the routing corridor so it doesn't pass through elements in the compact layout
                hallway_x = p_start.x + 2.0 + (idx * 0.3)
                
                # Draw right-angle segments in black
                self.d.add(elm.Line().at(p_start).tox(hallway_x).color('black'))
                self.d.add(elm.Line().toy(p_end.y).color('black'))
                self.d.add(elm.Line().tox(p_end.x).color('black'))
        
        return self.d

def draw_chip(json_dict, filename="microfluidic_layout.pdf"):
    renderer = ChipRenderer(json_dict)
    d = renderer.render()
    # When saving, schemdraw automatically handles the boundaries
    d.save(filename)
