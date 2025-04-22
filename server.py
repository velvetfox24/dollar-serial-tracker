import socket
import threading
import json
import sqlite3
from database import Database
import os
import sys
import signal

class DollarTrackerServer:
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.db = Database()
        self.clients = {}
        
    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")
            
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"New connection from {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()
                
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.server_socket.close()
            
    def handle_client(self, client_socket, address):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                request = json.loads(data.decode())
                response = self.process_request(request)
                client_socket.send(json.dumps(response).encode())
                
        except Exception as e:
            print(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            if address in self.clients:
                del self.clients[address]
                
    def process_request(self, request):
        action = request.get('action')
        data = request.get('data', {})
        
        try:
            if action == 'login':
                user_id = self.db.verify_user(data['username'], data['password'])
                if user_id:
                    return {'success': True, 'user_id': user_id}
                return {'success': False, 'error': 'Invalid credentials'}
                
            elif action == 'create_user':
                success = self.db.create_user(data['username'], data['password'])
                return {'success': success}
                
            elif action == 'add_bill':
                success = self.db.add_bill(
                    face_value=data['face_value'],
                    serial_number=data['serial_number'],
                    user_id=data['user_id'],
                    printing_location=data.get('printing_location'),
                    series_year=data.get('series_year'),
                    is_star_note=data.get('is_star_note', False),
                    is_star_filled=data.get('is_star_filled', False),
                    image_path=data.get('image_path'),
                    estimated_value=data.get('estimated_value')
                )
                return {'success': success}
                
            elif action == 'search_bills':
                results = self.db.search_bills(data)
                return {'success': True, 'results': results}
                
            elif action == 'update_bill':
                success = self.db.update_bill(
                    data['serial_number'],
                    data['user_id'],
                    **data.get('updates', {})
                )
                return {'success': success}
                
            elif action == 'get_user_bills':
                results = self.db.get_user_bills(data['user_id'])
                return {'success': True, 'results': results}
                
            else:
                return {'success': False, 'error': 'Invalid action'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
            
def signal_handler(sig, frame):
    print("\nShutting down server...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    server = DollarTrackerServer()
    server.start() 