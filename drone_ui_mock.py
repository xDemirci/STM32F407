import sys
import threading
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                           QWidget, QPushButton, QLabel, QSpinBox, QLineEdit, 
                           QTextEdit, QTabWidget, QGridLayout, QGroupBox, 
                           QComboBox, QDoubleSpinBox, QMessageBox, QTableWidget,
                           QTableWidgetItem, QHeaderView, QCheckBox)
from PyQt5.QtCore import QTimer, pyqtSignal, QObject, QThread
from PyQt5.QtGui import QFont
from drone_controller_mock import DroneController


class StatusUpdateWorker(QObject):
    """Worker thread for updating drone status"""
    status_update = pyqtSignal(int, dict)
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = False
        
    def start_updates(self):
        self.running = True
        while self.running:
            for i in range(len(self.controller.vehicles)):
                if self.controller.vehicles[i]:
                    status = self.controller.get_vehicle_status(i)
                    if status:
                        self.status_update.emit(i, status)
            time.sleep(1)  # Update every second
            
    def stop_updates(self):
        self.running = False


class DroneControlUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.controller = DroneController(use_mock=True)
        self.status_worker = None
        self.status_thread = None
        
        self.setWindowTitle("Drone Control Interface (Mock Mode)")
        self.setGeometry(100, 100, 1200, 800)
        
        self.init_ui()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(self.tab_widget)
        
        # Initialize connection fields list
        self.connection_fields = []
        
        # Create tabs
        self.create_connection_tab()
        self.create_control_tab()
        self.create_advanced_tab()
        self.create_status_tab()
        
        # Now update connection fields after all tabs are created
        self.update_connection_fields()
        
    def create_connection_tab(self):
        """Create the connection management tab"""
        connection_widget = QWidget()
        layout = QVBoxLayout(connection_widget)
        
        # Mock mode indicator
        mock_label = QLabel("🔧 MOCK MODE: Using simulated drones for testing")
        mock_label.setStyleSheet("QLabel { background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 5px; }")
        layout.addWidget(mock_label)
        
        # Number of UAVs section
        uav_group = QGroupBox("UAV Configuration")
        uav_layout = QHBoxLayout(uav_group)
        
        uav_layout.addWidget(QLabel("Number of UAVs:"))
        self.uav_count_spinbox = QSpinBox()
        self.uav_count_spinbox.setMinimum(1)
        self.uav_count_spinbox.setMaximum(10)
        self.uav_count_spinbox.setValue(3)  # Default to 3 for demo
        self.uav_count_spinbox.valueChanged.connect(self.update_connection_fields)
        uav_layout.addWidget(self.uav_count_spinbox)
        
        generate_btn = QPushButton("Generate Connection Fields")
        generate_btn.clicked.connect(self.update_connection_fields)
        uav_layout.addWidget(generate_btn)
        
        layout.addWidget(uav_group)
        
        # Connection strings section
        self.connection_group = QGroupBox("Connection Strings")
        self.connection_layout = QVBoxLayout(self.connection_group)
        layout.addWidget(self.connection_group)
        
        # Connection controls
        control_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect All")
        self.connect_btn.clicked.connect(self.connect_vehicles)
        control_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Disconnect All")
        self.disconnect_btn.clicked.connect(self.disconnect_vehicles)
        self.disconnect_btn.setEnabled(False)
        control_layout.addWidget(self.disconnect_btn)
        
        layout.addLayout(control_layout)
        
        # Status display
        self.connection_status = QTextEdit()
        self.connection_status.setMaximumHeight(150)
        self.connection_status.setReadOnly(True)
        layout.addWidget(QLabel("Connection Status:"))
        layout.addWidget(self.connection_status)
        
        self.tab_widget.addTab(connection_widget, "Connection")
        
    def create_control_tab(self):
        """Create the basic control tab"""
        control_widget = QWidget()
        layout = QVBoxLayout(control_widget)
        
        # Vehicle selection
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Vehicle:"))
        self.vehicle_selector = QComboBox()
        self.vehicle_selector.addItem("Vehicle 1")
        selection_layout.addWidget(self.vehicle_selector)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # Basic controls
        basic_group = QGroupBox("Basic Controls")
        basic_layout = QGridLayout(basic_group)
        
        self.arm_btn = QPushButton("ARM")
        self.arm_btn.clicked.connect(self.arm_vehicle)
        self.arm_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; padding: 8px; }")
        basic_layout.addWidget(self.arm_btn, 0, 0)
        
        self.disarm_btn = QPushButton("DISARM")
        self.disarm_btn.clicked.connect(self.disarm_vehicle)
        self.disarm_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; padding: 8px; }")
        basic_layout.addWidget(self.disarm_btn, 0, 1)
        
        # Takeoff controls
        takeoff_layout = QHBoxLayout()
        takeoff_layout.addWidget(QLabel("Altitude (m):"))
        self.takeoff_altitude = QDoubleSpinBox()
        self.takeoff_altitude.setMinimum(1.0)
        self.takeoff_altitude.setMaximum(100.0)
        self.takeoff_altitude.setValue(10.0)
        takeoff_layout.addWidget(self.takeoff_altitude)
        
        self.takeoff_btn = QPushButton("TAKEOFF")
        self.takeoff_btn.clicked.connect(self.takeoff_vehicle)
        self.takeoff_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; padding: 8px; }")
        takeoff_layout.addWidget(self.takeoff_btn)
        
        basic_layout.addLayout(takeoff_layout, 1, 0, 1, 2)
        
        self.land_btn = QPushButton("LAND")
        self.land_btn.clicked.connect(self.land_vehicle)
        self.land_btn.setStyleSheet("QPushButton { background-color: #ffc107; color: black; padding: 8px; }")
        basic_layout.addWidget(self.land_btn, 2, 0)
        
        self.rtl_btn = QPushButton("RTL")
        self.rtl_btn.clicked.connect(self.rtl_vehicle)
        self.rtl_btn.setStyleSheet("QPushButton { background-color: #6c757d; color: white; padding: 8px; }")
        basic_layout.addWidget(self.rtl_btn, 2, 1)
        
        layout.addWidget(basic_group)
        
        # All vehicles controls
        all_group = QGroupBox("All Vehicles Controls")
        all_layout = QGridLayout(all_group)
        
        self.arm_all_btn = QPushButton("ARM ALL")
        self.arm_all_btn.clicked.connect(self.arm_all_vehicles)
        self.arm_all_btn.setStyleSheet("QPushButton { background-color: #28a745; color: white; padding: 10px; font-weight: bold; }")
        all_layout.addWidget(self.arm_all_btn, 0, 0)
        
        self.takeoff_all_btn = QPushButton("TAKEOFF ALL")
        self.takeoff_all_btn.clicked.connect(self.takeoff_all_vehicles)
        self.takeoff_all_btn.setStyleSheet("QPushButton { background-color: #007bff; color: white; padding: 10px; font-weight: bold; }")
        all_layout.addWidget(self.takeoff_all_btn, 0, 1)
        
        self.land_all_btn = QPushButton("LAND ALL")
        self.land_all_btn.clicked.connect(self.land_all_vehicles)
        self.land_all_btn.setStyleSheet("QPushButton { background-color: #ffc107; color: black; padding: 10px; font-weight: bold; }")
        all_layout.addWidget(self.land_all_btn, 1, 0)
        
        self.rtl_all_btn = QPushButton("RTL ALL")
        self.rtl_all_btn.clicked.connect(self.rtl_all_vehicles)
        self.rtl_all_btn.setStyleSheet("QPushButton { background-color: #6c757d; color: white; padding: 10px; font-weight: bold; }")
        all_layout.addWidget(self.rtl_all_btn, 1, 1)
        
        layout.addWidget(all_group)
        layout.addStretch()
        
        self.tab_widget.addTab(control_widget, "Basic Control")
        
    def create_advanced_tab(self):
        """Create the advanced control tab"""
        advanced_widget = QWidget()
        layout = QVBoxLayout(advanced_widget)
        
        # Vehicle selection for advanced
        selection_layout = QHBoxLayout()
        selection_layout.addWidget(QLabel("Select Vehicle:"))
        self.advanced_vehicle_selector = QComboBox()
        self.advanced_vehicle_selector.addItem("Vehicle 1")
        selection_layout.addWidget(self.advanced_vehicle_selector)
        selection_layout.addStretch()
        layout.addLayout(selection_layout)
        
        # NED Position Control
        ned_group = QGroupBox("NED Position Control")
        ned_layout = QGridLayout(ned_group)
        
        ned_layout.addWidget(QLabel("X (North):"), 0, 0)
        self.ned_x = QDoubleSpinBox()
        self.ned_x.setRange(-1000, 1000)
        self.ned_x.setSuffix(" m")
        ned_layout.addWidget(self.ned_x, 0, 1)
        
        ned_layout.addWidget(QLabel("Y (East):"), 1, 0)
        self.ned_y = QDoubleSpinBox()
        self.ned_y.setRange(-1000, 1000)
        self.ned_y.setSuffix(" m")
        ned_layout.addWidget(self.ned_y, 1, 1)
        
        ned_layout.addWidget(QLabel("Z (Down):"), 2, 0)
        self.ned_z = QDoubleSpinBox()
        self.ned_z.setRange(-100, 100)
        self.ned_z.setSuffix(" m")
        ned_layout.addWidget(self.ned_z, 2, 1)
        
        self.send_ned_btn = QPushButton("Send NED Position")
        self.send_ned_btn.clicked.connect(self.send_ned_position)
        self.send_ned_btn.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; padding: 8px; }")
        ned_layout.addWidget(self.send_ned_btn, 3, 0, 1, 2)
        
        layout.addWidget(ned_group)
        
        # Yaw Control
        yaw_group = QGroupBox("Yaw Control")
        yaw_layout = QGridLayout(yaw_group)
        
        yaw_layout.addWidget(QLabel("Target Latitude:"), 0, 0)
        self.target_lat = QDoubleSpinBox()
        self.target_lat.setRange(-90, 90)
        self.target_lat.setDecimals(6)
        self.target_lat.setValue(37.7749)  # San Francisco
        yaw_layout.addWidget(self.target_lat, 0, 1)
        
        yaw_layout.addWidget(QLabel("Target Longitude:"), 1, 0)
        self.target_lon = QDoubleSpinBox()
        self.target_lon.setRange(-180, 180)
        self.target_lon.setDecimals(6)
        self.target_lon.setValue(-122.4194)  # San Francisco
        yaw_layout.addWidget(self.target_lon, 1, 1)
        
        self.yaw_to_target_btn = QPushButton("Yaw to Target")
        self.yaw_to_target_btn.clicked.connect(self.yaw_to_target)
        self.yaw_to_target_btn.setStyleSheet("QPushButton { background-color: #6f42c1; color: white; padding: 8px; }")
        yaw_layout.addWidget(self.yaw_to_target_btn, 2, 0, 1, 2)
        
        layout.addWidget(yaw_group)
        layout.addStretch()
        
        self.tab_widget.addTab(advanced_widget, "Advanced Control")
        
    def create_status_tab(self):
        """Create the status monitoring tab"""
        status_widget = QWidget()
        layout = QVBoxLayout(status_widget)
        
        # Status table
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(7)
        self.status_table.setHorizontalHeaderLabels([
            "Vehicle", "Armed", "Mode", "Altitude (m)", "Battery (V)", "GPS Fix", "Satellites"
        ])
        self.status_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(QLabel("Vehicle Status:"))
        layout.addWidget(self.status_table)
        
        # Auto-refresh controls
        refresh_layout = QHBoxLayout()
        self.auto_refresh_btn = QPushButton("Start Auto Refresh")
        self.auto_refresh_btn.clicked.connect(self.toggle_auto_refresh)
        self.auto_refresh_btn.setStyleSheet("QPushButton { background-color: #20c997; color: white; padding: 8px; }")
        refresh_layout.addWidget(self.auto_refresh_btn)
        
        self.manual_refresh_btn = QPushButton("Manual Refresh")
        self.manual_refresh_btn.clicked.connect(self.update_status_display)
        refresh_layout.addWidget(self.manual_refresh_btn)
        
        refresh_layout.addStretch()
        layout.addLayout(refresh_layout)
        
        self.tab_widget.addTab(status_widget, "Status")
        
    def update_connection_fields(self):
        """Update connection string input fields based on UAV count"""
        # Clear existing fields and layouts
        while self.connection_layout.count():
            child = self.connection_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
        
        self.connection_fields.clear()
        
        # Create new fields
        count = self.uav_count_spinbox.value()
        for i in range(count):
            field_layout = QHBoxLayout()
            field_layout.addWidget(QLabel(f"UAV {i+1}:"))
            
            line_edit = QLineEdit()
            line_edit.setPlaceholderText(f"Mock connection {i+1}")
            line_edit.setText(f"mock://vehicle_{i+1}")  # Mock connection string
            field_layout.addWidget(line_edit)
            
            self.connection_fields.append(line_edit)
            self.connection_layout.addLayout(field_layout)
        
        # Update vehicle selectors
        self.update_vehicle_selectors()
        
    def clear_layout(self, layout):
        """Helper method to clear a layout completely"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
        
    def update_vehicle_selectors(self):
        """Update vehicle selector comboboxes"""
        count = self.uav_count_spinbox.value()
        
        # Update basic control selector (if it exists)
        if hasattr(self, 'vehicle_selector'):
            self.vehicle_selector.clear()
            for i in range(count):
                self.vehicle_selector.addItem(f"Vehicle {i+1}")
            
        # Update advanced control selector (if it exists)
        if hasattr(self, 'advanced_vehicle_selector'):
            self.advanced_vehicle_selector.clear()
            for i in range(count):
                self.advanced_vehicle_selector.addItem(f"Vehicle {i+1}")
            
        # Update status table (if it exists)
        if hasattr(self, 'status_table'):
            self.status_table.setRowCount(count)
            for i in range(count):
                self.status_table.setItem(i, 0, QTableWidgetItem(f"Vehicle {i+1}"))
        
    def connect_vehicles(self):
        """Connect to all vehicles"""
        self.controller.connection_strings.clear()
        
        for field in self.connection_fields:
            conn_str = field.text().strip()
            if conn_str:
                self.controller.add_vehicle(conn_str)
        
        if not self.controller.connection_strings:
            QMessageBox.warning(self, "Warning", "No connection strings provided!")
            return
            
        self.connection_status.append("Connecting to mock vehicles...")
        
        # Connect in a separate thread to avoid freezing UI
        def connect_thread():
            connected_count = self.controller.connect_vehicles()
            self.connection_status.append(f"Connected to {connected_count} mock vehicles successfully.")
            
            if connected_count > 0:
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_vehicles(self):
        """Disconnect all vehicles"""
        self.controller.disconnect_vehicles()
        self.connection_status.append("All vehicles disconnected.")
        
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        
        # Stop status updates
        if self.status_timer.isActive():
            self.toggle_auto_refresh()
        
    def get_selected_vehicle_index(self, selector=None):
        """Get the index of the selected vehicle"""
        if selector is None:
            selector = self.vehicle_selector
        return selector.currentIndex()
        
    def arm_vehicle(self):
        """Arm the selected vehicle"""
        index = self.get_selected_vehicle_index()
        if self.controller.arm_vehicle(index):
            self.connection_status.append(f"Vehicle {index+1} armed successfully.")
        else:
            self.connection_status.append(f"Failed to arm Vehicle {index+1}.")
            
    def disarm_vehicle(self):
        """Disarm the selected vehicle"""
        index = self.get_selected_vehicle_index()
        if index < len(self.controller.vehicles) and self.controller.vehicles[index]:
            self.controller.vehicles[index].armed = False
            self.connection_status.append(f"Vehicle {index+1} disarmed.")
            
    def takeoff_vehicle(self):
        """Takeoff the selected vehicle"""
        index = self.get_selected_vehicle_index()
        altitude = self.takeoff_altitude.value()
        if self.controller.takeoff_vehicle(index, altitude):
            self.connection_status.append(f"Vehicle {index+1} taking off to {altitude}m.")
        else:
            self.connection_status.append(f"Failed to takeoff Vehicle {index+1}.")
            
    def land_vehicle(self):
        """Land the selected vehicle"""
        index = self.get_selected_vehicle_index()
        if self.controller.land_vehicle(index):
            self.connection_status.append(f"Vehicle {index+1} landing.")
        else:
            self.connection_status.append(f"Failed to land Vehicle {index+1}.")
            
    def rtl_vehicle(self):
        """Return to launch the selected vehicle"""
        index = self.get_selected_vehicle_index()
        if self.controller.rtl_vehicle(index):
            self.connection_status.append(f"Vehicle {index+1} returning to launch.")
        else:
            self.connection_status.append(f"Failed to RTL Vehicle {index+1}.")
            
    def arm_all_vehicles(self):
        """Arm all vehicles"""
        for i in range(len(self.controller.vehicles)):
            if self.controller.vehicles[i]:
                self.controller.arm_vehicle(i)
        self.connection_status.append("All vehicles armed.")
        
    def takeoff_all_vehicles(self):
        """Takeoff all vehicles"""
        altitude = self.takeoff_altitude.value()
        for i in range(len(self.controller.vehicles)):
            if self.controller.vehicles[i]:
                self.controller.takeoff_vehicle(i, altitude)
        self.connection_status.append(f"All vehicles taking off to {altitude}m.")
        
    def land_all_vehicles(self):
        """Land all vehicles"""
        for i in range(len(self.controller.vehicles)):
            if self.controller.vehicles[i]:
                self.controller.land_vehicle(i)
        self.connection_status.append("All vehicles landing.")
        
    def rtl_all_vehicles(self):
        """RTL all vehicles"""
        for i in range(len(self.controller.vehicles)):
            if self.controller.vehicles[i]:
                self.controller.rtl_vehicle(i)
        self.connection_status.append("All vehicles returning to launch.")
        
    def send_ned_position(self):
        """Send NED position command"""
        index = self.get_selected_vehicle_index(self.advanced_vehicle_selector)
        x = self.ned_x.value()
        y = self.ned_y.value()
        z = self.ned_z.value()
        
        if self.controller.send_ned_to_vehicle(index, x, y, z):
            self.connection_status.append(f"Vehicle {index+1} moving to NED position ({x}, {y}, {z}).")
        else:
            self.connection_status.append(f"Failed to send NED position to Vehicle {index+1}.")
            
    def yaw_to_target(self):
        """Yaw vehicle to target location"""
        index = self.get_selected_vehicle_index(self.advanced_vehicle_selector)
        lat = self.target_lat.value()
        lon = self.target_lon.value()
        
        bearing = self.controller.yaw_to_target(index, lat, lon)
        if bearing is not None:
            self.connection_status.append(f"Vehicle {index+1} yawing to target. Bearing: {bearing:.1f}°")
        else:
            self.connection_status.append(f"Failed to yaw Vehicle {index+1} to target.")
            
    def toggle_auto_refresh(self):
        """Toggle automatic status refresh"""
        if self.status_timer.isActive():
            self.status_timer.stop()
            self.auto_refresh_btn.setText("Start Auto Refresh")
            self.auto_refresh_btn.setStyleSheet("QPushButton { background-color: #20c997; color: white; padding: 8px; }")
        else:
            self.status_timer.start(1000)  # Update every second
            self.auto_refresh_btn.setText("Stop Auto Refresh")
            self.auto_refresh_btn.setStyleSheet("QPushButton { background-color: #dc3545; color: white; padding: 8px; }")
            
    def update_status_display(self):
        """Update the status display table"""
        for i in range(len(self.controller.vehicles)):
            if self.controller.vehicles[i]:
                status = self.controller.get_vehicle_status(i)
                if status:
                    # Armed status with color coding
                    armed_item = QTableWidgetItem("Yes" if status['armed'] else "No")
                    if status['armed']:
                        armed_item.setBackground(armed_item.background().color().fromRgb(144, 238, 144))  # Light green
                    else:
                        armed_item.setBackground(armed_item.background().color().fromRgb(255, 182, 193))  # Light red
                    self.status_table.setItem(i, 1, armed_item)
                    
                    self.status_table.setItem(i, 2, QTableWidgetItem(status['mode']))
                    self.status_table.setItem(i, 3, QTableWidgetItem(f"{status['altitude']:.1f}"))
                    self.status_table.setItem(i, 4, QTableWidgetItem(f"{status['battery']:.1f}"))
                    self.status_table.setItem(i, 5, QTableWidgetItem(str(status['gps_fix'])))
                    self.status_table.setItem(i, 6, QTableWidgetItem(str(status['satellites'])))
                else:
                    # Clear row if no status available
                    for j in range(1, 7):
                        self.status_table.setItem(i, j, QTableWidgetItem("N/A"))


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    window = DroneControlUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()