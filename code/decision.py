import numpy as np

def is_steer_angle_out_of_range(angle):
    return (angle > 15 or angle < -15)

# This is where you can build a decision tree for determining throttle, brake and steer
# commands based on the output of the perception_step() function
def decision_step(rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if rover.nav_angles is not None:
        # Check for rover.mode status
        if rover.mode == 'forward':

            if rover.near_sample:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
                rover.mode = 'sample'

            elif len(rover.nav_angles) > 0:
                # Find the wall to navigate in parallel
                wall_dir_rad = np.min(rover.nav_angles) + np.deg2rad(40)
                wall_dir_deg = np.rad2deg(wall_dir_rad)
                wall_dir_clipped_deg = np.clip(wall_dir_deg, -15, 15)
                wall_dir_angles = np.logical_and(rover.nav_angles < wall_dir_rad + np.deg2rad(0.5),
                                                 rover.nav_angles > wall_dir_rad - np.deg2rad(0.5))
                wall_dir_dist = len(rover.nav_angles)

                # Check the extent of navigable terrain
                if wall_dir_dist > rover.stop_forward:
                    # If steer angle is bigger than what the rover can steer
                    # and speed is too high slow down to avoid too big roll angles
                    if is_steer_angle_out_of_range(wall_dir_deg) and (rover.vel > 0.5*rover.max_vel):
                        rover.throttle = 0
                        rover.brake = rover.brake_slow_set
                    # if angle is ok and velocity is normal, then throttle
                    elif rover.vel >= rover.max_vel:
                        rover.throttle = 0
                        rover.brake = 0
                        rover.steer = wall_dir_clipped_deg
                    else:
                        # Set throttle value to throttle setting
                        rover.throttle = rover.throttle_set
                        rover.brake = 0
                        rover.steer = wall_dir_clipped_deg
                        if rover.vel > 0.2:
                            # To distinguish between being stuck and starting to move
                            rover.started = True
                else:
                    # Set mode to "stop" and hit the brakes!
                    rover.throttle = 0
                    # Set brake to stored brake value
                    rover.brake = rover.brake_fast_set
                    rover.steer = 0
                    rover.mode = 'stop'

                if rover.started and rover.vel == 0 and rover.throttle > 0:
                    # Set mode to "stop" and hit the brakes!
                    rover.throttle = 0
                    # Set brake to stored brake value
                    rover.brake = rover.brake_fast_set
                    rover.steer = 0
                    rover.started = False
                    rover.mode = 'unstuck'

            else:
                # Set mode to "stop" and hit the brakes!
                rover.throttle = 0
                # Set brake to stored brake value
                rover.brake = rover.brake_fast_set
                rover.steer = 0
                rover.mode = 'stop'

        elif rover.mode == 'stop':

            if rover.near_sample:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
                rover.mode = 'sample'

            # If we're in stop mode but still moving keep braking
            elif rover.vel > 0.2:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
            # If we're not moving
            else:
                if len(rover.nav_angles) < rover.go_forward:
                    rover.throttle = 0
                    # Release the brake to allow turning
                    rover.brake = 0
                    # When stopped the next line will induce 4-wheel turning
                    rover.steer = 15 # Could be more clever here about which way to turn
                elif len(rover.nav_angles) > 0:
                    # Find the wall to navigate in parallel
                    wall_dir_rad = np.min(rover.nav_angles) + np.deg2rad(60)
                    wall_dir_deg = np.rad2deg(wall_dir_rad)
                    wall_dir_clipped_deg = np.clip(wall_dir_deg, -15, 15)

                    if is_steer_angle_out_of_range(wall_dir_clipped_deg):
                        rover.throttle = 0
                        rover.brake = 0
                        rover.steer = 15
                    # If we're stopped but see sufficient navigable terrain in front then go!
                    else:
                        # Set throttle back to stored value
                        rover.throttle = rover.throttle_set
                        # Release the brake
                        rover.brake = 0
                        # Set steer to mean angle
                        rover.steer = wall_dir_clipped_deg
                        rover.mode = 'forward'

        elif rover.mode == 'unstuck':
            rover.steer = -15
            # Reverse
            rover.throttle = -1*rover.throttle_set
            rover.brake = 0

            if rover.vel < -0.4:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
                rover.mode = 'forward'

        elif rover.mode == 'sample':
            # If we're in stop mode but still moving keep braking
            if rover.vel > 0.2:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
            elif rover.near_sample and not rover.picking_up:
                rover.send_pickup = True
            else:
                rover.throttle = 0
                rover.brake = 0
                rover.steer = 0
                rover.mode = 'forward'

    return rover
