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

            # Check the extent of navigable terrain
            if len(rover.nav_angles) >= rover.stop_forward:
                steer_angle = np.mean(rover.nav_angles * 180/np.pi)

                if rover.vel >= rover.max_vel:
                    rover.throttle = 0
                else:
                    # If steer angle is bigger than what the rover can steer
                    # and speed is too high slow down to avoid too big roll angles
                    if is_steer_angle_out_of_range(steer_angle) and (rover.vel > 0.8*rover.max_vel):
                        rover.throttle = 0
                    # if angle is ok and velocity is normal, then throttle
                    else:
                        # Set throttle value to throttle setting
                        rover.throttle = rover.throttle_set

                # Set steering to average angle clipped to the rover's capabilities
                rover.steer = np.clip(steer_angle, -15, 15)
                rover.brake = 0

            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(rover.nav_angles) < rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    rover.throttle = 0
                    # Set brake to stored brake value
                    rover.brake = rover.brake_fast_set
                    rover.steer = 0
                    rover.mode = 'stop'

        # If we're already in "stop" mode then make different decisions
        elif rover.mode == 'stop':
            # If we're in stop mode but still moving keep braking
            if rover.vel > 0.2:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif rover.vel <= 0.2:
                steer_angle = np.mean(rover.nav_angles * 180/np.pi)
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(rover.nav_angles) < rover.go_forward or is_steer_angle_out_of_range(steer_angle):
                    rover.throttle = 0
                    # Release the brake to allow turning
                    rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    rover.steer = -15 # Could be more clever here about which way to turn
                # If we're stopped but see sufficient navigable terrain in front then go!
                else:
                    # Set throttle back to stored value
                    rover.throttle = rover.throttle_set
                    # Release the brake
                    rover.brake = 0
                    # Set steer to mean angle
                    rover.steer = np.clip(steer_angle, -15, 15)
                    rover.mode = 'forward'

        elif rover.mode == 'sample':
            if rover.vel > 0.2:
                rover.throttle = 0
                rover.brake = rover.brake_fast_set
                rover.steer = 0
            else:
                # If in a state where want to pickup a rock send pickup command
                if rover.near_sample and not rover.picking_up:
                    rover.send_pickup = True
                    rover.mode = 'forward'

    return rover
