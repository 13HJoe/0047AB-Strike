import socket
import datetime

host = '192.168.1.37'
port = 4444

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((host, port))

resp = ("Windows ->"+str(datetime.datetime.now()))
clientsocket.send(resp.encode('ascii'))

clientsocket.close()