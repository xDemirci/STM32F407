#!/usr/bin/env python3
"""
Test script to verify all imports and basic functionality
"""

def test_imports():
    """Test if all required modules can be imported"""
    try:
        import sys
        print("✓ sys module imported")
        
        import threading
        print("✓ threading module imported")
        
        import time
        print("✓ time module imported")
        
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5.QtWidgets imported")
        
        from PyQt5.QtCore import QTimer, pyqtSignal, QObject
        print("✓ PyQt5.QtCore imported")
        
        from PyQt5.QtGui import QFont
        print("✓ PyQt5.QtGui imported")
        
        try:
            from dronekit import connect, VehicleMode, LocationGlobalRelative
            print("✓ dronekit imported")
        except ImportError:
            print("⚠ dronekit not found (install with: pip install dronekit)")
        
        try:
            from pymavlink import mavutil
            print("✓ pymavlink imported")
        except ImportError:
            print("⚠ pymavlink not found (install with: pip install pymavlink)")
        
        from drone_controller import DroneController
        print("✓ drone_controller module imported")
        
        print("\n✅ All core imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_controller():
    """Test basic DroneController functionality"""
    try:
        controller = DroneController()
        print("✓ DroneController created successfully")
        
        # Test adding vehicles
        controller.add_vehicle("tcp:127.0.0.1:14550")
        controller.add_vehicle("tcp:127.0.0.1:14551")
        print(f"✓ Added {len(controller.connection_strings)} connection strings")
        
        print("✅ Controller test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Controller test error: {e}")
        return False

if __name__ == "__main__":
    print("🚁 Drone Control UI - Import Test\n")
    
    if test_imports():
        print("\n" + "="*50)
        if test_controller():
            print("\n✅ All tests passed! You can now run:")
            print("   python drone_ui.py")
            print("   or")
            print("   python run_drone_ui.py")
        else:
            print("\n❌ Controller tests failed")
    else:
        print("\n❌ Import tests failed")
        print("Please install missing dependencies with:")
        print("pip install -r requirements.txt")