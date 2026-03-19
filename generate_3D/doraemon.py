"""
DORAEMON 3D CHARACTER ASSEMBLY
-------------------------------------
Created for Blender 3.6+
Author: AI Assistant (Modeled after real Blender Doraemon projects)
References:
- https://github.com/JerinFrancisA/Doraemon-3D-Model-Blender
- https://sketchfab.com/3d-models/doraemon-d1f580c1476247208b01af5a5d73f80d
- https://docs.blender.org/api/current/index.html

Execute this script in Blender’s Scripting workspace.
"""

import bpy
import math
from mathutils import Vector

# =============================
# SCENE CLEANUP
# =============================
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ------------------------------------
# Utility: Create a colored material
# ------------------------------------
def create_material(name: str, color: tuple) -> bpy.types.Material:
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Roughness"].default_value = 0.4
    return mat

# Materials
MAT_BLUE = create_material("Doraemon_Blue", (0.1, 0.4, 0.8, 1))
MAT_WHITE = create_material("Doraemon_White", (1, 1, 1, 1))
MAT_RED = create_material("Doraemon_Red", (0.9, 0.1, 0.1, 1))
MAT_YELLOW = create_material("Doraemon_Yellow", (1, 0.85, 0.1, 1))
MAT_BLACK = create_material("Doraemon_Black", (0, 0, 0, 1))

# =============================
# HEAD
# =============================
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.1, location=(0, 0, 1.8))
head = bpy.context.active_object
head.name = "Head"
head.data.materials.append(MAT_BLUE)

# Face patch
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.08, location=(0, 0.02, 1.8))
face_patch = bpy.context.active_object
face_patch.scale = (1, 0.7, 1)
face_patch.name = "Face_Patch"
face_patch.data.materials.append(MAT_WHITE)

# =============================
# EYES
# =============================
def add_eye(x_offset):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(x_offset, 1.0, 2.1))
    eye = bpy.context.active_object
    eye.data.materials.append(MAT_WHITE)
    
    # pupil
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.06, location=(x_offset, 1.22, 2.1))
    pupil = bpy.context.active_object
    pupil.data.materials.append(MAT_BLACK)
    return eye, pupil

eye_L, pupil_L = add_eye(-0.17)
eye_R, pupil_R = add_eye(0.17)

# Nose
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 1.18, 1.95))
nose = bpy.context.active_object
nose.data.materials.append(MAT_RED)

# =============================
# BODY
# =============================
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0.8))
body = bpy.context.active_object
body.data.materials.append(MAT_BLUE)

# Belly patch
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.98, location=(0, 0.1, 0.8))
belly_patch = bpy.context.active_object
belly_patch.scale = (1, 0.7, 1)
belly_patch.data.materials.append(MAT_WHITE)

# =============================
# COLLAR + BELL
# =============================
bpy.ops.mesh.primitive_torus_add(major_radius=0.95, minor_radius=0.08, location=(0, 0.05, 1.25))
collar = bpy.context.active_object
collar.rotation_euler[0] = math.radians(90)
collar.data.materials.append(MAT_RED)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, 0.25, 1.25))
bell = bpy.context.active_object
bell.data.materials.append(MAT_YELLOW)

# Tail
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.12, location=(0, -0.95, 0.7))
tail = bpy.context.active_object
tail.data.materials.append(MAT_RED)

# =============================
# ARMS
# =============================
def add_arm(x_offset):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.28, location=(x_offset * 1.1, 0, 1.1))
    arm = bpy.context.active_object
    arm.scale = (0.9, 1.1, 1)
    arm.data.materials.append(MAT_WHITE)
    return arm

add_arm(-0.9)
add_arm(0.9)

# =============================
# LEGS
# =============================
def add_leg(x_offset):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.3, location=(x_offset * 0.5, 0.3, -0.1))
    leg = bpy.context.active_object
    leg.data.materials.append(MAT_WHITE)
    return leg

add_leg(-0.5)
add_leg(0.5)

# =============================
# POUCH
# =============================
bpy.ops.mesh.primitive_torus_add(major_radius=0.45, minor_radius=0.06, location=(0, 0.55, 0.65))
pouch = bpy.context.active_object
pouch.rotation_euler[0] = math.radians(90)
pouch.data.materials.append(MAT_YELLOW)

# =============================
# SCENE LIGHTING
# =============================
bpy.ops.object.light_add(type='AREA', location=(3, -3, 5))
light = bpy.context.active_object
light.data.energy = 1200

# =============================
# CAMERA
# =============================
bpy.ops.object.camera_add(location=(0, -5, 2.5), rotation=(math.radians(75), 0, 0))
bpy.context.scene.camera = bpy.context.active_object

# =============================
# PARENTING & ORGANIZATION
# =============================
collection = bpy.data.collections.new("Doraemon_Character")
bpy.context.scene.collection.children.link(collection)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        bpy.data.collections['Doraemon_Character'].objects.link(obj)
        bpy.context.scene.collection.objects.unlink(obj)

print("✅ Doraemon 3D model assembly complete!")
