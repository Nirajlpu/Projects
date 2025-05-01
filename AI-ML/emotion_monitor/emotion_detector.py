import cv2
import numpy as np
from deepface import DeepFace
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from database import DatabaseManager
import time

class EmotionDetector(QThread):
    emotion_detected = pyqtSignal(str, float)  
    frame_updated = pyqtSignal(np.ndarray)  
    
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.running = False
        self.db = DatabaseManager()
        
       
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
       
        self.backend_config = {
            'model_name': 'Facenet',
            'detector_backend': 'opencv',
            'distance_metric': 'cosine'
        }
    
    def run(self):
        self.running = True
        cap = cv2.VideoCapture(0)  
        
       
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        last_analysis_time = 0
        analysis_interval = 5 
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
            
          
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
           
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            current_time = time.time()
            
           
            if current_time - last_analysis_time > analysis_interval and len(faces) > 0:
                try:
                  
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                   
                    analysis = DeepFace.analyze(
                        img_path=rgb_frame,
                        actions=['emotion'],
                        enforce_detection=False,
                        silent=True,
                        detector_backend='opencv'
                    )
                    
                    if analysis and isinstance(analysis, list):
                       
                        face_analysis = analysis[0]
                        dominant_emotion = face_analysis['dominant_emotion']
                        emotion_score = face_analysis['emotion'][dominant_emotion] / 100
                        
                      
                        self.db.log_emotion(self.employee_id, dominant_emotion, emotion_score)
                        
                       
                        self.emotion_detected.emit(dominant_emotion, emotion_score)
                
                except Exception as e:
                    print(f"Emotion analysis error: {str(e)}")
                
                last_analysis_time = current_time
            
           
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
           
            self.frame_updated.emit(frame)
            
           
            self.msleep(50)
        
        
        cap.release()
    
    def stop(self):
        self.running = False
        self.wait()