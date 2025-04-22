import socket
import json
import os
import sys

class DollarTrackerClient:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.socket = None
        self.user_id = None
        
    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            
    def send_request(self, action, data=None):
        if not self.socket:
            if not self.connect():
                return {'success': False, 'error': 'Could not connect to server'}
                
        try:
            request = {'action': action, 'data': data or {}}
            self.socket.send(json.dumps(request).encode())
            
            response = self.socket.recv(4096)
            return json.loads(response.decode())
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
    def login(self, username, password):
        response = self.send_request('login', {
            'username': username,
            'password': password
        })
        
        if response['success']:
            self.user_id = response['user_id']
        return response
        
    def create_user(self, username, password):
        return self.send_request('create_user', {
            'username': username,
            'password': password
        })
        
    def add_bill(self, **bill_data):
        if not self.user_id:
            return {'success': False, 'error': 'Not logged in'}
            
        bill_data['user_id'] = self.user_id
        return self.send_request('add_bill', bill_data)
        
    def search_bills(self, criteria=None):
        if not self.user_id:
            return {'success': False, 'error': 'Not logged in'}
            
        return self.send_request('search_bills', criteria or {})
        
    def update_bill(self, serial_number, **updates):
        if not self.user_id:
            return {'success': False, 'error': 'Not logged in'}
            
        return self.send_request('update_bill', {
            'serial_number': serial_number,
            'user_id': self.user_id,
            'updates': updates
        })
        
    def get_user_bills(self):
        if not self.user_id:
            return {'success': False, 'error': 'Not logged in'}
            
        return self.send_request('get_user_bills', {'user_id': self.user_id}) 