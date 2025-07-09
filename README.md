# Drone Control UI

A PyQt5-based graphical user interface for controlling multiple drones using DroneKit.

## Features

- **Multi-drone support**: Control up to 10 drones simultaneously
- **Basic controls**: ARM, DISARM, TAKEOFF, LAND, RTL for individual or all drones
- **Advanced controls**: NED position control and yaw-to-target functionality
- **Real-time status monitoring**: Monitor battery, GPS, altitude, and flight mode
- **Flexible connection**: Support for various connection types (TCP, UDP, serial)

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
python drone_ui.py
```

## Usage

### 1. Connection Setup
- Navigate to the "Connection" tab
- Set the number of UAVs you want to control
- Configure connection strings for each drone (default: tcp:127.0.0.1:14550, 14551, etc.)
- Click "Connect All" to establish connections

### 2. Basic Control
- Use the "Basic Control" tab for standard operations
- Select a specific vehicle or use "ALL" buttons for simultaneous control
- ARM → TAKEOFF → Control → LAND/RTL workflow

### 3. Advanced Control
- Use the "Advanced Control" tab for precise positioning
- **NED Position Control**: Move drones using North-East-Down coordinates
- **Yaw Control**: Point drones toward specific GPS coordinates

### 4. Status Monitoring
- Check the "Status" tab for real-time vehicle information
- Enable auto-refresh for continuous updates
- Monitor battery levels, GPS fix, satellite count, and flight modes

## Connection Examples

### SITL (Software In The Loop)
```
tcp:127.0.0.1:14550
tcp:127.0.0.1:14551
```

### Real Hardware
```
/dev/ttyUSB0
/dev/ttyACM0
udp:192.168.1.100:14550
```

## Functions Included

- `yaw_to_target_with_position_control()`: Yaw drone to face a target location
- `send_ned_position()`: Move drone to specific NED coordinates
- `calculate_bearing()`: Calculate bearing between two GPS points

## Safety Notes

⚠️ **Important Safety Reminders:**
- Always test with SITL before using real hardware
- Ensure proper GPS lock before takeoff
- Have manual override capability ready
- Follow local aviation regulations
- Maintain visual line of sight when required

## Extending the UI

The application is designed to be easily extensible. You can:
- Add new tabs for additional functionality
- Extend the `DroneController` class with new commands
- Modify the status monitoring to include additional parameters
- Add new control widgets to existing tabs

## Troubleshooting

### Connection Issues
- Verify connection strings are correct
- Check if the autopilot is running and accessible
- Ensure no other ground control stations are connected
- Check firewall settings for TCP connections

### Control Issues
- Ensure drones are armed before attempting takeoff
- Verify GPS lock is established
- Check flight mode compatibility
- Monitor battery levels