import math
import time
import random


def calculate_bearing(location1, location2):
    """
    Calculate bearing between two locations in radians.
    """
    try:
        lat1 = math.radians(location1['lat'])
        lat2 = math.radians(location2['lat'])
        
        diff_long = math.radians(location2['lon'] - location1['lon'])
        
        x = math.sin(diff_long) * math.cos(lat2)
        y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diff_long))
        
        initial_bearing = math.atan2(x, y)
        
        # Convert from compass bearing to standard math bearing
        initial_bearing = math.degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        
        return math.radians(compass_bearing)
    except:
        return 0.0


class MockVehicle:
    """Mock vehicle for testing without real dronekit connection"""
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        self.armed = False
        self.mode = "STABILIZE"
        self.altitude = 0.0
        self.battery_voltage = 12.6
        self.gps_fix = 3
        self.satellites = 8
        self.location = {
            'lat': 37.7749 + (vehicle_id * 0.001),  # San Francisco + offset
            'lon': -122.4194 + (vehicle_id * 0.001),
            'alt': 0.0
        }
        
    def simple_takeoff(self, altitude):
        """Mock takeoff"""
        if self.armed:
            self.altitude = altitude
            self.location['alt'] = altitude
            self.mode = "GUIDED"
            return True
        return False
        
    def close(self):
        """Mock close connection"""
        pass


class DroneController:
    def __init__(self, use_mock=True):
        self.vehicles = []
        self.connection_strings = []
        self.use_mock = use_mock
        
    def add_vehicle(self, connection_string):
        """Add a vehicle connection string to the list"""
        self.connection_strings.append(connection_string)
        
    def connect_vehicles(self):
        """Connect to all vehicles in the connection list"""
        self.vehicles = []
        connected_count = 0
        
        for i, conn_str in enumerate(self.connection_strings):
            try:
                if self.use_mock:
                    # Create mock vehicle
                    vehicle = MockVehicle(i)
                    self.vehicles.append(vehicle)
                    print(f"Mock Vehicle {i+1} connected successfully")
                    connected_count += 1
                else:
                    # Try real dronekit connection
                    try:
                        from dronekit import connect
                        vehicle = connect(conn_str, wait_ready=True, timeout=60)
                        self.vehicles.append(vehicle)
                        print(f"Vehicle {i+1} connected successfully")
                        connected_count += 1
                    except ImportError:
                        print(f"DroneKit not available - using mock for Vehicle {i+1}")
                        vehicle = MockVehicle(i)
                        self.vehicles.append(vehicle)
                        connected_count += 1
                    except Exception as e:
                        print(f"Failed to connect to vehicle {i+1}: {str(e)}")
                        self.vehicles.append(None)
                        
            except Exception as e:
                print(f"Failed to connect to vehicle {i+1}: {str(e)}")
                self.vehicles.append(None)
                
        return connected_count
    
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
            if self.use_mock or isinstance(vehicle, MockVehicle):
                vehicle.mode = "GUIDED"
                vehicle.armed = True
                return True
            else:
                # Real dronekit logic
                vehicle.mode = "GUIDED"
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
                return vehicle.simple_takeoff(altitude)
        return False
    
    def land_vehicle(self, vehicle_index):
        """Land a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            if self.use_mock or isinstance(vehicle, MockVehicle):
                vehicle.mode = "LAND"
                vehicle.altitude = 0.0
                vehicle.location['alt'] = 0.0
                return True
            else:
                vehicle.mode = "LAND"
                return True
        return False
    
    def rtl_vehicle(self, vehicle_index):
        """Return to launch for a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            vehicle.mode = "RTL"
            return True
        return False
    
    def get_vehicle_status(self, vehicle_index):
        """Get status information for a specific vehicle"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            
            if self.use_mock or isinstance(vehicle, MockVehicle):
                # Add some random variation to make it look realistic
                return {
                    'armed': vehicle.armed,
                    'mode': vehicle.mode,
                    'altitude': vehicle.altitude + random.uniform(-0.1, 0.1),
                    'battery': vehicle.battery_voltage + random.uniform(-0.1, 0.1),
                    'gps_fix': vehicle.gps_fix,
                    'satellites': vehicle.satellites + random.randint(-1, 1)
                }
            else:
                # Real dronekit logic
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
            vehicle = self.vehicles[vehicle_index]
            
            if self.use_mock or isinstance(vehicle, MockVehicle):
                # Mock NED positioning
                print(f"Mock: Moving vehicle {vehicle_index+1} to NED position ({x}, {y}, {z})")
                return True
            else:
                # Real dronekit logic would go here
                # send_ned_position(vehicle, x, y, z)
                return True
        return False
    
    def yaw_to_target(self, vehicle_index, target_lat, target_lon):
        """Yaw vehicle to target location"""
        if vehicle_index < len(self.vehicles) and self.vehicles[vehicle_index]:
            vehicle = self.vehicles[vehicle_index]
            
            if self.use_mock or isinstance(vehicle, MockVehicle):
                target_location = {'lat': target_lat, 'lon': target_lon}
                bearing = calculate_bearing(vehicle.location, target_location)
                bearing_degrees = math.degrees(bearing)
                print(f"Mock: Yawing vehicle {vehicle_index+1} to bearing {bearing_degrees:.1f}°")
                return bearing_degrees
            else:
                # Real dronekit logic would go here
                target_location = {'lat': target_lat, 'lon': target_lon}
                bearing = calculate_bearing(vehicle.location, target_location)
                return math.degrees(bearing)
        return None