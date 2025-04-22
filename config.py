import json
import os
import secrets
from pathlib import Path

class Config:
    def __init__(self):
        self.config_dir = Path.home() / '.dollar_tracker'
        self.config_file = self.config_dir / 'config.json'
        self.server_file = self.config_dir / 'server.json'
        self.invitations_file = self.config_dir / 'invitations.json'
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(exist_ok=True)
        
        # Initialize config files if they don't exist
        if not self.config_file.exists():
            self._create_default_config()
        if not self.server_file.exists():
            self._create_default_server()
        if not self.invitations_file.exists():
            self._create_default_invitations()
            
    def _create_default_config(self):
        default_config = {
            'github_token': '',
            'auto_update': True,
            'theme': 'default'
        }
        self.save_config(default_config)
        
    def _create_default_server(self):
        default_server = {
            'is_server': False,
            'server_host': 'localhost',
            'server_port': 5000,
            'server_token': secrets.token_hex(32)
        }
        self.save_server_config(default_server)
        
    def _create_default_invitations(self):
        self.save_invitations([])
        
    def save_config(self, config):
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=4)
            
    def save_server_config(self, server_config):
        with open(self.server_file, 'w') as f:
            json.dump(server_config, f, indent=4)
            
    def save_invitations(self, invitations):
        with open(self.invitations_file, 'w') as f:
            json.dump(invitations, f, indent=4)
            
    def load_config(self):
        with open(self.config_file, 'r') as f:
            return json.load(f)
            
    def load_server_config(self):
        with open(self.server_file, 'r') as f:
            return json.load(f)
            
    def load_invitations(self):
        with open(self.invitations_file, 'r') as f:
            return json.load(f)
            
    def add_invitation(self, server_info):
        invitations = self.load_invitations()
        invitations.append(server_info)
        self.save_invitations(invitations)
        
    def remove_invitation(self, server_token):
        invitations = self.load_invitations()
        invitations = [inv for inv in invitations if inv['server_token'] != server_token]
        self.save_invitations(invitations)
        
    def get_invitation(self, server_token):
        invitations = self.load_invitations()
        for inv in invitations:
            if inv['server_token'] == server_token:
                return inv
        return None
        
    def set_github_token(self, token):
        config = self.load_config()
        config['github_token'] = token
        self.save_config(config)
        
    def get_github_token(self):
        config = self.load_config()
        return config.get('github_token', '')
        
    def set_server_mode(self, is_server, host='localhost', port=5000):
        server_config = self.load_server_config()
        server_config['is_server'] = is_server
        server_config['server_host'] = host
        server_config['server_port'] = port
        self.save_server_config(server_config)
        
    def get_server_info(self):
        return self.load_server_config()
        
    def generate_invitation_token(self):
        return secrets.token_hex(16) 