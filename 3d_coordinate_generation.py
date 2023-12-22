import bpy
import os
import json
import numpy as np
#from bpy_extras.object_utils import world_to_camera_view


# Load intrinsic matrix
mesh_file_path = r"C:\Users\rishi\OneDrive\Desktop\iavp_project\0047.obj"

# Output directory and file name settings
#output_directory = r'C:\Users\rishi\OneDrive\Desktop\inb\outputblend'
#output_file_name_prefix = 'rendered_image_'
#json_output_file = 'camera_data.json'
outp = r"C:\Users\rishi\OneDrive\Desktop\iavp_project\segmented_images"
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

# Output directory and file name settings
outp = r"C:\Users\rishi\OneDrive\Desktop\iavp_project\segmented_images"
output_directory = outp
output_file_name_prefix = 'rendered_image_'
pointcloud_output_file = 'pointcloud2.json'

# Create an empty point cloud
point_cloud = []

# Predefined list of 20 colors
colors_list = [
    [255, 235, 13], [0, 128, 255], [255, 128, 0],
    [128, 0, 255], [255, 0, 128], [128, 255, 0],
    [0, 255, 128], [128, 128, 0], [0, 128, 128],
    [128, 0, 128], [0, 0, 255], [0, 255, 0],
    [255, 0, 0], [0, 0, 128], [0, 128, 0],
    [128, 255, 255], [255, 128, 255], [255, 255, 128],
    [128, 128, 128], [255, 255, 255]
]
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
# Load data from the JSON file
json_output_path = r"C:\Users\rishi\OneDrive\Desktop\iavp_project\camera_data.json"  # Update the path
with open(json_output_path, 'r') as json_file:
    camera_data = json.load(json_file)

# Create an empty list to store the point cloud data
point_cloud_data = []

# Loop through each entry in the JSON file
for filename in os.listdir(output_directory):
    if filename.endswith(".jpg"):
        image_path = os.path.join(outp, filename)
        print(image_path)
        angle = int(filename.split('.')[0].split('_')[-1])

        camera_matrix_world = np.array(camera_data[str(angle)]["extrinsic_matrix"])
        intrinsic_matrix = np.array(camera_data[str(angle)]['intrinsic_matrix'])

        try:
            # Load the PNG image
            bpy.ops.image.open(filepath=image_path)

            # Retrieve the loaded image
            image = bpy.data.images.get(os.path.basename(image_path))

            # Get image dimensions
         
            width, height = image.size
            img = np.array(image.pixels[:]).reshape((height, width, 4))
   
            print(width, height)
            depth = np.load(os.path.join(r'C:\Users\rishi\OneDrive\Desktop\iavp_project\generated_depth','rendered_image_'+str(angle)+'.npz'))
            point_cloud_data_a = []
 
            # Loop through each pixel in the image
            for y in range(height):
                for x in range(width):
                    if img[x, y][:3].any() > 0:
           
                        u = (x - intrinsic_matrix[0,2]) / 28
                        v = (y - intrinsic_matrix[1,2]) / 28
                        z = depth['dmap'][x,y]
#                        print(z* np.array([u,v, 1]))
                        Xc, Yc, Zc = z* np.array([u,v, 1])
       
                        [Xw, Yw, Zw, _ ]= np.array([Xc, Yc, Zc, 1]) @ np.linalg.inv(np.transpose(camera_matrix_world))
                        """

                        # NDC coordinates
                        ndc_coordinates = np.linalg.inv(intrinsic_matrix) @ pixel_coordinates
                        print(depth['dmap'][x,y])
                        if(depth['dmap'][x,y] != 0):
                            ndc_coordinates = np.append(ndc_coordinates, 1) * depth['dmap'][x,y]
                        else:
                            ndc_coordinates = np.append(ndc_coordinates, 1) * 1

                        # Camera coordinates
                        #print(camera_matrix_world)
                        camera_coordinates = camera_matrix_world @ ndc_coordinates
                        camera_coordinates /= camera_coordinates[3]
                       
                        # World coordinates
                   
                        world_coordinates = np.array(mesh_object.matrix_world) @ camera_coordinates
                        """

                        # Extract color information from the image
                        color = colors_list[int(img[x,y][0]*14)]
                        """

                        # Add the point and color to the point cloud data
                        alp,bet,gam = world_coordinates[:3]
                        alp = alp 
                        bet = bet 
                        gam = gam 
                        """

                        point_cloud_data.append({
                            'point': tuple([Xw,Yw,Zw]),
                            'color': tuple(color)
                        })
#            point_cloud_data.append({str(angle):point_cloud_data_a})
        except Exception as e:
            print(f"Error processing image {filename}: {str(e)}")
            continue
        break

point_cloud = {'0': point_cloud_data}
json_output = os.path.join(output_directory, pointcloud_output_file)
print('writing', end =' ...')
with open(json_output, 'w') as json_file:
    json.dump(point_cloud, json_file, indent=4)
print('complete')
