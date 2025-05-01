from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QStackedWidget, QMessageBox, QFormLayout
)
from PyQt5.QtCore import Qt
from database import DatabaseManager

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Emotion Monitor - Login")
        self.resize(400, 300)
        
        self.db = DatabaseManager()
        self.current_user = None
        
       
        self.stacked_widget = QStackedWidget()
        
        
        self.login_page = QWidget()
        self._setup_login_page()
        
        
        self.signup_page = QWidget()
        self._setup_signup_page()
        
       
        self.stacked_widget.addWidget(self.login_page)
        self.stacked_widget.addWidget(self.signup_page)
        
       
        self.setCentralWidget(self.stacked_widget)
    
    def _setup_login_page(self):
        layout = QVBoxLayout()
        
       
        title = QLabel("Employee Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(title)
        
        
        form_layout = QFormLayout()
        
        self.login_employee_id = QLineEdit()
        self.login_employee_id.setPlaceholderText("Enter your employee ID")
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Employee ID:", self.login_employee_id)
        form_layout.addRow("Password:", self.login_password)
        
        layout.addLayout(form_layout)
        
       
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.handle_login)
        login_btn.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(login_btn)
        
       
        switch_text = QLabel("Don't have an account?")
        switch_text.setAlignment(Qt.AlignCenter)
        
        switch_btn = QPushButton("Sign Up")
        switch_btn.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        switch_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        switch_layout = QHBoxLayout()
        switch_layout.addStretch()
        switch_layout.addWidget(switch_text)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        
        layout.addLayout(switch_layout)
        layout.addStretch()
        
        self.login_page.setLayout(layout)
    
    def _setup_signup_page(self):
        layout = QVBoxLayout()
        
       
        title = QLabel("Employee Registration")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 30px;")
        layout.addWidget(title)
        
      
        form_layout = QFormLayout()
        
        self.signup_employee_id = QLineEdit()
        self.signup_employee_id.setPlaceholderText("Enter unique employee ID")
        
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Enter your full name")
        
        self.signup_designation = QLineEdit()
        self.signup_designation.setPlaceholderText("Enter your designation")
        
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Create a password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        
        self.signup_confirm_password = QLineEdit()
        self.signup_confirm_password.setPlaceholderText("Confirm password")
        self.signup_confirm_password.setEchoMode(QLineEdit.Password)
        
        form_layout.addRow("Employee ID:", self.signup_employee_id)
        form_layout.addRow("Full Name:", self.signup_name)
        form_layout.addRow("Designation:", self.signup_designation)
        form_layout.addRow("Password:", self.signup_password)
        form_layout.addRow("Confirm Password:", self.signup_confirm_password)
        
        layout.addLayout(form_layout)
        
       
        signup_btn = QPushButton("Register")
        signup_btn.clicked.connect(self.handle_signup)
        signup_btn.setStyleSheet("padding: 8px; font-size: 14px;")
        layout.addWidget(signup_btn)
        
       
        switch_text = QLabel("Already have an account?")
        switch_text.setAlignment(Qt.AlignCenter)
        
        switch_btn = QPushButton("Login")
        switch_btn.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        switch_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        switch_layout = QHBoxLayout()
        switch_layout.addStretch()
        switch_layout.addWidget(switch_text)
        switch_layout.addWidget(switch_btn)
        switch_layout.addStretch()
        
        layout.addLayout(switch_layout)
        layout.addStretch()
        
        self.signup_page.setLayout(layout)
    
    def handle_login(self):
        employee_id = self.login_employee_id.text().strip()
        password = self.login_password.text().strip()
        
        if not employee_id or not password:
            QMessageBox.warning(self, "Login Failed", "Please enter both employee ID and password")
            return
        
        user = self.db.authenticate_user(employee_id, password)
        
        if user:
            self.current_user = {
                'employee_id': user[0],
                'name': user[1],
                'designation': user[2]
            }
            self.close()  
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid employee ID or password")
    
    def handle_signup(self):
        employee_id = self.signup_employee_id.text().strip()
        name = self.signup_name.text().strip()
        designation = self.signup_designation.text().strip()
        password = self.signup_password.text().strip()
        confirm_password = self.signup_confirm_password.text().strip()
        
       
        if not all([employee_id, name, designation, password, confirm_password]):
            QMessageBox.warning(self, "Registration Failed", "All fields are required")
            return
        
        if password != confirm_password:
            QMessageBox.warning(self, "Registration Failed", "Passwords do not match")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Registration Failed", "Password must be at least 6 characters")
            return
        
       
        success = self.db.add_user(employee_id, name, designation, password)
        
        if success:
            QMessageBox.information(self, "Registration Successful", "Account created successfully!")
            self.stacked_widget.setCurrentIndex(0) 
           
            self.signup_employee_id.clear()
            self.signup_name.clear()
            self.signup_designation.clear()
            self.signup_password.clear()
            self.signup_confirm_password.clear()
            