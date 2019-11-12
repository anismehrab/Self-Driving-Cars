#!/usr/bin/env python3

"""
2D Controller Class to be used for the CARLA waypoint follower demo.
"""

import cutils
import numpy as np

class Controller2D(object):
    def __init__(self, waypoints):
        self.vars                = cutils.CUtils()
        self._current_x          = 0
        self._current_y          = 0
        self._current_yaw        = 0
        self._current_speed      = 0
        self._desired_speed      = 0
        self._current_frame      = 0
        self._current_timestamp  = 0
        self._start_control_loop = False
        self._set_throttle       = 0
        self._set_brake          = 0
        self._set_steer          = 0
        self._waypoints          = waypoints
        self._conv_rad_to_steer  = 180.0 / 70.0 / np.pi
        self._pi                 = np.pi
        self._2pi                = 2.0 * np.pi

    def update_values(self, x, y, yaw, speed, timestamp, frame):
        self._current_x         = x
        self._current_y         = y
        self._current_yaw       = yaw
        self._current_speed     = speed
        self._current_timestamp = timestamp
        self._current_frame     = frame
        if self._current_frame:
            self._start_control_loop = True

    def update_desired_speed(self):
        min_idx       = 0
        min_dist      = float("inf")
        desired_speed = 0
        for i in range(len(self._waypoints)):
            dist = np.linalg.norm(np.array([
                    self._waypoints[i][0] - self._current_x,
                    self._waypoints[i][1] - self._current_y]))
            if dist < min_dist:
                min_dist = dist
                min_idx = i
        if min_idx < len(self._waypoints)-1:
            desired_speed = self._waypoints[min_idx][2]
        else:
            desired_speed = self._waypoints[-1][2]
        self._desired_speed = desired_speed

    def update_waypoints(self, new_waypoints):
        self._waypoints = new_waypoints

    def get_commands(self):
        return self._set_throttle, self._set_steer, self._set_brake

    def set_throttle(self, input_throttle):
        # Clamp the throttle command to valid bounds
        throttle           = np.fmax(np.fmin(input_throttle, 1.0), 0.0)
        self._set_throttle = throttle

    def set_steer(self, input_steer_in_rad):
        # Covnert radians to [-1, 1]
        input_steer = self._conv_rad_to_steer * input_steer_in_rad

        # Clamp the steering command to valid bounds
        steer           = np.fmax(np.fmin(input_steer, 1.0), -1.0)
        self._set_steer = steer

    def set_brake(self, input_brake):
        # Clamp the steering command to valid bounds
        brake           = np.fmax(np.fmin(input_brake, 1.0), 0.0)
        self._set_brake = brake

    def update_controls(self):
        ######################################################
        # RETRIEVE SIMULATOR FEEDBACK
        ######################################################
        x               = self._current_x
        y               = self._current_y
        yaw             = self._current_yaw
        v               = self._current_speed
        self.update_desired_speed()
        v_desired       = self._desired_speed
        t               = self._current_timestamp
        waypoints       = self._waypoints
        throttle_output = 0
        steer_output    = 0
        brake_output    = 0

        ######################################################
        ######################################################
        # MODULE 7: DECLARE USAGE VARIABLES HERE
        ######################################################
        ######################################################
        """
            Use 'self.vars.create_var(<variable name>, <default value>)'
            to create a persistent variable (not destroyed at each iteration).
            This means that the value can be stored for use in the next
            iteration of the control loop.

            Example: Creation of 'v_previous', default value to be 0
            self.vars.create_var('v_previous', 0.0)

            Example: Setting 'v_previous' to be 1.0
            self.vars.v_previous = 1.0

            Example: Accessing the value from 'v_previous' to be used
            throttle_output = 0.5 * self.vars.v_previous
        """
        kp = 5
        ki = 1.5
        kd = 0.5
        self.vars.create_var('v_previous', 0.0)
        self.vars.create_var('t_previous',0.0)
        self.vars.create_var('error_previous',0.0)
        self.vars.create_var('integral_previous',0.0)
        # self.vars.create_var("acc_previous",0.0)
        # self.vars.create_var("throttle_previous",0.0)
        # Skip the first frame to store previous values properly
        if self._start_control_loop:
            """
                Controller iteration code block.

                Controller Feedback Variables:
                    x               : Current X position (meters)
                    y               : Current Y position (meters)
                    yaw             : Current yaw pose (radians)
                    v               : Current forward speed (meters per second)
                    t               : Current time (seconds)
                    v_desired       : Current desired speed (meters per second)
                                      (Computed as the speed to track at the
                                      closest waypoint to the vehicle.)
                    waypoints       : Current waypoints to track
                                      (Includes speed to track at each x,y
                                      location.)
                                      Format: [[x0, y0, v0],
                                               [x1, y1, v1],
                                               ...
                                               [xn, yn, vn]]
                                      Example:
                                          waypoints[2][1]: 
                                          Returns the 3rd waypoint's y position

                                          waypoints[5]:
                                          Returns [x5, y5, v5] (6th waypoint)
                
                Controller Output Variables:
                    throttle_output : Throttle output (0 to 1)
                    steer_output    : Steer output (-1.22 rad to 1.22 rad)
                    brake_output    : Brake output (0 to 1)
            """

            ######################################################
            ######################################################
            # MODULE 7: IMPLEMENTATION OF LONGITUDINAL CONTROLLER HERE
            ######################################################
            ######################################################
            """
                Implement a longitudinal controller here. Remember that you can
                access the persistent variables declared above here. For
                example, can treat self.vars.v_previous like a "global variable".

            """
            
            time_period = t - self.vars.t_previous
            print("vehicle speed {}".format(v))
            error = v_desired - v

            integral = self.vars.integral_previous + error * time_period

            diff = (error - self.vars.error_previous)/time_period
            
            acc = kp * error + ki * integral + kd * diff


            # Change these outputs with the longitudinal controller. Note that
            # brake_output is optional and is not required to pass the
            # assignment, as the car will naturally slow down over time.
            if acc > 0:
                
                    throttle_output = min(1,acc) #1.0 / (1.0 + np.exp(-acc))
                    brake_output = 0
                    
            else:
                throttle_output = 0
                brake_output = max(1,-acc)
                
            if v > 5 * v_desired:
                brake_output = 1
                throttle_output = 0
           
            
            ######################################################
            ######################################################
            # MODULE 7: IMPLEMENTATION OF LATERAL CONTROLLER HERE
            ######################################################
            ######################################################
            """
                Implement a lateral controller here. Remember that you can
                access the persistent variables declared above here. For
                example, can treat self.vars.v_previous like a "global variable".
            """
            # Stanly Controller
            

            ### HEADING ERROR ###
            

            #path equation aX + bY + c = 0 => Y = -a/b*X -c
            #path slop (Yf - Yi)/(Xi - Xf)
            path_slop = (waypoints[-1][1]-waypoints[0][1])/ (waypoints[-1][0]-waypoints[0][0])#(waypoints[k][1] - waypoints[i][1])/ (waypoints[k][0]-waypoints[i][0])
            #heading of the path
            path_heading = np.arctan2(waypoints[-1][1]-waypoints[0][1], waypoints[-1][0]-waypoints[0][0]) #np.arctan2((waypoints[k][1] - waypoints[i][1]),(waypoints[k][0] - waypoints[i][0]))
            #vehicle heading
            vehicle_heading = yaw
            #(yaw angle) heading of the vehicle with respect to the path
            heading_error = path_heading - vehicle_heading
            #print("heading error {}".format(heading_error))
            #if the yaw angle is greater than pi then heading_yaw = 2*pi - heading_yaw
            if heading_error > np.pi:
                heading_error -= self._2pi
            elif heading_error < -np.pi:
                heading_error += self._2pi 

            print("heading error {}".format(heading_error))
                
            # #CROSSTRACK ERROR
            k_err = 0.6
            #solve for " a,b,c" for the path equation aX + bY + c = 0 
            # c = -slop * X - Y
            # c = (path_slop*waypoints[i][0]) - waypoints[i][1]
            # ck = (path_slop*waypoints[k][0]) - waypoints[k][1]
            # path_slop = - a/b
            # b = -1
            # a = path_slop
            
            c = -1

            b = -1 / (path_slop * waypoints[0][0] - waypoints[0][1])
            a = - path_slop * b
            # A = np.array([[waypoints[i][0],waypoints[i][1]],[waypoints[k][0],waypoints[k][1]]])
            # B = np.array([-c,-ck])
            # solution = np.linalg.solve(A, B)
           
            # a = solution[0]
            # b = solution[1]
            # cross track error
            crosstrack_error = (a*x + b*y + c)/(np.sqrt(a**2 + b**2))
            print("cross_error {}".format(crosstrack_error))
            print("steer_cross_track {}".format(np.arctan(k_err*crosstrack_error/v)))
            # Change the steer output with the lateral controller. 
            steer = heading_error +  np.arctan(k_err*crosstrack_error/v)
            #print("steer {}".format(steer))
            
            if steer > self._pi:
                steer -= self._2pi
            elif steer < -self._pi:
                steer += self._2pi

            if steer > 1.22:
                steer= 1.22
            elif steer < -1.22:
                steer = -1.22

            steer_output = steer

            ######################################################
            # SET CONTROLS OUTPUT
            ######################################################
            self.set_throttle(throttle_output)  # in percent (0 to 1)
            self.set_steer(steer_output)        # in rad (-1.22 to 1.22)
            self.set_brake(brake_output)        # in percent (0 to 1)

        ######################################################
        ######################################################
        # MODULE 7: STORE OLD VALUES HERE (ADD MORE IF NECESSARY)
        ######################################################
        ######################################################
        """
            Use this block to store old values (for example, we can store the
            current x, y, and yaw values here using persistent variables for use
            in the next iteration)
        """
        self.vars.v_previous = v  # Store forward speed to be used in next step
        self.vars.t_previous = t
        self.vars.error_previous = error
        self.vars.integral_previous = integral
       
        # self.vars.acc_previous = acc
        # self.vars.throttle_previous = throttle_output
