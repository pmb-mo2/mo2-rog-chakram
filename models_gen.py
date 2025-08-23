import math

def generate_stl(offset):
    stl = ["solid thumbstick"]
    # Параметры
    stick_radius = 5  # мм
    outer_radius = 10 # мм
    height_half = 6   # мм

    # Простейший цилиндр посадки (нижняя часть)
    stl.append(cylinder(stick_radius, height_half, 0, 0, 0))
    # Простейший цилиндр чашки (верхняя часть), смещённый вбок
    stl.append(cylinder(outer_radius, height_half, offset, 0, height_half))

    stl.append("endsolid thumbstick")
    return "\n".join(stl)

def cylinder(radius, height, cx, cy, cz):
    facets = []
    segments = 64
    for i in range(segments):
        angle1 = 2 * math.pi * i / segments
        angle2 = 2 * math.pi * (i + 1) / segments
        x1 = cx + radius * math.cos(angle1)
        y1 = cy + radius * math.sin(angle1)
        x2 = cx + radius * math.cos(angle2)
        y2 = cy + radius * math.sin(angle2)
        # Боковая грань
        facets.append(f"facet normal 0 0 0\n  outer loop\n    vertex {x1} {y1} {cz}\n    vertex {x2} {y2} {cz}\n    vertex {x2} {y2} {cz+height}\n  endloop\nendfacet")
        facets.append(f"facet normal 0 0 0\n  outer loop\n    vertex {x1} {y1} {cz}\n    vertex {x2} {y2} {cz+height}\n    vertex {x1} {y1} {cz+height}\n  endloop\nendfacet")
    return "\n".join(facets)

# Сохраняем три варианта STL
for off in [5, 7, 9]:
    with open(f"thumbstick_{off}mm.stl", "w") as f:
        f.write(generate_stl(off))
