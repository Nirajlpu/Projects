import numpy as np
import sounddevice as sd
import librosa
from datetime import datetime
from PyQt5.QtCore import QThread, pyqtSignal
from database import DatabaseManager
import time
import warnings
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
import joblib
import os


warnings.filterwarnings('ignore')

class AudioAnalyzer(QThread):
    emotion_detected = pyqtSignal(str, float)  
    
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.running = False
        self.db = DatabaseManager()
        
       
        self.sample_rate = 22050  
        self.duration = 5  
        self.silence_threshold = 0.03 
        
       
        self.model = self._load_audio_model()
        self.scaler = self._load_scaler()
        
       
        self.emotion_map = {
            0: 'neutral',
            1: 'happy',
            2: 'sad',
            3: 'angry',
            4: 'fearful'
        }
    
    def _load_audio_model(self):
        """Load pre-trained audio emotion model"""
       
        
        model_path = 'models/audio_emotion_model.pkl'
        if os.path.exists(model_path):
            return joblib.load(model_path)
        else:
           
            print("Warning: Using dummy audio model. For real use, train a proper model.")
            return SVC(kernel='linear', probability=True)
    
    def _load_scaler(self):
        """Load feature scaler"""
        scaler_path = 'models/audio_scaler.pkl'
        if os.path.exists(scaler_path):
            return joblib.load(scaler_path)
        else:
           
            print("Warning: Using dummy audio scaler. For real use, train a proper scaler.")
            return StandardScaler()
    
    def run(self):
        """Main analysis loop"""
        self.running = True
        
      
        with sd.InputStream(samplerate=self.sample_rate,
                           channels=1,
                           dtype='float32',
                           blocksize=int(self.sample_rate * self.duration),
                           callback=self.audio_callback):
            
            print("Audio analysis started...")
            while self.running:
                time.sleep(0.1)  
    
    def audio_callback(self, indata, frames, time_info, status):
        """Callback function for audio stream"""
        if status:
            print("Audio stream status:", status)
        
       
        audio_data = np.squeeze(indata)
        
       
        if np.sqrt(np.mean(audio_data**2)) < self.silence_threshold:
            return
        
        try:
          
            features = self.extract_features(audio_data)
            
            if features is not None:
               
                features_scaled = self.scaler.transform([features])
                
              
                proba = self.model.predict_proba(features_scaled)[0]
                pred_class = np.argmax(proba)
                confidence = np.max(proba)
                emotion = self.emotion_map.get(pred_class, 'neutral')
                
               
                self.db.log_emotion(self.employee_id, emotion, confidence, source='audio')
                
                
                self.emotion_detected.emit(emotion, confidence)
        except Exception as e:
            print(f"Audio analysis error: {str(e)}")
    
    def extract_features(self, audio_data):
        """Extract audio features for emotion recognition"""
        try:
           
            if len(audio_data.shape) > 1:
                audio_data = librosa.to_mono(audio_data.T)
            
            
            if len(audio_data) < self.sample_rate // 2:  
                return None
            
           
            features = []
            
           
            mfccs = librosa.feature.mfcc(y=audio_data, sr=self.sample_rate, n_mfcc=13)
            mfccs_mean = np.mean(mfccs, axis=1)
            features.extend(mfccs_mean)
            
           
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
            chroma_mean = np.mean(chroma, axis=1)
            features.extend(chroma_mean)
            
           
            mel = librosa.feature.melspectrogram(y=audio_data, sr=self.sample_rate)
            mel_mean = np.mean(mel, axis=1)
            features.extend(mel_mean)
            
           
            contrast = librosa.feature.spectral_contrast(y=audio_data, sr=self.sample_rate)
            contrast_mean = np.mean(contrast, axis=1)
            features.extend(contrast_mean)
            
            
            tonnetz = librosa.feature.tonnetz(y=audio_data, sr=self.sample_rate)
            tonnetz_mean = np.mean(tonnetz, axis=1)
            features.extend(tonnetz_mean)
            
           
            zcr = librosa.feature.zero_crossing_rate(audio_data)
            features.append(np.mean(zcr))
            
           
            rms = librosa.feature.rms(y=audio_data)
            features.append(np.mean(rms))
            
            return np.array(features)
        
        except Exception as e:
            print(f"Feature extraction error: {str(e)}")
            return None
    
    def stop(self):
        """Stop the audio analysis"""
        self.running = False
        self.wait()

class DummyAudioAnalyzer(QThread):
    """Fallback analyzer when audio dependencies aren't available"""
    emotion_detected = pyqtSignal(str, float)
    
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.running = False
    
    def run(self):
        """Dummy run method that does nothing"""
        self.running = True
        while self.running:
            time.sleep(1)
    
    def stop(self):
        """Stop the dummy analyzer"""
        self.running = False
        self.wait()

def create_audio_analyzer(employee_id, parent=None):
    """Factory function to create appropriate audio analyzer"""
    try:
       
        import sounddevice as sd
        import librosa
        return AudioAnalyzer(employee_id, parent)
    except ImportError:
        print("Audio dependencies not found. Audio analysis will be disabled.")
        return DummyAudioAnalyzer(employee_id, parent)