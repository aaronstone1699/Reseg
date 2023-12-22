import bpy
import math
import mathutils
import os
import json

import numpy as np

# Specify the path to your mesh file
mesh_file_path = r'C:\Users\rishi\OneDrive\Desktop\inb\0047.obj'

# Output directory and file name settings
output_directory = r'C:\Users\rishi\OneDrive\Desktop\inb\outputblend2'
output_file_name_prefix = 'rendered_image_'
json_output_file = 'camera_data.json'

def get_depth():
    """Obtains depth map from Blender render.
    :return: The depth map of the rendered camera view as a numpy array of size (H,W).
    """
    z = bpy.data.images['Viewer Node']
    w, h = z.size
    dmap = np.array(z.pixels[:], dtype=np.float32) # convert to numpy array
    dmap = np.reshape(dmap, (h, w, 4))[:,:,0]
    dmap = np.rot90(dmap, k=2)
    dmap = np.fliplr(dmap)
    return dmap

# Clear existing mesh objects and cameras in the scene
bpy.ops.object.select_all(action='DESELECT')
bpy.ops.object.select_by_type(type='MESH')
bpy.ops.object.delete()

bpy.ops.object.select_by_type(type='CAMERA')
bpy.ops.object.delete()

# Import the mesh
bpy.ops.import_scene.obj(filepath=mesh_file_path)

# Select the imported mesh
bpy.ops.object.select_by_type(type='MESH')
mesh_object = bpy.context.selected_objects[-1]
bpy.context.view_layer.objects.active = mesh_object

# Add a camera to the scene
bpy.ops.object.camera_add(location=(0, 0, 0), rotation=(math.radians(90), math.radians(0), math.radians(0)))
camera_object = bpy.context.object

# Set camera properties
camera_object.data.sensor_fit = 'HORIZONTAL'
camera_object.data.lens = 28
camera_object.data.sensor_width = 35  # Assuming a 35mm camera sensor width
camera_object.data.sensor_height = 35  # Assuming a 35mm camera sensor height

# Set resolution
bpy.context.scene.render.resolution_x = 256
bpy.context.scene.render.resolution_y = 256

bpy.ops.object.constraint_add(type='TRACK_TO')
track_constraint = camera_object.constraints["Track To"]
track_constraint.target = mesh_object
track_constraint.track_axis = 'TRACK_NEGATIVE_Z'

# Make the camera track the object
bpy.ops.object.select_all(action='DESELECT')
mesh_object.select_set(True)
camera_object.select_set(True)
bpy.context.view_layer.objects.active = camera_object

# Set the camera as the active camera
bpy.context.scene.camera = camera_object

# Update the scene
bpy.context.view_layer.update()

# Print information about the camera
print("\nCamera added successfully:")
print("Name:", camera_object.name)
print("Focal Length:", camera_object.data.lens)
print("Resolution:", bpy.context.scene.render.resolution_x, "x", bpy.context.scene.render.resolution_y)

# Get the camera transformation matrix (extrinsic matrix)
camera_matrix_world = camera_object.matrix_world
print("\nExtrinsic Matrix (Camera Transformation Matrix):")
print(camera_matrix_world)

# Calculate the intrinsic matrix
def get_calibration_matrix_K_from_blender(mode='simple'):

    scene = bpy.context.scene

    scale = scene.render.resolution_percentage / 100
    width = scene.render.resolution_x * scale # px
    height = scene.render.resolution_y * scale # px

    camdata = scene.camera.data

    if mode == 'simple':

        aspect_ratio = width / height
        K = np.zeros((3,3), dtype=np.float32)
        K[0][0] = width / 2 / np.tan(camdata.angle / 2)
        K[1][1] = height / 2. / np.tan(camdata.angle / 2) * aspect_ratio
        K[0][2] = width / 2.
        K[1][2] = height / 2.
        K[2][2] = 1.
        K.transpose()
    
    if mode == 'complete':

        focal = camdata.lens # mm
        sensor_width = camdata.sensor_width # mm
        sensor_height = camdata.sensor_height # mm
        pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y

        if (camdata.sensor_fit == 'VERTICAL'):
            # the sensor height is fixed (sensor fit is horizontal), 
            # the sensor width is effectively changed with the pixel aspect ratio
            s_u = width / sensor_width / pixel_aspect_ratio 
            s_v = height / sensor_height
        else: # 'HORIZONTAL' and 'AUTO'
            # the sensor width is fixed (sensor fit is horizontal), 
            # the sensor height is effectively changed with the pixel aspect ratio
            pixel_aspect_ratio = scene.render.pixel_aspect_x / scene.render.pixel_aspect_y
            s_u = width / sensor_width
            s_v = height * pixel_aspect_ratio / sensor_height

        # parameters of intrinsic calibration matrix K
        alpha_u = focal * s_u
        alpha_v = focal * s_v
        u_0 = width / 2
        v_0 = height / 2
        skew = 0 # only use rectangular pixels

        K = np.array([
            [alpha_u,    skew, u_0],
            [      0, alpha_v, v_0],
            [      0,       0,   1]
        ])
    
    return K

