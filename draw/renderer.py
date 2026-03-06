import schemdraw
import schemdraw.elements as elm
from .components import COMPONENTS_LIB, standardize_interface
from .layout import generate_grid_coords

# 建议在文件顶部或 demo_run.py 中加入此行，以确保文字在 PDF 中渲染正常
# schemdraw.use_matplotlib()

class ChipRenderer:
    def __init__(self, json_data):
        self.instances = json_data.get("instances", [])
        self.connections = json_data.get("connections", [])
        self.d = schemdraw.Drawing()
        # 设置全局字体大小
        self.d.config(fontsize=10)
        self.drawn_cache = {}
        self.input_trackers = {}

    def render(self):
        # 1. 布局：5列，横向间距 9 (缩短了一半)
        pos_map = generate_grid_coords(self.instances, x_pitch=9, y_pitch=14)
        
        # 2. 绘制元件：仅标注 inst_id
        for inst in self.instances:
            iid = str(inst.get("inst_id", "")) # 严格对应 JSON 的 inst_id
            lib_id = inst.get("lib_id")
            pos = pos_map.get(iid)

            # 获取元件定义
            base_func = COMPONENTS_LIB.get(lib_id, lambda: elm.Rect(w=1.2, h=1.2))
            element = standardize_interface(base_func())
            
            # --- 关键修改：直接在 add 时绑定 label，且仅显示 iid ---
            # loc='top' 会自动将文字放在元件上方，ofst 是文字与元件的间距
            added_el = self.d.add(element.at(pos).color('black').label(iid, loc='top', ofst=0.3))
            
            self.drawn_cache[iid] = added_el
            self.input_trackers[iid] = 0

        # 3. 直角连线 (Manhattan Routing)
        for conn in self.connections:
            from_id, to_id = conn.get("from_inst"), conn.get("to_inst")
            start_el, end_el = self.drawn_cache.get(from_id), self.drawn_cache.get(to_id)
            
            if start_el and end_el:
                self.input_trackers[to_id] += 1
                idx = self.input_trackers[to_id]
                
                p_start = start_el.end
                port_name = f'in{idx}'
                p_end = getattr(end_el, port_name) if hasattr(end_el, port_name) else end_el.start

                # 计算布线走廊，确保不穿过紧凑布局下的元件
                hallway_x = p_start.x + 2.0 + (idx * 0.3)
                
                # 分段绘制直角线，确保黑色
                self.d.add(elm.Line().at(p_start).tox(hallway_x).color('black'))
                self.d.add(elm.Line().toy(p_end.y).color('black'))
                self.d.add(elm.Line().tox(p_end.x).color('black'))
        
        return self.d

def draw_chip(json_dict, filename="microfluidic_layout.pdf"):
    renderer = ChipRenderer(json_dict)
    d = renderer.render()
    # 保存时 schemdraw 会自动处理边界
    d.save(filename)
