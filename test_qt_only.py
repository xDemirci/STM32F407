#!/usr/bin/env python3
"""
Test script to verify Qt5 works without dronekit
"""

def test_qt():
    """Test if Qt5 can be imported and works"""
    try:
        import sys
        print("✓ sys module imported")
        
        from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
        print("✓ PyQt5.QtWidgets imported")
        
        from PyQt5.QtCore import QTimer
        print("✓ PyQt5.QtCore imported")
        
        from PyQt5.QtGui import QFont
        print("✓ PyQt5.QtGui imported")
        
        # Test creating a simple Qt application
        app = QApplication(sys.argv)
        window = QMainWindow()
        window.setWindowTitle("Test Window")
        label = QLabel("Qt5 is working!", window)
        window.setCentralWidget(label)
        window.resize(300, 100)
        
        print("✓ Qt5 application created successfully")
        print("✅ Qt5 test passed!")
        
        # Don't show the window in headless environment
        return True
        
    except Exception as e:
        print(f"❌ Qt5 test error: {e}")
        return False

if __name__ == "__main__":
    print("🚁 Qt5 Only Test\n")
    test_qt()