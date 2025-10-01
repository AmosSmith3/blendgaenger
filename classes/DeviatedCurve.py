import os
import numpy as np
from random import uniform
import math
import matplotlib.pyplot as plt
from pathlib import Path
from config import load_config
from classes.SensorTrajectory import SensorTrajectory
from classes.Vector import Vector

class DeviatedCurve:
    """Class to generate a deviated curve, given a base curve
    """

    def __init__(self, base_trajectory: SensorTrajectory, noise_param: int):
        """Initialize deviated curve with base curve and noise parameter
        @param base_trajectory: Base sensor trajectory to deviate from
        @param noise_param: Parameter to determine deviation"""

        self.base_trajectory = base_trajectory
        self.points = list[Vector]()
        self.current_heading = float(0)

        self.generate_deviation(noise_param)

    def generate_deviation(self, noise_param: int):
        """Generate deviated curve from base curve
        @param noise_param: Parameter to determine deviation"""

        match noise_param:

            case 1: #Low deviation
                noise_max = 0.5
                dist_delta = 0.25
                goal_distance_thold = 2.0
                end_goal_distance_thold = 1.0
                error_thold = 5.0
                heading_weight = 0.2

            case 2: #High deviation
                noise_max = 1.5
                dist_delta = 0.25
                goal_distance_thold = 2.0
                end_goal_distance_thold = 1.0
                error_thold = 10.0
                heading_weight = 0.2

            case _:
                raise Exception("Invalid noise parameter for deviated sensor trajectory")

        #Copy original base trajectory points
        orig_x = np.array([point.x for point in self.base_trajectory.points])
        orig_y = np.array([point.y for point in self.base_trajectory.points])

        #Add noise to original points
        for i in range(0,len(orig_x)):
            orig_x[i] += uniform(-noise_max, noise_max)
            orig_y[i] += uniform(-noise_max, noise_max)

        #Initialize new deviated trajectory with first point
        self.points.append(Vector(orig_x[0], orig_y[0], self.base_trajectory.points[0].z))

        #Calculate initing heading based on original base trajectory
        self.current_heading = math.atan2(orig_y[1]-orig_y[0], orig_x[1]-orig_x[0])

        #Index of current goal point in the original base trajectory that is being tracked
        goal_idx = 1

        #Main tracking loop
        while True:

            #Find next goal point in base trajectory
            goal_point = Vector(orig_x[goal_idx], orig_y[goal_idx], self.base_trajectory.points[goal_idx].z)

            #Find distance to goal point
            dist_to_goal = self.points[-1].distance(goal_point)

            #If distance to goal point is less than goal_distance_thold
            if dist_to_goal < goal_distance_thold:

                #Increment current goal index
                goal_idx += 1

                #Ensure that the current goal index is not out of bounds
                goal_idx = min(goal_idx, len(orig_x)-1)

                #If current goal is last element of original curve, and distance to this end goal is less then end_goal_distance_thold, break
                if goal_idx == len(orig_x)-1 and dist_to_goal < end_goal_distance_thold:
                    break

                #Else if the goal is not at the end of the base curve, go to next iteration of loop
                elif goal_idx != len(orig_x)-1:
                    continue

            #Catch if trajectory deviates too far from the goal by error_thold
            elif dist_to_goal > error_thold:
                print("     ERROR: Sensor trajectory deviated too far from base sensor trajectory")
                break

            #Find heading to goal point
            goal_diff = goal_point - self.points[-1]

            goal_point_rot = Vector(goal_diff.x*math.cos(-self.current_heading) - goal_diff.y*math.sin(-self.current_heading), 
                                    goal_diff.x*math.sin(-self.current_heading) + goal_diff.y*math.cos(-self.current_heading),
                                    0)

            goal_heading = math.atan2(goal_point_rot.y, goal_point_rot.x)

            #Adjust current heading with weighted goal heading
            self.current_heading += heading_weight*goal_heading

            #Update current position
            self.points.append(self.points[-1] + dist_delta*Vector(math.cos(self.current_heading), math.sin(self.current_heading), 0))

if __name__ == "__main__":

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_filename = "cleanseas_config.yaml"
    config_file_path = project_root / "config" / config_filename
    myconfig = load_config.load_configuration(config_file_path)

    sensor_trajectory = SensorTrajectory()
    sensor_trajectory.generate_trajectory(myconfig,debug=True)

    deviated_trajectory = DeviatedCurve(sensor_trajectory, myconfig.sonar.sensor_path_deviation_noise_params)

    #plot base curve points
    x = [point.x for point in sensor_trajectory.points]
    y = [point.y for point in sensor_trajectory.points]
    plt.plot(x,y)

    #plot deviated curve points
    x_dev = [point.x for point in deviated_trajectory.points]
    y_dev = [point.y for point in deviated_trajectory.points]
    plt.plot(x_dev,y_dev)
    plt.plot(x_dev[0],y_dev[0],'go')

    plt.legend(['Base Trajectory', 'Deviated Trajectory', 'Start Point'])
    plt.title('Deviated Trajectory')
    plt.xlim((-30,30))
    plt.ylim((-30,30))
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()