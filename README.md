# Drone Control UI

A PyQt5-based graphical user interface for controlling multiple drones using DroneKit.

## 🚁 Available Versions

### 1. Full Version (`drone_ui.py`)
- Complete DroneKit integration
- Real drone control capabilities
- Your specific custom functions included

### 2. Mock Version (`drone_ui_mock.py`) ⭐
- **Currently Working** - No dependency issues
- Simulated drone connections for testing
- Full UI functionality with realistic mock data
- Perfect for development and UI testing

## ✨ Features

- **Multi-drone support**: Control up to 10 drones simultaneously
- **Basic controls**: ARM, DISARM, TAKEOFF, LAND, RTL for individual or all drones
- **Advanced controls**: NED position control and yaw-to-target functionality
- **Real-time status monitoring**: Monitor battery, GPS, altitude, and flight mode
- **Flexible connection**: Support for various connection types (TCP, UDP, serial)
- **Beautiful UI**: Color-coded buttons and status indicators

## 🛠 Installation

### Quick Start (Mock Version)
```bash
# Already installed system packages
python3 drone_ui_mock.py
```

### Full Installation
```bash
# Install dependencies
sudo apt install python3-pyqt5 python3-serial python3-pip
pip3 install dronekit pymavlink --break-system-packages

# Note: There may be compatibility issues with Python 3.13
# Use the mock version for development and testing
```

## 🎮 Usage

### Mock Version (Recommended for Testing)
```bash
python3 drone_ui_mock.py
```

### Real DroneKit Version
```bash
python3 drone_ui.py
```

The UI includes 4 main tabs:

### 1. **Connection Tab**
- Configure number of drones (1-10)
- Set connection strings for each drone
- Connect/disconnect all vehicles
- Real-time connection status

### 2. **Basic Control Tab**
- Individual vehicle control:
  - **ARM/DISARM** (Green/Red buttons)
  - **TAKEOFF** with altitude setting (Blue)
  - **LAND** (Yellow)
  - **RTL** (Gray)
- **All vehicles control** for simultaneous operations

### 3. **Advanced Control Tab**
- **NED Position Control**: Move drones using North-East-Down coordinates
- **Yaw Control**: Point drones toward specific GPS coordinates
- Uses your custom functions:
  - `send_ned_position()`
  - `yaw_to_target_with_position_control()`

### 4. **Status Tab**
- Real-time vehicle monitoring table
- Color-coded armed status (Green/Red)
- Battery voltage, GPS fix, satellite count
- Auto-refresh capability

## 📋 Connection Examples

### Mock Mode (Default)
```
mock://vehicle_1
mock://vehicle_2
mock://vehicle_3
```

### SITL (Software In The Loop)
```
tcp:127.0.0.1:14550
tcp:127.0.0.1:14551
tcp:127.0.0.1:14552
```

### Real Hardware
```
/dev/ttyUSB0
/dev/ttyACM0
udp:192.168.1.100:14550
```

## 🔧 Custom Functions Included

### `yaw_to_target_with_position_control(vehicle, target_location)`
Alternative method using SET_POSITION_TARGET_LOCAL_NED with yaw control.
Maintains current position while only changing yaw.

### `send_ned_position(vehicle, x, y, z)`
Move vehicle to a specified position in NED coordinates using SET_POSITION_TARGET_LOCAL_NED.

### `calculate_bearing(location1, location2)`
Calculate bearing between two GPS locations in radians.

## 🎨 UI Features

- **Modern Design**: Clean, intuitive interface with color-coded controls
- **Mock Mode Indicator**: Clear labeling when using simulated drones
- **Status Indicators**: Visual feedback for all operations
- **Responsive Layout**: Adapts to different window sizes
- **Real-time Updates**: Live status monitoring with auto-refresh

## ⚠️ Safety Notes

**Important Safety Reminders:**
- Always test with SITL or mock mode before using real hardware
- Ensure proper GPS lock before takeoff
- Have manual override capability ready
- Follow local aviation regulations
- Maintain visual line of sight when required

## 🔄 Current Status

### ✅ Working
- **Mock Version**: Fully functional UI with simulated drones
- **Qt5 Interface**: Beautiful, responsive user interface
- **All Controls**: ARM, TAKEOFF, LAND, RTL, NED positioning, yaw control
- **Status Monitoring**: Real-time updates with mock data

### ⚠️ Known Issues
- **DroneKit Compatibility**: Python 3.13 compatibility issues with `collections.MutableMapping`
- **Real Connections**: May require Python 3.8-3.11 for full DroneKit functionality

### 🚧 Workarounds
- Use **Mock Mode** for development and UI testing
- Switch to older Python version for real drone connections
- Mock mode provides realistic simulation for most use cases

## 🔧 Extending the UI

The application is designed to be easily extensible:

### Adding New Controls
1. Add buttons in `create_control_tab()` or `create_advanced_tab()`
2. Implement the handler function
3. Update the controller with new drone commands

### Adding Status Information
1. Modify `get_vehicle_status()` in the controller
2. Add columns to the status table
3. Update `update_status_display()`

### Custom Widgets
- Add new tabs with `self.tab_widget.addTab()`
- Create specialized control panels
- Integrate additional sensors or data

## 📁 File Structure

```
📦 Drone Control UI
├── 📄 drone_ui.py              # Main UI (DroneKit version)
├── 📄 drone_ui_mock.py         # Mock UI (Working version) ⭐
├── 📄 drone_controller.py      # Real DroneKit controller
├── 📄 drone_controller_mock.py # Mock controller
├── 📄 test_imports.py          # Import testing
├── 📄 test_qt_only.py         # Qt5 testing
├── 📄 run_drone_ui.py         # Launcher script
├── 📄 requirements.txt        # Dependencies
└── 📄 README.md               # This file
```

## 🐛 Troubleshooting

### Mock Version Issues
- **Qt5 not found**: Install with `sudo apt install python3-pyqt5`
- **Display issues**: Set `DISPLAY` environment variable if running remotely

### Real DroneKit Issues
- **Import errors**: Python version compatibility (try Python 3.8-3.11)
- **Connection failed**: Check connection strings and drone availability
- **Permission errors**: Check device permissions for serial connections

### General Issues
- **Window not showing**: Check if running in headless environment
- **Buttons not working**: Check console output for error messages
- **Status not updating**: Ensure auto-refresh is enabled

## 🎯 Next Steps

1. **Test the Mock Version**: Get familiar with the UI layout and controls
2. **Add Custom Functions**: Integrate your specific drone control algorithms
3. **Real Drone Testing**: Set up SITL or connect to real hardware
4. **Extend Features**: Add new controls or monitoring capabilities

---

**Ready to fly? Start with the mock version:**
```bash
python3 drone_ui_mock.py
```