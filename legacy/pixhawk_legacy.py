from __future__ import print_function
from dronekit import connect, VehicleMode, LocationGlobal, LocationGlobalRelative
from pymavlink import mavutil # Needed for command message definitions
import dronekit_sitl
import time
import argparse 

def download_mission():
    missionList = []
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    for cmd in cmds:
        missionList.append(cmd)
    return missionList

def grab_waypoints():
    missionList = download_mission()
    latitudes = []
    longitudes = []
    for cmd in missionList:
        if ( (cmd.x > 10) & (cmd.x < 45) ):
            latitudes.append(cmd.x)
            longitudes.append(cmd.y)
    return latitudes, longitudes

def goto(latitudes, longitudes, altitudes, waypoint, guided2):
    if guided2 < 1:
        airspeed = 1
        targetLocation = LocationGlobalRelative(latitudes[waypoint], longitudes[waypoint], altitude)
        vehicle.simple_goto(targetLocation, airspeed)

def arm_and_takeoff(targetAltitude):
    """
    Arms vehicle and fly to a targetAltitude
    """

    print("Basic pre-arm checks")

    # Do not arm until autopilot is ready
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialize")
        time.sleep(1)
    
    print("Arming motors")

    # Arming the vehicle as GUIDED
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True

    # Confirming that the vehicle is armed
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)
    
    print("Taking off")\

    # Vehicle takes off to go to target altitude
    vehicle.simple_takeoff(targetAltitude)

    # Print altitude until target altitude is reached
    while True:
        print("Altitude: ", vehicle.location.global_relative_frame.alt)
        
        # If just below target altitude, break
        if vehicle.location.global_relative_frame.alt >= targetAltitude * 0.95:
            print("Reached target altitude")
            break
        
        # Wait before checking again
        time.sleep(1)


if __name__ == "__main__":

    # Getting the arguments for the arguments input
    parser = argparse.ArgumentParser(description='Print out vehicle state information. Connects to SITL on local PC by default.')
    
    # Will need to change when testing
    connection = '/dev/ttyTHS1'

    # Adding the arguments from pixhawk to the parser
    parser.add_argument(connection, 
                    help="vehicle connection target string. If not specified, SITL automatically started and used.")
    
    # Getting the arguments from the parser
    args = parser.parse_args()

    # Getting the connection to the pixhawk
    connection_string = args.connect

    # Creating the sitl
    sitl = None

    # Start SITL (simulator) if no connection
    if not connection_string:
        sitl = dronekit_sitl.start_default()
        connection_string = sitl.connection_string()

    # Creating a vehicle with connection to pixhawk, baud rate, and timeout
    vehicle = connect(connection_string,
                        wait_ready = True,
                        baud = 57600,
                        timeout = 60)

    # Get the latitudes and longitudes
    [latitudes, longitudes] = grab_waypoints()
    print("Waypoint latitudes: ", latitudes)
    print("Waypoint longitudes: ", longitudes)

    # Time to look at waypooints
    time.sleep(2)

    # Tell the pixhawk to stabilize
    vehicle.mode = VehicleMode("Stabilize")

    # Get the start time
    startTime = time.time()

    # Initialization
    z = 0
    waypoint = 0
    startingAltitude = 3.5
    zStop = 50 # Critical distance in cm below which to stop vehicle
    zSteer = 250 # Distance in cm below which to steer vehicle

    # Check that the pixhawk is receiving correct commands
    # Ctrl + C to disable
    while (time.time() - startTime < 45):
        try:		
            print(" Global Location (relative altitude): %s"%vehicle.location.global_relative_frame)    
            print(" Attitude: %s" % vehicle.attitude)
            print(" Velocity: %s" % vehicle.velocity)
            print(" GPS: %s" % vehicle.gps_0)
            print(" Last Heartbeat: %s" % vehicle.last_heartbeat)
            print(" Rangefinder: %s" % vehicle.rangefinder)
            print(" Rangefinder distance: %s" % vehicle.rangefinder.distance)
            print(" Heading: %s" % vehicle.heading)
            print(" Is Armable?: %s" % vehicle.is_armable)
            print(" Mode: %s" % vehicle.mode.name)    # settable
            print(" Armed: %s" % vehicle.armed)    # settable
            print(" Battery: %s" % vehicle.battery)
            time.sleep(1)
        except KeyboardInterrupt:
            pass
            break
    
    # Change pixhawk mode to GUIDED
    vehicle.mode = VehicleMode("GUIDED")

    # Wait to confirm that pixhawk is in GUIDED mode
    while not(vehicle.mode.name == "GUIDED"):
        print("Waiting for guided mode")
        time.sleep(1)

    # Initializing values for while loop
    z=0
    q=0
    v=0

    # Initializing the control values
    control=[0,0,0,0,0,0,0]

    # Get a new start time
    startTime = time.time()

    # Set time 0 to the start time
    T0=start

    delta_t = np.array([0.000, 0.000, 0.000])

    guided2 = 0
    waypoint = goto(latitudes,longitudes,altitude,waypoint,guided2)

    # While the vehicle is in GUIDED mode and less than 500 seconds have past since the start time was recorded
    while ( (vehicle.mode.name=="GUIDED") & (time.time() - startTime < 500) ): # value here
        try:
                    if z == 5:  #perform every 20th? iteration was at 7						
                        z = 0 #reset iterator
                        send_movement_command_YAW(yaw) #from AI drones
                        send_movement_command_XYA(speed,altitude)

                        while  (time.time() - T0 < 0.2):
                            pass
                        delta_t=np.roll(delta_t,-1)
                        delta_t[2]= time.time()-T0 #round( time.time()-T0 , 3)
                        T0=time.time()
                        if q==2:  #perform every other iteration of z loop
                            q=0
                            rangedist= vehicle.rangefinder.distance
                            if rangedist<1:
                                altitude=altitude+0.1
                            elif  ((rangedist>3) & (rangedist<4)):
                                altitude=altitude-0.1
                            print("Min Y: %0.0f  Min Y Raw: %0.0f "%(control[3],control[5]) )
                            print("Guided: ",control[2]," Yaw: ",control[1]," Speed: ",control[0])
                            if control[2] > 0:
                                waypoint=waypoint_check(latitudes,longitudes,altitude,waypoint,guided2)
                            print("Delta T:" ,delta_t)
                        else: q += 1
                    else:
                        z += 1 
        except KeyboardInterrupt:
            pass
            break
    


