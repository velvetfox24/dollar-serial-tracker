from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QComboBox,
                            QTableWidget, QTableWidgetItem, QFileDialog,
                            QMessageBox, QFormLayout, QCheckBox, QDialog,
                            QDialogButtonBox, QTabWidget, QGroupBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage
import sys
from client import DollarTrackerClient
from value_scraper import ValueScraper
from image_processor import ImageProcessor
from config import Config
from github_integration import GitHubIntegration
import cv2
import os

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Login")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Server settings
        server_group = QWidget()
        server_layout = QFormLayout(server_group)
        self.server_host = QLineEdit("localhost")
        self.server_port = QLineEdit("5000")
        server_layout.addRow("Server Host:", self.server_host)
        server_layout.addRow("Server Port:", self.server_port)
        layout.addWidget(server_group)
        
        # Login form
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("Username:", self.username)
        form_layout.addRow("Password:", self.password)
        layout.addWidget(form_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_credentials(self):
        return {
            'host': self.server_host.text(),
            'port': int(self.server_port.text()),
            'username': self.username.text(),
            'password': self.password.text()
        }

class GitHubSetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GitHub Setup")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # GitHub token input
        token_group = QGroupBox("GitHub Token")
        token_layout = QFormLayout(token_group)
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your GitHub personal access token")
        token_layout.addRow("Token:", self.token_input)
        layout.addWidget(token_group)
        
        # Repository setup
        repo_group = QGroupBox("Repository Setup")
        repo_layout = QFormLayout(repo_group)
        self.repo_name = QLineEdit()
        self.repo_name.setPlaceholderText("Enter repository name")
        repo_layout.addRow("Repository Name:", self.repo_name)
        layout.addWidget(repo_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_github_info(self):
        return {
            'token': self.token_input.text(),
            'repo_name': self.repo_name.text()
        }

class ServerInviteDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Join Server")
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Invitation code input
        invite_group = QGroupBox("Server Invitation")
        invite_layout = QFormLayout(invite_group)
        self.invite_code = QLineEdit()
        self.invite_code.setPlaceholderText("Enter invitation code")
        invite_layout.addRow("Invitation Code:", self.invite_code)
        layout.addWidget(invite_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_invite_code(self):
        return self.invite_code.text()

class DollarTrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dollar Serial Number Tracker")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize components
        self.config = Config()
        self.client = None
        self.image_processor = ImageProcessor()
        self.github = GitHubIntegration()
        
        # Check if GitHub setup is needed
        if not self.config.get_github_token():
            self.show_github_setup()
        else:
            self.show_login_dialog()
            
    def show_github_setup(self):
        dialog = GitHubSetupDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            github_info = dialog.get_github_info()
            self.config.set_github_token(github_info['token'])
            
            # Create repository
            result = self.github.create_repository(github_info['repo_name'])
            if result['success']:
                # Push initial code
                self.github.push_to_github(result['repo_url'])
                # Create server branch
                self.github.create_server_branch()
                QMessageBox.information(self, "Success", "Repository created successfully")
                self.show_login_dialog()
            else:
                QMessageBox.warning(self, "Error", result.get('error', 'Failed to create repository'))
                self.show_github_setup()
        else:
            sys.exit(0)
            
    def show_login_dialog(self):
        dialog = LoginDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            credentials = dialog.get_credentials()
            self.client = DollarTrackerClient(credentials['host'], credentials['port'])
            
            # Try to login
            response = self.client.login(credentials['username'], credentials['password'])
            if not response['success']:
                QMessageBox.warning(self, "Login Failed", response.get('error', 'Unknown error'))
                self.show_login_dialog()
            else:
                self.setup_ui()
        else:
            sys.exit(0)
            
    def setup_ui(self):
        # Create main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Create tab widget
        tabs = QTabWidget()
        
        # Main tab
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        
        # Create form for new bill entry
        self.create_entry_form(main_layout)
        
        # Create search interface
        self.create_search_interface(main_layout)
        
        # Create results table
        self.create_results_table(main_layout)
        
        tabs.addTab(main_tab, "Collection")
        
        # Server tab
        server_tab = QWidget()
        server_layout = QVBoxLayout(server_tab)
        self.create_server_interface(server_layout)
        tabs.addTab(server_tab, "Server")
        
        layout.addWidget(tabs)
        
    def create_server_interface(self, parent_layout):
        # Server status
        status_group = QGroupBox("Server Status")
        status_layout = QFormLayout(status_group)
        
        self.server_status = QLabel("Not Running")
        status_layout.addRow("Status:", self.server_status)
        
        # Server controls
        controls_group = QGroupBox("Server Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        start_button = QPushButton("Start Server")
        start_button.clicked.connect(self.start_server)
        controls_layout.addWidget(start_button)
        
        stop_button = QPushButton("Stop Server")
        stop_button.clicked.connect(self.stop_server)
        controls_layout.addWidget(stop_button)
        
        # Invitation management
        invite_group = QGroupBox("Invitations")
        invite_layout = QVBoxLayout(invite_group)
        
        generate_button = QPushButton("Generate Invitation Code")
        generate_button.clicked.connect(self.generate_invitation)
        invite_layout.addWidget(generate_button)
        
        join_button = QPushButton("Join Server")
        join_button.clicked.connect(self.join_server)
        invite_layout.addWidget(join_button)
        
        parent_layout.addWidget(status_group)
        parent_layout.addWidget(controls_group)
        parent_layout.addWidget(invite_group)
        
    def start_server(self):
        # Start server process
        server_info = self.config.get_server_info()
        if server_info['is_server']:
            # TODO: Start server process
            self.server_status.setText("Running")
        else:
            QMessageBox.warning(self, "Error", "This instance is not configured as a server")
            
    def stop_server(self):
        # Stop server process
        self.server_status.setText("Not Running")
        
    def generate_invitation(self):
        server_info = self.config.get_server_info()
        if server_info['is_server']:
            invitation = {
                'server_token': server_info['server_token'],
                'host': server_info['server_host'],
                'port': server_info['server_port']
            }
            QMessageBox.information(self, "Invitation Code", 
                                  f"Share this code with others:\n{server_info['server_token']}")
        else:
            QMessageBox.warning(self, "Error", "Only server instances can generate invitations")
            
    def join_server(self):
        dialog = ServerInviteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            invite_code = dialog.get_invite_code()
            invitation = self.config.get_invitation(invite_code)
            
            if invitation:
                self.config.set_server_mode(False, invitation['host'], invitation['port'])
                QMessageBox.information(self, "Success", "Successfully joined server")
                self.show_login_dialog()
            else:
                QMessageBox.warning(self, "Error", "Invalid invitation code")
                
    def create_entry_form(self, parent_layout):
        form_group = QWidget()
        form_layout = QFormLayout(form_group)
        
        # Face value
        self.face_value = QComboBox()
        self.face_value.addItems(['1', '2', '5', '10', '20', '50', '100'])
        form_layout.addRow("Face Value:", self.face_value)
        
        # Serial number
        self.serial_number = QLineEdit()
        form_layout.addRow("Serial Number:", self.serial_number)
        
        # Printing location
        self.printing_location = QComboBox()
        self.printing_location.addItems(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L'])
        form_layout.addRow("Printing Location:", self.printing_location)
        
        # Series year
        self.series_year = QLineEdit()
        form_layout.addRow("Series Year:", self.series_year)
        
        # Star note
        self.is_star_note = QCheckBox()
        form_layout.addRow("Star Note:", self.is_star_note)
        
        # Image upload
        self.image_path = QLineEdit()
        self.image_path.setReadOnly(True)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_image)
        
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_path)
        image_layout.addWidget(browse_button)
        form_layout.addRow("Bill Image:", image_layout)
        
        # Add bill button
        add_button = QPushButton("Add Bill")
        add_button.clicked.connect(self.add_bill)
        form_layout.addRow("", add_button)
        
        parent_layout.addWidget(form_group)
        
    def create_search_interface(self, parent_layout):
        search_group = QWidget()
        search_layout = QHBoxLayout(search_group)
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search by serial number...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_bills)
        
        search_layout.addWidget(self.search_field)
        search_layout.addWidget(search_button)
        
        parent_layout.addWidget(search_group)
        
    def create_results_table(self, parent_layout):
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels([
            "Face Value", "Serial Number", "Date Recorded",
            "Printing Location", "Series Year", "Star Note",
            "Estimated Value", "Added By", "Image"
        ])
        
        parent_layout.addWidget(self.results_table)
        
    def browse_image(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Bill Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_name:
            self.image_path.setText(file_name)
            
    def add_bill(self):
        # Get form data
        face_value = float(self.face_value.currentText())
        serial_number = self.serial_number.text().strip()
        printing_location = self.printing_location.currentText()
        series_year = self.series_year.text().strip()
        is_star_note = self.is_star_note.isChecked()
        image_path = self.image_path.text()
        
        if not serial_number:
            QMessageBox.warning(self, "Error", "Serial number is required")
            return
            
        # Process image if provided
        image_data = None
        if image_path:
            image_data = self.image_processor.process_bill_image(image_path)
            if image_data['success']:
                # Update serial number and star note status from image
                serial_number = image_data['serial_number']
                is_star_note = image_data['is_star_note']
                
        # Add to database through client
        response = self.client.add_bill(
            face_value=face_value,
            serial_number=serial_number,
            printing_location=printing_location,
            series_year=series_year if series_year else None,
            is_star_note=is_star_note,
            image_path=image_path
        )
        
        if response['success']:
            QMessageBox.information(self, "Success", "Bill added successfully")
            self.clear_form()
            self.search_bills()  # Refresh results
        else:
            QMessageBox.warning(self, "Error", response.get('error', 'Failed to add bill'))
            
    def search_bills(self):
        search_term = self.search_field.text().strip()
        if search_term:
            response = self.client.search_bills({'serial_number': search_term})
        else:
            response = self.client.search_bills({})
            
        if response['success']:
            self.display_results(response['results'])
        else:
            QMessageBox.warning(self, "Error", response.get('error', 'Search failed'))
            
    def display_results(self, results):
        self.results_table.setRowCount(len(results))
        for row, bill in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(str(bill[1])))  # Face value
            self.results_table.setItem(row, 1, QTableWidgetItem(bill[2]))  # Serial number
            self.results_table.setItem(row, 2, QTableWidgetItem(bill[3]))  # Date recorded
            self.results_table.setItem(row, 3, QTableWidgetItem(bill[4]))  # Printing location
            self.results_table.setItem(row, 4, QTableWidgetItem(str(bill[5])))  # Series year
            self.results_table.setItem(row, 5, QTableWidgetItem("Yes" if bill[6] else "No"))  # Star note
            self.results_table.setItem(row, 6, QTableWidgetItem(str(bill[8])))  # Estimated value
            self.results_table.setItem(row, 7, QTableWidgetItem(bill[9]))  # Added by
            
            # Display image if available
            if bill[7]:  # Image path
                pixmap = QPixmap(bill[7])
                if not pixmap.isNull():
                    label = QLabel()
                    label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio))
                    self.results_table.setCellWidget(row, 8, label)
                    
    def clear_form(self):
        self.serial_number.clear()
        self.series_year.clear()
        self.image_path.clear()
        self.is_star_note.setChecked(False)
        
    def closeEvent(self, event):
        if self.client:
            self.client.disconnect()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DollarTrackerGUI()
    window.show()
    sys.exit(app.exec()) 