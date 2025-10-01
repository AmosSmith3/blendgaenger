import bpy
import math
import pyproj
from mathutils import *
from random import seed, randint, random, uniform
from config import load_config

D = bpy.data
C = bpy.context

seed()

def generate_environment(config: load_config.RootConfig):
    """Generate landscape environment, including seafloor, boulders, and noise particles
    @param config: Configuration object
    """

    #Generate landscape
    generate_landscape_ant(config)

    #Project sensor trajectory onto landscape
    project_trajectory_to_landscape(config)

    #Create boulders
    create_boulders(config)

    #Create noise particles
    create_noise_particles(config)

def create_boulders(config: load_config.RootConfig):
    """Create boulders in the scene
    @param config: Configuration object
    """

     #Create boulders
    if(config.landscape.boulder_chance>randint(0,100)):

        scene_collection = bpy.context.view_layer.layer_collection
        bpy.context.view_layer.active_layer_collection = scene_collection

        directory = config.get_base_path()+"/geometry_node_templates/boulder_generation_node.blend/Collection/"
        bpy.ops.wm.append(directory=directory,filename="Boulders")

        bpy.ops.mesh.primitive_cube_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        boulder_obj = bpy.context.object
        boulder_obj.name = "Boulders"
        boulder_obj["categoryID"] = "boulder"
        boulder_obj["partID"] = "boulder"
        boulder_mat = bpy.data.materials.new(name="BoulderMaterial")
        if config.sonar.generate:
            boulder_mat_alpha = uniform(config.boulders.alpha_min,config.boulders.alpha_max)
        else:
            boulder_mat_alpha = 1.0
        boulder_mat.diffuse_color = (0.061, 0.039, 0.018, boulder_mat_alpha)

        bpy.ops.object.modifier_add(type='NODES')

        filename = "boulder_generation_node"
        directory = config.get_base_path()+"/geometry_node_templates/boulder_generation_node.blend/NodeTree/"
        bpy.ops.wm.link(directory=directory,filename=filename)
        bpy.context.active_object.modifiers[-1].node_group = bpy.data.node_groups['boulder_generation_node']
        bpy.context.object.modifiers["GeometryNodes"]["Socket_2"] = bpy.data.objects["SensorTrajectoryProjection"]
        bpy.context.object.modifiers["GeometryNodes"]["Socket_3"] = float(config.boulders.max_dist)
        bpy.context.object.modifiers["GeometryNodes"]["Socket_4"] = bpy.data.objects["Landscape"]
        bpy.context.object.modifiers["GeometryNodes"]["Socket_5"] = randint(0,1000)
        bpy.context.object.modifiers["GeometryNodes"]["Socket_6"] = config.boulders.density*0.05

        bpy.ops.object.modifier_apply(modifier="GeometryNodes")

        #Add material to boulders
        boulder_obj.material_slots[0].material = boulder_mat

        #Delete boulder collections to clean up
        boulder_col = bpy.data.collections.get("Boulders")
        if boulder_col is not None:
            bpy.data.collections.remove(boulder_col)

        print("     --Created boulders--")

def create_noise_particles(config: load_config.RootConfig):
    """Create noise particles in the scene
    @param config: Configuration object
    """

    if(config.landscape.noise_chance>randint(0,100)):
        bpy.ops.mesh.primitive_uv_sphere_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
        noise_obj = bpy.context.object
        noise_obj.name = "NoiseParticles"
        noise_obj["categoryID"] = "none"
        noise_obj["partID"] = "none"
        noise_mat = bpy.data.materials.new(name="NoiseParticleMaterial")
        noise_alpha = uniform(0.5,1.0)
        noise_mat.diffuse_color = (0.5, 0.5, 0.5, noise_alpha)

        bpy.ops.object.modifier_add(type='NODES')

        filename = "noise_generator"
        directory = config.get_base_path()+"/geometry_node_templates/particle_noise.blend/NodeTree/"
        bpy.ops.wm.link(directory=directory,filename=filename)

        bpy.context.active_object.modifiers[-1].node_group = bpy.data.node_groups['noise_generator']
        bpy.context.object.modifiers["GeometryNodes"]["Input_2"] = bpy.data.objects["Landscape"]
        bpy.context.object.modifiers["GeometryNodes"]["Input_3"] = randint(0,999)
        bpy.ops.object.modifier_apply(modifier="GeometryNodes")

        bpy.data.objects["NoiseParticles"].data.materials[0] = bpy.data.materials["NoiseParticleMaterial"]

        print("     --Created noise particles--")

def project_trajectory_to_landscape(config: load_config.RootConfig):
    """Project sensor trajectory onto landscape surface
    @param config: Configuration object
    """

    bpy.context.view_layer.objects.active = bpy.data.objects["Landscape"]

    #Project trajectory onto landscape surface
    obj = bpy.data.objects.get("SensorTrajectoryProjection")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = None
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True,rotation=False,scale=False)

    filename = "trajectory_projection_node"
    directory = config.get_base_path()+"/geometry_node_templates/sensor_trajectory_projection_node.blend/NodeTree/"
    bpy.ops.wm.link(directory=directory,filename=filename)
    modifier = obj.modifiers.new(name="GeometryNodes", type="NODES")
    modifier.node_group = bpy.data.node_groups['trajectory_projection_node']
    modifier["Input_2"] = bpy.data.objects["Landscape"]
    bpy.ops.object.modifier_apply(modifier="GeometryNodes")

    print("     --Projected sensor trajectory onto seafloor--")

def generate_landscape_ant(config: load_config.RootConfig):
    """Generate landscape using ANT landscape addon
    @param config: Configuration object
    """

    # add landscape
    bpy.ops.mesh.landscape_add(refresh=True)
    lscp = bpy.context.object.ant_landscape

    # randomize landscape
    newSeed = randint(0, 99999)
    lscp.random_seed = newSeed

    # scale landscape
    sizeFactor = 2
    lscp.mesh_size_x = sizeFactor
    lscp.mesh_size_y = sizeFactor

    # set number of squares in each direction
    lscp.subdivision_x = 128
    lscp.subdivision_y = 128

    lscp.height = 0.08 #0.2
    lscp.edge_falloff = '0'

    # triangulate faces
    lscp.tri_face = True

    # make things smooth
    lscp.smooth_mesh = True

    obj = bpy.context.object

    # resize landscape object
    scale = config.landscape.size / sizeFactor

    obj.scale[0] = scale
    obj.scale[1] = scale
    obj.scale[2] = (randint(20, 100) / 5.0)

    # update landscape
    bpy.ops.mesh.ant_landscape_regenerate()

    landscapeObject = bpy.context.object

    # convert local vertex coordinates to world coordinates
    # https://blender.stackexchange.com/a/1313/95167
    coords = [(landscapeObject.matrix_world @ v.co) for v in landscapeObject.data.vertices]

    mat = bpy.data.materials.new(name="LandscapeMaterial")
    if config.sonar.generate:
        landscape_mat_alpha = uniform(config.landscape.alpha_min,config.landscape.alpha_max)
    else:
        landscape_mat_alpha = 1.0
    mat.diffuse_color = (0.896, 0.919, 0.653, landscape_mat_alpha)
    landscapeObject.data.materials.append(mat)
    landscapeObject.name = "Landscape"
    landscapeObject.data.name = "LandscapeMesh"

    landscapeObject["categoryID"] = "ground"
    landscapeObject["partID"] = "ground"

    bpy.context.view_layer.objects.active = bpy.data.objects["Landscape"]

    #Set scale, position, and rotation of landscape
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    print("     --Created seafloor--")