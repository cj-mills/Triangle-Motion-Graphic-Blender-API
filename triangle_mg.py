# The Blender Python API
import bpy
# Gives access to Blender's internal mesh editing API
import bmesh

# Provides access to mathematical functions
import math

def get_name():
    """Get the name for the currently active object"""
    return bpy.context.active_object.name

def degToRadian(angle):
    """Convert angle from degrees to radians"""
    return angle*(math.pi/180)

def move_obj(name, coords):
    """Set object location to the specified coordinates"""
    bpy.data.objects[name].location = coords

def rotate_obj(name, angles):
    """Set object rotation to the specified angles"""
    rotation = [degToRadian(angle) for angle in angles]
    bpy.data.objects[name].rotation_euler = rotation

def scale_obj(name, scale):
    """Set object scale"""
    bpy.data.objects[name].scale = scale

def clear_collection(collection):
    """Remove everything from the specified collection"""
    for obj in collection.objects:
        bpy.data.objects.remove(obj)
        
def add_keyframe_sequence(obj, attribute, values, frames):
    """Add a sequence of keyframes for an object"""
    for v, f in zip(values, frames):
        setattr(obj, attribute, v)
        obj.keyframe_insert(data_path=attribute, frame=f)


"""Set up the scene"""
# Set View Transform to Standard
bpy.data.scenes["Scene"].view_settings.view_transform = "Standard"
# Enable transparency
bpy.data.scenes['Scene'].render.film_transparent = True
# Set the Background color to pure black
bpy.data.worlds['World'].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)
# Clear Collection
clear_collection(bpy.data.collections[0])


"""Create and position a new camera"""
# Create a new camera
bpy.ops.object.camera_add()
# Get the name of the current object, the camera
name = get_name()
# Move the camera
move_obj(name, [0, -8, 0])
# Rotate the camera
rotate_obj(name, [90, 0, 0])
# Set camera to orthographic
bpy.context.active_object.data.type = "ORTHO"


"""Create a material with an Emission Shader"""
# Create a material named "Material" if it does not exist
mat_name = "Material"
mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)

# Enable nodes for the material
mat.use_nodes = True
# Get a reference to the material's node tree
nodes = mat.node_tree.nodes

# Remove the 'Principled BSDF' node if there is one
if (nodes.get('Principled BSDF') is not None):
    nodes.remove(nodes.get('Principled BSDF'))
    
# Remove the 'Emission' node if there is one
if (nodes.get('Emission') is not None):
    nodes.remove(nodes.get('Emission'))

# Get a reference to the material's output node
mat_output = nodes.get('Material Output')
# Create a new Emission shader
emission = nodes.new('ShaderNodeEmission')
# Set the color for the Emission shader
emission.inputs['Color'].default_value = (0, 0.5, 1, 1)
# Link the Emission shader to the Surface value of the output node
mat.node_tree.links.new(mat_output.inputs[0], emission.outputs[0])


"""Create a cone with the Emission material"""
# Create a new cone with 3 vertices
bpy.ops.mesh.primitive_cone_add(vertices=3)

# Get the name of the new cone
name = get_name()
# Rotate the cone
rotate_obj(name, [90, 180, 0])
# Move cone to origin
move_obj(name, [0, 0, -0.25])
# Reduce the size of the cone
scale = 0.75
scale_obj(name, [scale]*3)

# Get a reference to the currently active objecct
cone = bpy.context.active_object
# Assign the material with the Emission shader to the cone
if cone.data.materials:
    cone.data.materials[0] = mat
else:
    cone.data.materials.append(mat)


"""Turn the cone into a triangle"""
# Get the mesh for the cone
mesh = bpy.context.object.data

# Get a BMesh representation from current mesh in edit mode
bm = bmesh.new()
bm.from_mesh(mesh)

# Get a list of vertices
verts = [v for v in bm.verts]
# Delete the middle face
bmesh.ops.delete(bm, geom=[verts[3]], context='VERTS')
# Update the mesh
bm.to_mesh(mesh)
# Free the Bmesh representation and prevent further access
bm.free()

# Set the origin to geometry
bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")


"""Duplicate the triangle"""
# Duplicate the current object
bpy.ops.object.duplicate()
# Get the name of the current object, the triangle
name = get_name()
# Move the duplicate in front of the original
move_obj(name, [0, -0.05, -0.25])


"""Create a new material that will make objects behind it transparent"""
# Create a material named "X-ray" if it does not exist
mat_name = "X-ray"
mat = bpy.data.materials.get(mat_name) or bpy.data.materials.new(mat_name)

# Enable nodes for the material
mat.use_nodes = True
# Get a reference to the material's node tree
nodes = mat.node_tree.nodes

# Remove the 'Principled BSDF' node if there is one
if (nodes.get('Principled BSDF') is not None):
    nodes.remove(nodes.get('Principled BSDF'))
    
# Remove the 'Holdout' node if there is one
if (nodes.get('Holdout') is not None):
    nodes.remove(nodes.get('Holdout'))

# Get a reference to the material's output node
mat_output = nodes.get('Material Output')
# Create a new Holdout shader
holdout = nodes.new('ShaderNodeHoldout')
# Link the Holdout shader to the Surface value of the output node
mat.node_tree.links.new(mat_output.inputs[0], holdout.outputs[0])

# Assign the material with the Holdout shader to the currently active object
bpy.context.active_object.data.materials[0] = mat



"""Set up for animation"""
# Set the render frame rate to 60
bpy.context.scene.render.fps = 60

# Set the start frame to 0
bpy.data.scenes['Scene'].frame_start = 0
# Set the end frame to 250
bpy.data.scenes['Scene'].frame_end = 250
# Set the current frame to 0
bpy.data.scenes['Scene'].frame_current = 0


"""Add keyframes to animate the X-ray triangle"""
# Get the name of the current object
xray_triangle = bpy.context.active_object
# Set values for keyframes
values = [[degToRadian(angle) for angle in [90, 180, 0]],
          [degToRadian(angle) for angle in [90, 145, 0]],
          [degToRadian(angle) for angle in [90, 90, 0]],
          [degToRadian(angle) for angle in [90, 180, 0]]]
# Set the frames for keyframes
frames = [20, 70, 120, 250]
# Add keyframes for the rotation of the xray_triangle
add_keyframe_sequence(xray_triangle, 'rotation_euler', values, frames)

# Set values for keyframes
values = [[scale]*3, [0.5]*3, [0]*3, [scale]*3]
# Set the frames for keyframes
frames = [10, 60, 100, 250]
# Add keyframes for the scale of the xray_triangle
add_keyframe_sequence(xray_triangle, 'scale', values, frames)

