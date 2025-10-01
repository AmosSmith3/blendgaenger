import bpy
from config import load_config

def generate_data(config: load_config.RootConfig, iter_num: int, save_dir = ''):

    # Create camera as sonar sensor
    bpy.ops.object.camera_add()

    # Set sensor to follow path
    bpy.ops.object.constraint_add(type='FOLLOW_PATH')
    bpy.context.object.constraints["Follow Path"].use_curve_follow = True
    bpy.context.object.constraints["Follow Path"].target = bpy.data.objects["SensorTrajectory"]
    bpy.ops.constraint.followpath_path_animate(constraint="Follow Path", owner='OBJECT')
    bpy.data.curves["NurbsPath"].use_path_clamp = True
    bpy.data.curves["NurbsPath"].path_duration = 600

    # Set camera to look forward along path (90deg), sonar is emitted from underside
    bpy.context.object.rotation_euler[0] = 1.5708

    # Attach Blainder addon and set parameters
    bpy.context.scene.scannerProperties.scannerObject = bpy.data.objects["Camera"]
    bpy.context.scene.scannerProperties.scannerCategory = 'sonar'
    bpy.context.scene.scannerProperties.scannerType = 'sideScan'
    bpy.context.scene.scannerProperties.fovSonar = config.sonar.fov
    bpy.context.scene.scannerProperties.sonarStepDegree = config.sonar.resolution
    bpy.context.scene.scannerProperties.frameEnd = 600
    bpy.context.scene.scannerProperties.sonarMode3D = True
    bpy.context.scene.scannerProperties.enableAnimation = True
    
    # Set gaussian noise parameters
    bpy.context.scene.scannerProperties.noiseType = 'gaussian'
    bpy.context.scene.scannerProperties.addNoise = True
    bpy.context.scene.scannerProperties.mu = config.sonar.noise_mean
    bpy.context.scene.scannerProperties.sigma = config.sonar.noise_std
    bpy.context.scene.scannerProperties.addConstantNoise = False

    # Set interference noise parameters
    bpy.context.scene.scannerProperties.interferenceNoise = config.sonar.interference_noise
    bpy.context.scene.scannerProperties.interferenceNoiseChancePerPing = config.sonar.interference_noise_chance_per_ping
    bpy.context.scene.scannerProperties.interferenceNoiseMin = config.sonar.interference_noise_min
    bpy.context.scene.scannerProperties.interferenceNoiseMax = config.sonar.interference_noise_max
    bpy.context.scene.scannerProperties.interferenceNoiseChancePerBeam = config.sonar.interference_noise_chance_per_beam
    
    # Set output file name and path    
    bpy.data.scenes["Scene"].scannerProperties.dataFileName = f'{iter_num:05d}'
    bpy.data.scenes["Scene"].scannerProperties.dataFilePath = save_dir + "/"
    bpy.data.scenes["Scene"].scannerProperties.exportCSV = config.sonar.save_csv
    bpy.data.scenes["Scene"].scannerProperties.receptionThreshold = 0

    #Execute sonar scan
    bpy.ops.wm.execute_scan()

    if config.sonar.save_csv: 
        print(f"    Sonar data saved: {save_dir + '/' + f'{iter_num:05d}' + '.csv'}")

def finish_scene():
    for obj in bpy.data.objects:
        obj.select_set(False)

    bpy.context.view_layer.objects.active = None