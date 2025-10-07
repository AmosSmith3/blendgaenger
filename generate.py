import bpy
import os
import sys
from datetime import datetime
from shutil import copy
import pathlib

#Add path depending on if headless or GUI usage
if (bpy.context.space_data == None): #Running headless
    file_dir = str(pathlib.Path(__file__).parent.resolve())
else: #Running through GUI
    file_dir = str(os.path.dirname(bpy.context.space_data.text.filepath))
sys.path.append(file_dir)

from plugins import environment_plugin, sonar_plugin, munitions_plugin, sensor_plugin
from config import load_config
from utils.ArgumentParserForBlender import ArgumentParserForBlender

from mathutils import *
D = bpy.data
C = bpy.context

#reload plugins to adopt new changes
import importlib
importlib.reload(environment_plugin)
importlib.reload(sonar_plugin)
importlib.reload(munitions_plugin)
importlib.reload(load_config)
importlib.reload(sensor_plugin)

#function to clear the current Blender scene
def clear_scene():

    #delete libraries
    bpy.data.batch_remove(bpy.data.libraries)

    #delete objects
    for object in bpy.data.objects:
        bpy.data.objects.remove(object)

    #delete textures
    for texture in bpy.data.textures:
        bpy.data.textures.remove(texture)

    #delete materials
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)

    #delete meshes
    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

    #delete curves
    for curve in bpy.data.curves:
        bpy.data.curves.remove(curve)

    #delete collections
    for col in bpy.data.collections:
        bpy.data.collections.remove(col)

    bpy.ops.outliner.orphans_purge()

def Update3DViewPorts():
    #should use modal operator? https://blender.stackexchange.com/questions/28673/update-viewport-while-running-script
    if myconfig.general.continuous_play:
        bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

if __name__ == "__main__":

    # Parse CLI arguments
    parser = ArgumentParserForBlender(description='Generate an underwater scene')
    parser.add_argument("-c","--config", type=str, help='Path to the configuration file')
    parser.add_argument("-o","--output", type=str, help='Path to the output directory')
    args = parser.parse_args()

    # Print Start Time
    print("-----------------------------------")
    print("BLENDgänger - Underwater Scene Generator for UXO Perception Tasks")
    print("Start Time: ", datetime.now().strftime("%Y/%m/%d %H:%M:%S"))

    # Determine blender path
    if (bpy.context.space_data == None):
        print("Running headless")
        base_path = str(pathlib.Path(__file__).parent.resolve())
    else:
        print("Running through GUI")
        base_path = os.path.dirname(bpy.context.space_data.text.filepath)

    print("-----------------------------------")

    # Set configuration file if CLI param is set
    if args.config:
        config_file = args.config
    else:
        config_file = base_path + "/config/example.yaml"

    #Read in configuration file
    myconfig = load_config.load_configuration(config_file)
    myconfig.set_base_path(base_path)

    #Set order of labels to be applied to point clouds
    bpy.context.scene["labels_list"] = ["none","ground","boulder","munition"]

    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            region = area.spaces[0].region_3d
            region.view_matrix = Matrix((
                ( 0.7029,  0.7112, -0.0127,   3.1937),
                (-0.3595,  0.3706,  0.8564,   4.2320),
                ( 0.6138, -0.5974,  0.5161, -64.9235),
                ( 0.0000,  0.0000,  0.0000,   1.0000)
            ))

    Update3DViewPorts()

    #Ensure output directory sructure if data saves are to occur
    if(myconfig.general.dae_output or myconfig.sonar.save_csv or myconfig.munitions.save_bb_info):
        if args.output:
            save_dir_base = args.output + r"/"
        else:
            save_dir_base = myconfig.get_base_path() + r"/output/"

        save_dir = save_dir_base + datetime.now().strftime("%Y_%m_%d-%H_%M_%S")

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        if(myconfig.general.dae_output):
            dae_save_dir = save_dir + "/dae"
            if not os.path.exists(dae_save_dir):
                os.makedirs(dae_save_dir)

        if(myconfig.sonar.save_csv):
            sonar_save_dir = save_dir + "/sonar"
            if not os.path.exists(sonar_save_dir):
                os.makedirs(sonar_save_dir)

        if(myconfig.munitions.save_bb_info):
            munitions_save_dir = save_dir + "/munitions_bb_info"
            if not os.path.exists(munitions_save_dir):
                os.makedirs(munitions_save_dir)

        #Save copy of config file into output directory
        copy(config_file,save_dir)

    iterations = myconfig.general.iterations

    for i in range(iterations):

        print("\n------ ITERATION: ", i, " --------")

        print("--SCENE GENERATION START--")

        clear_scene()

        print("--SENSOR TRAJECTORY GENERATION--")

        sensor_plugin.gen_sensor_trajectory(myconfig)

        print("--ENVIRONMENT GENERATION--")
        environment_plugin.generate_environment(myconfig)

        if(myconfig.munitions.generate):
            print("--MUNITIONS GENERATION--")
            munitions_plugin.gen_munition(myconfig, i, munitions_save_dir if myconfig.munitions.save_bb_info else None)

        if(myconfig.sonar.generate):
            print("--SONAR GENERATION--")
            if(myconfig.sonar.save_csv):
                sonar_plugin.generate_data(myconfig, i, sonar_save_dir)
            else:
                sonar_plugin.generate_data(myconfig, i)
        else:
            sonar_plugin.finish_scene()

        Update3DViewPorts()

        print("--SCENE GENERATION COMPLETE--")

        if(myconfig.general.dae_output):
            dae_filepath = dae_save_dir + "/" + f'{i:05d}' + "_blender_world.dae"
            bpy.ops.wm.collada_export(filepath=dae_filepath, apply_modifiers=True)
            print(f"    Exported .dae file to {dae_filepath}")


