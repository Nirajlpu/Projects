import os
import sqlite3
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QMessageBox
import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from utils import AlertManager, ImageUtils, StyleUtils

class AlertManager:
    """Handles alerts for HR about employee emotional states"""
    def __init__(self, db_manager):
        self.db = db_manager
    
    def check_for_alerts(self):
        """Check database for employees needing HR attention"""
        try:
            conn = sqlite3.connect(self.db.db_path)
            cursor = conn.cursor()
            
          
            cursor.execute('''
                SELECT u.employee_id, u.name, COUNT(*) as negative_count
                FROM emotion_logs e
                JOIN users u ON e.employee_id = u.employee_id
                WHERE e.emotion IN ('sad', 'angry', 'fear')
                AND date(e.timestamp) = date('now')
                GROUP BY u.employee_id
                HAVING COUNT(*) >= 3
                ORDER BY negative_count DESC
            ''')
            
            alerts = cursor.fetchall()
            return alerts
            
        except sqlite3.Error as e:
            print(f"Alert check error: {str(e)}")
            return []
        finally:
            if conn:
                conn.close()
    
    def show_alert_popup(self, parent_window):
        """Show alert popup if needed"""
        alerts = self.check_for_alerts()
        if alerts:
            message = "Employees needing attention:\n\n"
            for emp_id, name, count in alerts:
                message += f"{name} ({emp_id}): {count} negative emotions today\n"
            
            QMessageBox.warning(parent_window, "HR Alert", message)

class ImageUtils:
    """Utility class for image processing"""
    @staticmethod
    def cv2_to_qimage(cv_img):
        """Convert OpenCV image to QImage"""
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        q_img = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        return q_img
    
    @staticmethod
    def draw_emotion_text(image, emotion, confidence, position=(20, 40)):
        """Draw emotion text on image"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        color = (255, 255, 255)
        thickness = 2
        
        text = f"{emotion} ({confidence:.0%})"
        
       
        (text_width, text_height), _ = cv2.getTextSize(text, font, scale, thickness)
        cv2.rectangle(image, 
                     (position[0], position[1] - text_height - 10),
                     (position[0] + text_width, position[1] + 10),
                     (0, 0, 0), -1)
        
        
        cv2.putText(image, text, position, font, scale, color, thickness)
        return image

class DataExporter:
    """Handles exporting data to various formats"""
    @staticmethod
    def export_to_csv(db_path, output_file):
        """Export emotion data to CSV"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            
            cursor.execute('''
                SELECT u.employee_id, u.name, e.emotion, e.confidence, e.timestamp
                FROM emotion_logs e
                JOIN users u ON e.employee_id = u.employee_id
                ORDER BY e.timestamp
            ''')
            
            data = cursor.fetchall()
            
           
            with open(output_file, 'w') as f:
                f.write("employee_id,name,emotion,confidence,timestamp\n")
                for row in data:
                    f.write(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]}\n")
            
            return True
        except Exception as e:
            print(f"Export error: {str(e)}")
            return False
        finally:
            if conn:
                conn.close()

class StyleUtils:
    """Utility class for UI styling"""
    @staticmethod
    def get_main_stylesheet():
        """Returns the main application stylesheet"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLabel {
                font-size: 14px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
                top: -1px;
                background: white;
            }
            QTabBar::tab {
                background: #e0e0e0;
                border: 1px solid #ddd;
                padding: 8px 16px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
            }
        """
    
    @staticmethod
    def get_emotion_color(emotion):
        """Returns a color for the given emotion"""
        colors = {
            'happy': '#4CAF50',
            'sad': '#2196F3',
            'angry': '#F44336',
            'surprise': '#FFC107',
            'fear': '#9C27B0',
            'disgust': '#795548',
            'neutral': '#9E9E9E'
        }
        return colors.get(emotion.lower(), '#000000')

class TimeUtils:
    """Utility class for time-related functions"""
    @staticmethod
    def format_timestamp(timestamp):
        """Format SQLite timestamp to human-readable format"""
        try:
            dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            return dt.strftime("%b %d, %Y %I:%M %p")
        except:
            return timestamp
    
    @staticmethod
    def get_time_ranges(days=7):
        """Get time ranges for filtering data"""
        today = datetime.now().date()
        return {
            'Today': today.strftime("%Y-%m-%d"),
            'Last 7 Days': (today - timedelta(days=7)).strftime("%Y-%m-%d"),
            'This Month': today.replace(day=1).strftime("%Y-%m-%d"),
            'Last Month': (today.replace(day=1) - timedelta(days=1)).replace(day=1).strftime("%Y-%m-%d")
        }

class ChartUtils:
    """Utility class for chart creation"""
    @staticmethod
    def create_emotion_chart(data, title="Emotion Distribution"):
        """Create a matplotlib emotion distribution chart"""
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, "No data available", 
                   ha='center', va='center', fontsize=12)
            return FigureCanvas(fig)
        
        emotions = [d[0] for d in data]
        counts = [d[1] for d in data]
        colors = [StyleUtils.get_emotion_color(e) for e in emotions]
        
        bars = ax.bar(emotions, counts, color=colors)
        ax.set_title(title)
        ax.set_ylabel("Count")
        
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        return FigureCanvas(fig)
    
    @staticmethod
    def create_trend_chart(data, title="Emotion Trend"):
        """Create a line chart showing emotion trends over time"""
        fig = Figure(figsize=(8, 4))
        ax = fig.add_subplot(111)
        
        if not data:
            ax.text(0.5, 0.5, "No data available", 
                   ha='center', va='center', fontsize=12)
            return FigureCanvas(fig)
        
       
        emotion_data = {}
        for emotion, count, day in data:
            if emotion not in emotion_data:
                emotion_data[emotion] = {}
            emotion_data[emotion][day] = count
        
       
        for emotion, values in emotion_data.items():
            days = sorted(values.keys())
            counts = [values[day] for day in days]
            ax.plot(days, counts, 
                    label=emotion, 
                    color=StyleUtils.get_emotion_color(emotion),
                    marker='o')
        
        ax.set_title(title)
        ax.set_ylabel("Count")
        ax.legend()
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        return FigureCanvas(fig)

def create_data_directory():
    """Ensure data directory exists"""
    os.makedirs('data', exist_ok=True)