intrinsic_matrix = get_calibration_matrix_K_from_blender('complete')

print("\nIntrinsic Matrix:")
print(intrinsic_matrix)

# Set output directory and file name


# Dictionary to store camera data
camera_data = {}
plo ={90 :[1.0000,0.0000,0.0000],
 100 :[0.9848,0.1736,0.0000],
 110 :[0.9397,0.3420,0.0000],
 120 :[0.8660,0.5000,0.0000],
 130 :[0.7660,0.6428,0.0000],
 140 :[0.6428,0.7660,0.0000],
 150 :[0.5000,0.8660,0.0000],
 160 :[0.3420,0.9397,0.0000],
 170 :[0.1736,0.9848,0.0000],
 180 :[0.0000,1.0000,0.0000],
 190 :[-0.1736,0.9848,0.0000],
 200 :[-0.3420,0.9397,0.0000],
 210 :[-0.5000,0.8660,0.0000],
 220 :[-0.6428,0.7660,0.0000],
 230 :[-0.7660,0.6428,0.0000],
 240 :[-0.8660,0.5000,0.0000],
 250 :[-0.9397,0.3420,0.0000],
 260 :[-0.9848,0.1736,0.0000],
 270 :[-1.0000,0.0000,0.0000],
 280 :[-0.9848,-0.1736,0.0000],
 290 :[-0.9397,-0.3420,0.0000],
 300 :[-0.8660,-0.5000,0.0000],
 310 :[-0.7660,-0.6428,0.0000],
 320 :[-0.6428,-0.7660,0.0000],
 330 :[-0.5000,-0.8660,0.0000],
 340 :[-0.3420,-0.9397,0.0000],
 350 :[-0.1736,-0.9848,0.0000],
 0 :[-0.0000,-1.0000,0.0000],
 10 :[0.1736,-0.9848,0.0000],
 20 :[0.3420,-0.9397,0.0000],
 30 :[0.5000,-0.8660,0.0000],
 40 :[0.6428,-0.7660,0.0000],
 50 :[0.7660,-0.6428,0.0000],
 60 :[0.8660,-0.5000,0.0000],
 70 :[0.9397,-0.3420,0.0000],
 80 :[0.9848,-0.1736,0.0000]}
# Render for each camera position in plo dictionary
for angle, position in plo.items():
    # Set camera location
    camera_object.location = position

    # Set camera rotation
    #bpy.context.object.rotation_euler = (math.radians(90), 0, math.radians(0))

    # Set the frame for the current camera position
    bpy.context.scene.frame_set(angle)

    # Render the frame
    bpy.ops.render.render(write_still=True)
    bpy.context.scene.render.filepath = os.path.join(output_directory, output_file_name_prefix+str(angle)+'.png')

    # Save camera data to dictionary
    dmap = get_depth()
    np.savez_compressed(os.path.join(output_directory, output_file_name_prefix+str(angle)+".npz"), dmap=dmap)
    camera_matrix_world = camera_object.matrix_world
    
    camera_data[angle] = {
        "intrinsic_matrix": [list(row) for row in intrinsic_matrix],
        "extrinsic_matrix": [list(row) for row in camera_matrix_world],
        
        "image_path": bpy.context.scene.render.filepath
    }

# Save camera data to a JSON file
json_output_path = os.path.join(output_directory, json_output_file)
with open(json_output_path, 'w') as json_file:
    json.dump(camera_data, json_file, indent=4)

# Print message after rendering
print(f"\nImages rendered and saved successfully. Camera data saved to {json_output_path}.")
