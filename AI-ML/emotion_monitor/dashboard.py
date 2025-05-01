import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QColor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from datetime import datetime, timedelta
from database import DatabaseManager
from emotion_detector import EmotionDetector

class Dashboard(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = DatabaseManager()
        
        self.setWindowTitle(f"Employee Emotion Monitor - {user_data['name']}")
        self.resize(1000, 700)
        
       
        self._init_ui()
        
        
        if user_data['designation'].lower() != 'hr':
            self.start_emotion_detection()
        
       
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_dashboard)
        self.update_timer.start(10000)  
    
    def _init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
       
        header = QLabel(f"Welcome, {self.user_data['name']} ({self.user_data['designation']})")
        header.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        header.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(header)
        
       
        self.tabs = QTabWidget()
        
        if self.user_data['designation'].lower() == 'hr':
           
            self._setup_hr_dashboard()
        else:
           
            self._setup_employee_dashboard()
        
        main_layout.addWidget(self.tabs)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def _setup_hr_dashboard(self):
        
        overview_tab = QWidget()
        overview_layout = QVBoxLayout()
        
       
        self.emotion_chart = EmotionChart()
        overview_layout.addWidget(self.emotion_chart)
        
        
        negative_label = QLabel("Employees with Frequent Negative Emotions")
        negative_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 20px;")
        overview_layout.addWidget(negative_label)
        
        self.negative_table = QTableWidget()
        self.negative_table.setColumnCount(4)
        self.negative_table.setHorizontalHeaderLabels(["Employee ID", "Name", "Emotion", "Count"])
        self.negative_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        overview_layout.addWidget(self.negative_table)
        
        overview_tab.setLayout(overview_layout)
        self.tabs.addTab(overview_tab, "Overview")
        
       
        self.employee_stats_tab = QWidget()
        employee_stats_layout = QVBoxLayout()
        
       
        self.employee_stats_chart = EmployeeStatsChart()
        employee_stats_layout.addWidget(self.employee_stats_chart)
        
        self.employee_stats_tab.setLayout(employee_stats_layout)
        self.tabs.addTab(self.employee_stats_tab, "Employee Stats")
    
    def _setup_employee_dashboard(self):
       
        webcam_tab = QWidget()
        webcam_layout = QVBoxLayout()
        
       
        self.webcam_label = QLabel()
        self.webcam_label.setAlignment(Qt.AlignCenter)
        self.webcam_label.setStyleSheet("border: 1px solid #ccc;")
        webcam_layout.addWidget(self.webcam_label)
        
       
        self.current_emotion = QLabel("Detecting emotion...")
        self.current_emotion.setAlignment(Qt.AlignCenter)
        self.current_emotion.setStyleSheet("font-size: 16px; margin-top: 10px;")
        webcam_layout.addWidget(self.current_emotion)
        
        webcam_tab.setLayout(webcam_layout)
        self.tabs.addTab(webcam_tab, "Emotion Detection")
        
       
        stats_tab = QWidget()
        stats_layout = QVBoxLayout()
        
        self.personal_stats_chart = EmployeeStatsChart(employee_id=self.user_data['employee_id'])
        stats_layout.addWidget(self.personal_stats_chart)
        
        stats_tab.setLayout(stats_layout)
        self.tabs.addTab(stats_tab, "My Stats")
    
    def start_emotion_detection(self):
        """Start the emotion detection thread"""
        self.detector = EmotionDetector(self.user_data['employee_id'])
        self.detector.frame_updated.connect(self.update_webcam_feed)
        self.detector.emotion_detected.connect(self.update_emotion_display)
        self.detector.start()
    
    def update_webcam_feed(self, frame):
        """Update the webcam feed with the current frame"""
       
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        
       
        pixmap = QPixmap.fromImage(q_img)
        self.webcam_label.setPixmap(pixmap.scaled(
            self.webcam_label.width(), self.webcam_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    
    def update_emotion_display(self, emotion, confidence):
        """Update the current emotion display"""
        emotion_colors = {
            'happy': '#4CAF50',    
            'sad': '#2196F3',     
            'angry': '#F44336',    
            'surprise': '#FFC107',  
            'fear': '#9C27B0',    
            'disgust': '#795548',  
            'neutral': '#9E9E9E'   
        }
        
        color = emotion_colors.get(emotion, '#000000')
        self.current_emotion.setText(
            f"Current emotion: <span style='color: {color}; font-weight: bold;'>{emotion}</span> "
            f"(confidence: {confidence:.1%})"
        )
        
      
        if emotion == 'sad' and confidence > 0.7:
            self.current_emotion.setText(
                self.current_emotion.text() + "<br><i>We notice you might be feeling down. "
                "Remember, it's okay to take a break if you need to.</i>"
            )
    
    def update_dashboard(self):
        """Periodically update the dashboard data"""
        if self.user_data['designation'].lower() == 'hr':
           
            overall_stats, negative_stats = self.db.get_all_emotion_stats()
            
           
            self.emotion_chart.update_data(overall_stats)
            
           
            self.negative_table.setRowCount(len(negative_stats))
            for row, (emp_id, name, emotion, count) in enumerate(negative_stats):
                self.negative_table.setItem(row, 0, QTableWidgetItem(emp_id))
                self.negative_table.setItem(row, 1, QTableWidgetItem(name))
                self.negative_table.setItem(row, 2, QTableWidgetItem(emotion))
                self.negative_table.setItem(row, 3, QTableWidgetItem(str(count)))
        
        else:
           
            self.personal_stats_chart.update_data()
    
    def closeEvent(self, event):
        """Clean up resources when window is closed"""
        if hasattr(self, 'detector'):
            self.detector.stop()
        super().closeEvent(event)

class EmotionChart(FigureCanvas):
    def __init__(self, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        
      
        self.ax.set_title("Employee Emotion Distribution (Last 7 Days)")
        self.ax.set_ylabel("Count")
        self.bars = None
    
    def update_data(self, emotion_data):
        """Update the chart with new emotion data"""
        self.ax.clear()
        
        if not emotion_data:
            self.ax.text(0.5, 0.5, "No data available", 
                        ha='center', va='center', fontsize=12)
            self.draw()
            return
        
        emotions = [e[0] for e in emotion_data]
        counts = [e[1] for e in emotion_data]
        
       
        emotion_colors = {
            'happy': '#4CAF50',
            'sad': '#2196F3',
            'angry': '#F44336',
            'surprise': '#FFC107',
            'fear': '#9C27B0',
            'disgust': '#795548',
            'neutral': '#9E9E9E'
        }
        
        colors = [emotion_colors.get(e, '#000000') for e in emotions]
        
        self.bars = self.ax.bar(emotions, counts, color=colors)
        self.ax.set_title("Employee Emotion Distribution (Last 7 Days)")
        self.ax.set_ylabel("Count")
        
      
        for bar in self.bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        
        self.draw()

class EmployeeStatsChart(FigureCanvas):
    def __init__(self, employee_id=None, parent=None):
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        super().__init__(self.fig)
        self.setParent(parent)
        self.employee_id = employee_id
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
        
        
        if employee_id:
            self.ax.set_title("Your Emotion Trends (Last 7 Days)")
        else:
            self.ax.set_title("Employee Emotion Trends")
        self.ax.set_ylabel("Count")
        self.lines = {}
    
    def update_data(self):
        """Update the chart with new data"""
        if not self.employee_id:
            return
        
        self.ax.clear()
        
        db = DatabaseManager()
        stats = db.get_employee_emotion_stats(self.employee_id)
        
        if not stats:
            self.ax.text(0.5, 0.5, "No data available", 
                        ha='center', va='center', fontsize=12)
            self.draw()
            return
        
       
        emotion_data = {}
        days = set()
        
        for emotion, count, day in stats:
            if emotion not in emotion_data:
                emotion_data[emotion] = {}
            emotion_data[emotion][day] = count
            days.add(day)
        
    
        days = sorted(list(days))
        
       
        emotion_colors = {
            'happy': '#4CAF50',
            'sad': '#2196F3',
            'angry': '#F44336',
            'surprise': '#FFC107',
            'fear': '#9C27B0',
            'disgust': '#795548',
            'neutral': '#9E9E9E'
        }
        
       
        for emotion, data in emotion_data.items():
            counts = [data.get(day, 0) for day in days]
            line, = self.ax.plot(days, counts, 
                                label=emotion, 
                                color=emotion_colors.get(emotion, '#000000'),
                                marker='o')
            self.lines[emotion] = line
        
        self.ax.set_title(f"Emotion Trends (Last 7 Days)")
        self.ax.set_ylabel("Count")
        self.ax.legend()
        
       
        plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        
        self.draw()

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    sample_user = {
        "name": "John Doe",
        "employee_id": "EMP001",
        "designation": "Employee"  # or "HR" to test the HR dashboard
    }

    app = QApplication(sys.argv)
    window = Dashboard(sample_user)
    window.show()
    sys.exit(app.exec_())