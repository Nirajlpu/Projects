import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow
from dashboard import Dashboard


class EmotionMonitorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.dashboard = None 
        
       
        self.login_window.closeEvent = self.on_login_window_close
    
    def on_login_window_close(self, event):
        """Handle login window close event"""
        if hasattr(self.login_window, 'current_user') and self.login_window.current_user:
            
            self.dashboard = Dashboard(self.login_window.current_user)
            self.dashboard.show()
        else:
            
            self.app.quit()
    
    def run(self):
        """Run the application"""
        self.login_window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = EmotionMonitorApp()
    app.run()