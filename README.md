# Dollar Serial Number Tracker

A collaborative application for tracking and valuing paper money collections. Built with Python and PyQt6, this application allows multiple users to manage a shared collection of bills while tracking who added each entry.

## Features

- Multi-user support with secure authentication
- Network sharing capabilities
- Bill image processing and serial number recognition
- Automatic value estimation through web scraping
- GitHub integration for easy sharing and collaboration
- Server invitation system for secure access

## Prerequisites

- Python 3.8 or higher
- Git
- pip (Python package manager)
- GitHub account (for repository creation)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/velvetfox24/dollar-serial-tracker
cd dollar-serial-tracker
```

2. Create and activate a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/macOS
# or
.\venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Required Dependencies

The following packages are required and will be installed automatically:

- PyQt6 (6.4.0 or higher) - GUI framework
- requests (2.28.0 or higher) - HTTP client
- beautifulsoup4 (4.11.0 or higher) - Web scraping
- opencv-python (4.7.0 or higher) - Image processing
- numpy (1.23.0 or higher) - Numerical computing
- pillow (9.3.0 or higher) - Image processing
- pyzbar (0.1.9 or higher) - Barcode scanning
- cryptography (38.0.0 or higher) - Security features

## First-Time Setup

1. Run the application:
```bash
python3 main.py
```

2. On first run, you'll be prompted to:
   - Enter your GitHub personal access token
   - Create a new repository name
   - Set up server configuration

3. After GitHub setup, you'll need to:
   - Configure server settings (if running as server)
   - Create a user account
   - Log in to start using the application

## Server Setup

To run as a server:

1. Start the server:
```bash
python3 server.py
```

2. Generate an invitation code to share with other users

To join an existing server:

1. Get the invitation code from the server owner
2. Use the "Join Server" option in the application
3. Enter the invitation code when prompted

## Usage

1. **Adding Bills**:
   - Click "Add Bill" in the Collection tab
   - Enter bill details or upload an image
   - The application will automatically process the image and extract information

2. **Searching Bills**:
   - Use the search bar in the Collection tab
   - Search by serial number, face value, or other attributes
   - Results will display with images and estimated values

3. **Managing Server**:
   - Use the Server tab to:
     - Start/stop the server
     - Generate invitation codes
     - Monitor connected users

## Security Features

- Secure password hashing
- Encrypted network communication
- GitHub-based authentication
- Invitation-based server access
- User permission management

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Check Python version:
```bash
python3 --version
```

3. Verify GitHub token permissions:
   - The token needs 'repo' scope
   - Check token validity in GitHub settings

4. Network issues:
   - Ensure server port is not blocked
   - Verify correct server address and port
   - Check firewall settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 