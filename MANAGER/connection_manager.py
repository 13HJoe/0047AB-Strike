import socket
import threading
import time
import json
import base64

class Con_Stor():
    def __init__(self, client_socket_object, addr):
        self.client_socket_object = client_socket_object
        self.addr = addr

    def json_send(self, data):
        for i in range(len(data)):
            word = data[i]
            if not isinstance(word, str):
                data[i] = word.decode('utf-8')
        
        json_data = json.dumps(data).encode('utf-8')
        self.client_socket_object.send(data)

    def json_receive(self, data):
        json_data = "" 
        while True:
            try:
                page = self.client_socket_object.recv(1024)
                json_data += page.decode('utf-8')
                return json.loads(json_data)
            except:
                continue

    def read_file(self, path):
        try:
            with open(path, 'rb') as file_obj:
                return base64.b64encode(file_obj.read())
        except:
            return "[+] ERROR - Error opening file"
    def write_file(self, name, content):
        try:
            with open(name, 'wb') as file_obj:
                file_obj.write(base64.b64decode(content))
                return "[+] File downloaded successfully"
        except:
            return "[+] ERROR - Error during creating a file"    
            
ACTIVE_CONNECTIONS = []

class Server:
    def __init__(self, ip, port):
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_obj.bind((ip, port))
        
