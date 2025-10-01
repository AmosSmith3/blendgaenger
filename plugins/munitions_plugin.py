import bpy
import math
import os
import csv
from random import seed, randint, uniform, choice
from config import load_config
from classes.Vector import Vector
import re

from mathutils import Vector as BlenderVector

D = bpy.data
C = bpy.context

#Initialize random generator
seed()

def project_point_to_landscape(point, landscape_obj):
    """Projects a point downwards onto the landscape using raycasting.

    Args:
        point: The 3D point to project (Vector or tuple)
        landscape_obj: The landscape object to project onto

    Returns:
        BlenderVector: The projected point on the landscape surface, or None if no hit
    """
    if landscape_obj is None:
        print("Landscape object not found")
        return None

    # Convert point to Blender Vector if needed
    if not isinstance(point, BlenderVector):
        point = BlenderVector(point)

    # Create ray origin high above the point
    ray_origin = BlenderVector((point.x, point.y, point.z + 1000))

    # Ray direction pointing downwards
    ray_direction = BlenderVector((0, 0, -1))

    # Transform ray to object's local space
    matrix_inv = landscape_obj.matrix_world.inverted()
    ray_origin_local = matrix_inv @ ray_origin
    ray_direction_local = matrix_inv.to_3x3() @ ray_direction

    # Perform raycast
    hit, location, normal, face_index = landscape_obj.ray_cast(
        ray_origin_local,
        ray_direction_local
    )

    if hit:
        # Transform hit location back to world space
        world_location = landscape_obj.matrix_world @ location
        return world_location
    else:
        print(f"No hit found for point {point}")
        return None

def save_munition_info(obj, config: load_config.RootConfig, iteration: int, save_dir: str = None):
    """Saves the bounding box information of the munition object to a CSV file
    Args:
        obj: The munition object to save information from.
        config: The configuration object containing settings.
        iteration: The current iteration number for naming.
        save_dir: The directory where the CSV file will be saved.
    """

    # Extract dimensions, location, and rotation of the object
    dimensions = obj.dimensions
    print(f"Dimensions of {obj.name}: {dimensions}")
    location = obj.location
    print(f"Location of {obj.name}: {location}")
    rotation = obj.rotation_euler
    print(f"Rotation of {obj.name}: {rotation}")

    # Save the bounding box information to a KITTI format TXT file
    if config.munitions.save_bb_info:
        txt_file = f"{save_dir}/{iteration:05d}.txt"

        with open(txt_file, "a") as f:
            # Extract object type from name (remove instance number suffix if present)
            object_type = re.sub(r'_\d+$', '', obj.name)

            # KITTI format: <object_type> <truncation> <occlusion> <alpha> <left> <top> <right> <bottom> <height> <width> <length> <x> <y> <z> <rotation_y>
            # Setting truncation, occlusion, alpha, left, top, right, bottom to 0
            line = f"{object_type} 0 0 0 0 0 0 0 {dimensions.z:.8f} {dimensions.x:.8f} {dimensions.y:.8f} {location.x:.8f} {location.y:.8f} {location.z:.8f} {rotation.z:.8f}\n"
            f.write(line)

#Main function to generate munitions
def gen_munition(config: load_config.RootConfig, iteration: int, save_dir: str = None):
    """Generates munitions in the scene based on the configuration.
    Args:
        config: The configuration object containing settings.
        iteration: The current iteration number for naming.
        save_dir: The directory where the bounding box information will be saved.
    """

    landscape_obj = bpy.data.objects.get("Landscape")

    directory = config.get_base_path()+"/geometry_node_templates/munitions.blend"

    with bpy.data.libraries.load(directory) as (data_from, data_to):
        data_to.collections.append("MunitionsCollection")

    munitions_collection = bpy.data.collections.get("MunitionsCollection")

    sensor_proj_obj = bpy.data.objects.get("SensorTrajectoryProjection")

    munition_name = config.munitions.munition_type

    #Check if the munition_name exists in collection
    if munition_name not in munitions_collection.objects:
        print(f"Munition {munition_name} not found in collection")
        print(f"Available choices are: {munitions_collection.objects.keys()}")
        return

    x_max = 3.0
    y_max = 3.0
    z_max = 0.25

    #Number of munitions to create
    num_munitions = config.munitions.num_munitions
    munition_points = []

    bpy.ops.object.select_all(action='DESELECT')

    for i in range(num_munitions):

        point_found = False
        projected_point = None

        while not point_found:
            # Set the location of the munition to a random point on the sensor trajectory projection
            point = sensor_proj_obj.data.vertices[randint(0, len(sensor_proj_obj.data.vertices)-1)].co

            point_x = point.x + uniform(-x_max, x_max)
            point_y = point.y + uniform(-y_max, y_max)
            point_z = point.z + 10.0 #uniform(-z_max, z_max)

            # Project the point onto the landscape
            projected_point_test = project_point_to_landscape((point_x, point_y, point_z), landscape_obj)

            if projected_point_test is None:
                print(f"Failed to project point onto landscape. Skipping munition {i}")
                continue
            else:
                projected_point = projected_point_test
                point_found = True

        point_x, point_y, point_z = projected_point.x, projected_point.y, projected_point.z

        point_vec = Vector(point_x, point_y, point_z + uniform(-z_max, z_max))

        point_too_close = False

        for occ_point in munition_points:
            if point_vec.distance(occ_point) < config.munitions.min_distance:
                print(f"Point too close to existing munition. Skipping...")
                point_too_close = True
                break

        if point_too_close:
            continue

        # Copy object from collection and assign instance number
        obj = munitions_collection.objects.get(munition_name)
        obj = obj.copy()
        obj.data = obj.data.copy()
        obj.name = f"{munition_name}_{i}"
        bpy.context.collection.objects.link(obj)

        mat = bpy.data.materials.new(name=f"{munition_name}_{i}_material")
        mat.diffuse_color = (0.281, 0.244, 0.263, uniform(config.munitions.alpha_min, config.munitions.alpha_max))
        obj.data.materials.append(mat)
        obj.active_material = mat

        munition_points.append(point_vec)

        obj.location = (point_x, point_y, point_z)

        # Set random rotation for the munition
        x_rad = math.radians(randint(0, 360))
        y_rad = math.radians(randint(-25,25))
        z_rad = math.radians(randint(0, 360))

        if munition_name == "mine":
            # Mines are usually flat, so we set the rotation around the X and Y axis to a small random value
            x_rad = math.radians(randint(-10, 10))
            y_rad = math.radians(randint(-10, 10))
            z_rad = math.radians(randint(0, 360))

        obj.rotation_euler = (x_rad, y_rad, z_rad)

        #Apply properties for sonar data label generation
        obj["categoryID"] = "munition"
        obj["partID"] = "munition"
        obj.select_set(True)

        save_munition_info(obj, config, iteration, save_dir)


    bpy.context.view_layer.objects.active = bpy.data.objects[f"{munition_name}_0"]
    bpy.ops.object.join()
    bpy.context.view_layer.objects.active = None

    return

