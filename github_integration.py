import requests
import json
import os
from config import Config
import subprocess
import shutil
from pathlib import Path

class GitHubIntegration:
    def __init__(self):
        self.config = Config()
        self.github_token = self.config.get_github_token()
        self.headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
    def create_repository(self, name, description="Dollar Serial Number Tracker"):
        """Create a new GitHub repository"""
        if not self.github_token:
            return {'success': False, 'error': 'GitHub token not set'}
            
        data = {
            'name': name,
            'description': description,
            'private': True,
            'auto_init': True
        }
        
        try:
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                return {'success': True, 'repo_url': response.json()['clone_url']}
            else:
                return {'success': False, 'error': response.json().get('message', 'Unknown error')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def push_to_github(self, repo_url):
        """Push local changes to GitHub"""
        try:
            # Initialize git if not already done
            if not os.path.exists('.git'):
                subprocess.run(['git', 'init'], check=True)
                
            # Add all files
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', 'Initial commit'], check=True)
            
            # Add remote
            subprocess.run(['git', 'remote', 'add', 'origin', repo_url], check=True)
            
            # Push to GitHub
            subprocess.run(['git', 'push', '-u', 'origin', 'master'], check=True)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def generate_invitation_link(self, repo_url):
        """Generate an invitation link for the repository"""
        try:
            # Extract owner and repo name from URL
            parts = repo_url.split('/')
            owner = parts[-2]
            repo = parts[-1].replace('.git', '')
            
            # Create a collaborator invitation
            response = requests.put(
                f'https://api.github.com/repos/{owner}/{repo}/collaborators/USERNAME',
                headers=self.headers,
                json={'permission': 'push'}
            )
            
            if response.status_code in [201, 204]:
                return {'success': True, 'invitation_url': response.json().get('html_url')}
            else:
                return {'success': False, 'error': response.json().get('message', 'Unknown error')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def accept_invitation(self, invitation_url):
        """Accept a repository invitation"""
        try:
            # Extract invitation ID from URL
            invitation_id = invitation_url.split('/')[-1]
            
            # Accept the invitation
            response = requests.patch(
                f'https://api.github.com/user/repository_invitations/{invitation_id}',
                headers=self.headers
            )
            
            if response.status_code == 204:
                return {'success': True}
            else:
                return {'success': False, 'error': response.json().get('message', 'Unknown error')}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def clone_repository(self, repo_url, destination=None):
        """Clone a repository"""
        try:
            if destination is None:
                destination = os.getcwd()
                
            subprocess.run(['git', 'clone', repo_url, destination], check=True)
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def pull_changes(self):
        """Pull latest changes from GitHub"""
        try:
            subprocess.run(['git', 'pull'], check=True)
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def create_server_branch(self):
        """Create a branch for server configuration"""
        try:
            # Create and switch to server branch
            subprocess.run(['git', 'checkout', '-b', 'server'], check=True)
            
            # Create server configuration
            server_config = {
                'host': '0.0.0.0',
                'port': 5000,
                'token': self.config.generate_invitation_token()
            }
            
            with open('server_config.json', 'w') as f:
                json.dump(server_config, f, indent=4)
                
            # Commit server configuration
            subprocess.run(['git', 'add', 'server_config.json'], check=True)
            subprocess.run(['git', 'commit', '-m', 'Add server configuration'], check=True)
            subprocess.run(['git', 'push', '-u', 'origin', 'server'], check=True)
            
            return {'success': True}
            
        except Exception as e:
            return {'success': False, 'error': str(e)} 