def generate_grid_coords(instances, x_pitch=9, y_pitch=15):
    coords = {}
    cols = 5 
    for i, inst in enumerate(instances):
        iid = str(inst.get("inst_id", ""))
        row, col = i // cols, i % cols
        coords[iid] = (col * x_pitch, -row * y_pitch)
    return coords
