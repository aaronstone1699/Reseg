import json
import open3d as o3d
import numpy as np
from tqdm import tqdm

def read_json_file(file_path):
    print('loading ', file_path, end='...')
    with open(file_path, 'r') as file:
        data = json.load(file)
    print('done')
    return data

# Example usage
if __name__ == "__main__":
    json_file_path = ''

    # Read data from JSON file
    json_data = read_json_file(json_file_path)

    # Initialize an empty point cloud
    point_cloud = o3d.geometry.PointCloud()

    # Iterate through each key-value pair in the JSON data
    total_points = len(json_data['0'])
    for point_info in tqdm(json_data['0'], desc="Processing Points", total=total_points):
        # Convert each set of points and color to NumPy arrays and add them to the point cloud
        
        
        point_cloud.points.append(np.array([float(point_info['point'][0]), float(point_info['point'][1]), float(point_info['point'][2])]))
        point_cloud.colors.append(np.array([float(point_info['color'][0]) / 255.0, float(point_info['color'][1]) / 255.0, float(point_info['color'][2]) / 255.0]))

    # Save the resulting colored point cloud to a PLY file
    o3d.io.write_point_cloud('colored_projection.ply', point_cloud)

    print("Colored point cloud saved.")
