import bpy
import math
from random import seed, randint, uniform, choice
from config import load_config
from classes.Vector import Vector
from classes.SensorTrajectory import SensorTrajectory
from classes.DeviatedCurve import DeviatedCurve

D = bpy.data
C = bpy.context

#Initialize random generator
seed()

#Main function to generate sensor trajectory
def gen_sensor_trajectory(config: load_config.RootConfig):
    """Generate a sensor trajectory based on configuration parameters
    @param config: Configuration object
    """

    sensor_trajectory = SensorTrajectory()
    sensor_trajectory.generate_trajectory(config)

    if config.sensor_trajectory.trajectory_deviation_param > 0:
        sensor_trajectory = DeviatedCurve(sensor_trajectory, config.sensor_trajectory.trajectory_deviation_param)

    ### Create trajectory object
    bpy.ops.curve.primitive_nurbs_path_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    traj_curve_obj = bpy.context.object
    traj_curve_obj.name = "SensorTrajectory"
    splines = traj_curve_obj.data.splines
    splines.remove(splines[0])
    splines.new("NURBS")
    spline = splines[0]
    spline.use_endpoint_u = True
    spline.points.add(len(sensor_trajectory.points)-1)

    for i, point in enumerate(sensor_trajectory.points):
        spline.points[i].co = (point.x, point.y, point.z, 1)

    traj_curve_obj.location[2] = uniform(config.sensor_trajectory.height_min,config.sensor_trajectory.height_max)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    ### Create trajectory projection onto landscape
    projection_path = traj_curve_obj.copy()
    projection_path.data = traj_curve_obj.data.copy()
    projection_path.name = "SensorTrajectoryProjection"
    projection_path.data.name="TrajectoryProjectionCurve"
    projection_path.location[2] = config.sensor_trajectory.height_max
    bpy.context.collection.objects.link(projection_path)
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = projection_path
    projection_path.select_set(True)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.convert(target='MESH')

    bpy.context.view_layer.objects.active = None

    return

