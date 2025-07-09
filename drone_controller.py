import math
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil


def calculate_bearing(location1, location2):
    """
    Calculate bearing between two locations in radians.
    """
    lat1 = math.radians(location1.lat)
    lat2 = math.radians(location2.lat)
    
    diff_long = math.radians(location2.lon - location1.lon)
    
    x = math.sin(diff_long) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_long))
    
    initial_bearing = math.atan2(x, y)
    
    # Convert from compass bearing to standard math bearing
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return math.radians(compass_bearing)


def yaw_to_target_with_position_control(vehicle, target_location):
    """
    Alternative method using SET_POSITION_TARGET_LOCAL_NED with yaw control.
    This maintains current position while only changing yaw.
    """
    vehicle_location = vehicle.location.global_relative_frame

    target_bearing = calculate_bearing(vehicle_location, target_location)
    
    # Send position target message with yaw control
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0, # time_boot_ms (not used)
        0, 0, # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED, # frame
        0b100111111000, # type_mask (only yaw enabled, position and velocity ignored)
        0, 0, 0, # x, y, z positions (ignored due to type_mask)
        0, 0, 0, # x, y, z velocity (ignored due to type_mask)
        0, 0, 0, # x, y, z acceleration (ignored)
        target_bearing+math.pi, 0) # yaw (radians), yaw_rate (rad/s)
    
    vehicle.send_mavlink(msg)
    
    return target_bearing


def send_ned_position(vehicle, x, y, z):
    """
    Move vehicle to a specified position in NED coordinates.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_OFFSET_NED, # frame
        0b110111111000, # type_mask (only positions enabled)
        x, y, z, # x, y, z positions in m
        0, 0, 0, # x, y, z velocity (not used)
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)
    
    vehicle.send_mavlink(msg)


class DroneController:
    def __init__(self):
        self.vehicles = []
        self.connection_strings = []
        
    def add_vehicle(self, connection_string):
        """Add a vehicle connection string to the list"""
        self.connection_strings.append(connection_string)
        
    def connect_vehicles(self):
        """Connect to all vehicles in the connection list"""
        self.vehicles = []
        for i, conn_str in enumerate(self.connection_strings):
            try:
                vehicle = connect(conn_str, wait_ready=True, timeout=60)
                self.vehicles.append(vehicle)
                print(f"Vehicle {i+1} connected successfully")
            except Exception as e:
                print(f"Failed to connect to vehicle {i+1}: {str(e)}")
                self.vehicles.append(None)
        return len([v for v in self.vehicles if v is not None])
    
    def disconnect_vehicles(self):
        """Disconnect all vehicles"""
        for vehicle in self.vehicles:
            if vehicle:
                vehicle.close()
        self.vehicles = []
        
    def arm_vehicle(self, vehicle_index):
        """Arm a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            vehicle.mode = VehicleMode("GUIDED")
            vehicle.armed = True
            
            # Wait until armed
            timeout = 10
            start_time = time.time()
            while not vehicle.armed and (time.time() - start_time) < timeout:
                time.sleep(1)
            
            return vehicle.armed
        return False
    
    def takeoff_vehicle(self, vehicle_index, altitude):
        """Takeoff a specific vehicle to specified altitude"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            if vehicle.armed:
                vehicle.simple_takeoff(altitude)
                return True
        return False
    
    def land_vehicle(self, vehicle_index):
        """Land a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            vehicle.mode = VehicleMode("LAND")
            return True
        return False
    
    def rtl_vehicle(self, vehicle_index):
        """Return to launch for a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            vehicle.mode = VehicleMode("RTL")
            return True
        return False
    
    def get_vehicle_status(self, vehicle_index):
        """Get status information for a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            return {
                'armed': vehicle.armed,
                'mode': str(vehicle.mode),
                'altitude': vehicle.location.global_relative_frame.alt if vehicle.location.global_relative_frame else 0,
                'battery': vehicle.battery.voltage if vehicle.battery else 0,
                'gps_fix': vehicle.gps_0.fix_type if vehicle.gps_0 else 0,
                'satellites': vehicle.gps_0.satellites_visible if vehicle.gps_0 else 0
            }
        return None
    
    def send_ned_to_vehicle(self, vehicle_index, x, y, z):
        """Send NED position command to specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            send_ned_position(self.vehicles[vehicle_index], x, y, z)
            return True
        return False
    
    def yaw_to_target(self, vehicle_index, target_lat, target_lon):
        """Yaw vehicle to target location"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            target_location = LocationGlobalRelative(target_lat, target_lon, 0)
            bearing = yaw_to_target_with_position_control(self.vehicles[vehicle_index], target_location)
            return math.degrees(bearing)
        return None