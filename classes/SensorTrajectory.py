import math
import os
from pathlib import Path
from random import randint, choice, randint, uniform
import matplotlib.pyplot as plt
from classes.Vector import Vector
from config import load_config

class SensorTrajectory:
    """Class to generate a sensor trajectory, with straight and bend segments.
    """

    def __init__(self):
        self.points = list[Vector]()
        self.current_heading = float(0)
        self.bend_points = list[Vector]()
        self.terminated = False

    def straight_segment(self, distance: float, edge_coordinate: float):
        """Generate a straight segment of trajectory, with a given distance.
        If the segment exceeds the edge of the landscape, the trajectory is terminated.
        @param distance: Length of straight segment
        @param edge_coordinate: Coordinate of edge of landscape
        """

        initial_point = self.points[-1]

        #Calculate new x/y pairs until requested distance is covered
        while self.points[-1].distance(initial_point) < distance:

            next_point = self.points[-1] + 0.5*Vector(math.cos(self.current_heading), math.sin(self.current_heading), 0)
            self.points.append(next_point)

            #Check if next point exceeds edge coordinates
            if abs(next_point.x) > edge_coordinate or abs(next_point.y) > edge_coordinate:
                self.terminated = True
                return

    def curve_segment(self, new_angle: float, bend_radius: float, edge_coordinate: float):
        """Generate a curve segment of trajectory, with a given angle and bend radius.
        If the segment exceeds the edge of the landscape, the trajectory is terminated.
        @param new_angle: Angle of bend segment
        @param bend_radius: Radius of bend segment
        @param edge_coordinate: Coordinate of edge of landscape
        """

        initial_point = self.points[-1]
        self.bend_points.append(initial_point)
        bend_offset = Vector(0,0,0)

        #Iterate through bend angle, with step size of 1 degree
        for i in range(0, int(new_angle) + int(math.copysign(1,new_angle)), int(math.copysign(1,new_angle))):

            #Calculate angle based on current heading and new angle
            angle = (math.radians(i) + self.current_heading - int(math.copysign(1,new_angle))*math.pi/2)

            #Calcuate position of point in bend
            arc_length = bend_radius*Vector(math.cos(angle), math.sin(angle), 0)

            #Calculate offset due to bend radius
            if i == 0:
                bend_offset = arc_length
                continue

            #Add initial point to bend, and subtract bend radius offset
            next_point = initial_point + arc_length - bend_offset

            self.points.append(next_point)

            #Check if next point exceeds edge coordinates
            if abs(next_point.x) > edge_coordinate or abs(next_point.y) > edge_coordinate:
                self.terminated = True
                return

        self.bend_points.append(self.points[-1])

        #Update current heading
        test_heading = (self.current_heading + math.radians(new_angle))%(2*math.pi)
        self.current_heading = math.atan2(math.sin(test_heading), math.cos(test_heading))

    def generate_trajectory(self, config: load_config.RootConfig, debug: bool = False):
        """Generate a trajectory based on configuration file.
        @param config: Configuration file
        @param debug: Debug flag to print additional information
        """

        #Generate starting point along edge of landscape
        edge_coordinate = config.sensor_trajectory.size/2

        start_axis = randint(0,1)

        if start_axis: #x-axis
            self.points.append(Vector(choice((-1,1))*edge_coordinate, uniform(-edge_coordinate, edge_coordinate), 0))
        else: #y-axis
            self.points.append(Vector(uniform(-edge_coordinate, edge_coordinate), choice((-1,1))*edge_coordinate, 0))

        #Generate starting heading based on start position plus 180 degrees
        start_heading = math.atan2(self.points[0].y,self.points[0].x)%(2*math.pi)
        self.current_heading = (start_heading + math.pi)%(2*math.pi)
        if debug: print(f"  Start heading: {math.degrees(self.current_heading)} degrees")

        #Create initial straight segment
        self.straight_segment(randint(5,10),edge_coordinate)

        #Create Bends
        num_bends = randint(config.sensor_trajectory.bend_occ_min, config.sensor_trajectory.bend_occ_max)
        if debug: print(f"  Trajectory bends: {num_bends}")

        for i in range(0,num_bends):

            #Determine bend radius and angle
            bend_radius = randint(config.sensor_trajectory.bend_radius_min, config.sensor_trajectory.bend_radius_max)
            bend_angle = choice((-1,1))*randint(1,4)*10.0 #bend angle from 10-40 degrees, +/-

            if(not self.terminated):
                self.curve_segment(bend_angle, bend_radius, edge_coordinate)
                if debug: print(f"      Bend {i+1}: Bend angle: {bend_angle} degrees, Bend radius: {bend_radius} m, New heading: {math.degrees(self.current_heading)} degrees")

            if(not self.terminated):
                self.straight_segment(randint(5,10),edge_coordinate)

        #Create final straight section
        if(not self.terminated):
            self.straight_segment(2*edge_coordinate,edge_coordinate)

if __name__ == "__main__":

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    config_filename = "cleanseas_config.yaml"
    config_file_path = project_root / "config" / config_filename
    myconfig = load_config.load_configuration(config_file_path)

    trajectory = SensorTrajectory()
    trajectory.generate_trajectory(myconfig,debug=True)

    #plot sensor trajectory points
    x = [point.x for point in trajectory.points]
    y = [point.y for point in trajectory.points]
    plt.figure(0)
    plt.plot(x,y)
    plt.plot(x[0],y[0],'go')
    plt.plot(x[-1],y[-1],'ro')

    #plot bend points
    bend_x = [point.x for point in trajectory.bend_points]
    bend_y = [point.y for point in trajectory.bend_points]
    plt.plot(bend_x,bend_y,'bo')

    plt.xlim((-30,30))
    plt.ylim((-30,30))
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend(['Trajectory','Start','End','Bend'])
    plt.title('Sensor Trajectory')
    plt.grid()
    plt.show()



