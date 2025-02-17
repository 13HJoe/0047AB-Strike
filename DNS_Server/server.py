import socket, glob, json, base64

# note: only serve requests it has zone files for, 
# don't serve requests for domain names not found in /zones
ZONE_DATA = {}

DATA_BUFFER = {}

class DNS_Handler:
    def __init__(self, data, client_address):
        self.data = data
        self.client_address = client_address

    def DNS_Tunnel(self):
        tunnelled_data = self.domain_name[0]
        raw_data = base64.b32decode(tunnelled_data)
        print(raw_data)
        if b'#FILE#' in raw_data:
            file_name = str(raw_data).split()[1].strip("'") 
            key = self.client_address[0]
            DATA_BUFFER[key] = [file_name, b'']
        elif b'#END#' in raw_data:
            file_name = DATA_BUFFER[self.client_address[0]][0]
            with open("downloads/"+file_name, 'wb') as obj:
                obj.write(DATA_BUFFER[self.client_address[0]][1])
            DATA_BUFFER.pop(self.client_address[0])
        else:
            DATA_BUFFER[self.client_address[0]][1] += raw_data
        
    # build -> used in HEADER, BODY, QUESTION
    def DNS_Get_Zone(self, domain_parts):
        global ZONE_DATA
        zone_name = '.'.join(domain_parts[1:]) # ignore tunnelled data in subdomain
        return ZONE_DATA[zone_name]

    def DNS_Get_Records(self):
        domain_parts, QTYPE = self.DNS_Get_Question()
        
        if QTYPE == b"\x00\x01":
            QTYPE = 'a'
        
        zone = self.DNS_Get_Zone(domain_parts)

        return (zone[QTYPE], QTYPE, domain_parts)


    # build -> HEADER
    def DNS_Get_Flags(self):
        temp_buf = self.data[2:4]
        byte_1 = bytes(temp_buf[:1])
        byte_2 = bytes(temp_buf[1:2])

        # QR - query(0) | response(1) 1 bit
        QR = '1'
        # OPCODE - four bit field that specifies kind of query in 
        # this message
        # 0 - standard query
        # 1 - inverse query
        # 2 - server status request
        # (3,15) - reserved for future use
        OPCODE = '' 
        for bit in range(1, 5):
            OPCODE += str(ord(byte_1)&(1<<bit)) # check for every bit and 
                                                # modifying OPCODE accordingly
        # Authoritative Answer
        AA = '1'
        # TrunCation - specifies that this message was 
        # truncated due to length greater than that 
        # permitted on the transmission channel
        TC = '0' 
        RD = '0' # Recursion Desired
        RA = '0' # Recursion Available
        Z = '000' # Reserved for future use
        # RCODE -  Response code
        # 0 - no error
        # 1 - format error
        # 2 - server failure
        # 3 - name error - this code signifies that the domain name referenced in the query does not exist
        # 4 - not implemented - name server does not support the requested kind of query
        # 5 - refused - name server refuses to perform the specified operation for policy reasons.
        RCODE = '0000' 

        response_byte_1 =  int(QR+OPCODE+AA+TC+RD, 2).to_bytes(1, byteorder='big')
        response_byte_2 = int(RA+Z+RCODE, 2).to_bytes(1, byteorder='big')

        return response_byte_1 + response_byte_2

    def DNS_Get_Question(self):
        temp_buf = self.data[12:]
        state = 0
        expected_length = 0
        domain_string = ''
        x = 0
        y = 0
        domain_parts = []
        for byte in temp_buf:
            if state == 1:
                if byte!=0:
                    domain_string += chr(byte) # each character in domain -> 1 byte
                x += 1
                if x == expected_length:
                    domain_parts.append(domain_string)
                    domain_string = ''
                    state, x = 0, 0
                if byte == 0:
                    domain_parts.append(domain_string)
                    break
            else:
                state = 1
                expected_length  = byte
            y += 1

        QTYPE = temp_buf[y:y+2]
        return (domain_parts, QTYPE)

    # build -> QUESTION
    def DNS_Build_Question(self):
        qbytes = b''
        # build QNAME
        for part in self.domain_name:
            length = len(part)
            qbytes += bytes([length])
            for char in part:
                qbytes += ord(char).to_bytes(1, byteorder='big')
        # build QTYPE
        if self.rectype == 'a':
            qbytes += (1).to_bytes(2, byteorder='big')
        # build QCLASS
        qbytes += (1).to_bytes(2, byteorder='big')
        return qbytes
    
    # build -> BODY
    def DNS_Record_to_Bytes(self, recttl, recval):
        '''
                                        1  1  1  1  1  1
          0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                                               |
        /                                               /
        /                      NAME                     /
        |                                               |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                      TYPE                     |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                     CLASS                     |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                      TTL                      |
        |                                               |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
        |                   RDLENGTH                    |
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--|
        /                     RDATA                     /
        /                                               /
        +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

        '''
        rbytes = b'\xc0\x0c'
        if self.rectype == 'a':
            rbytes += bytes([0]) + bytes([1])
        rbytes += bytes([0]) + bytes([1])
        rbytes += int(recttl).to_bytes(4, byteorder='big')
        if self.rectype == 'a':
            rbytes += bytes([0]) + bytes([4])
            for part in recval.split('.'):
                rbytes += bytes([int(part)])
        return rbytes


    '''
    https://www.ietf.org/rfc/rfc1035.txt

                                    1  1  1  1  1  1
      0  1  2  3  4  5  6  7  8  9  0  1  2  3  4  5
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                      ID                       | ------> TID 2 bytes / 16 bits
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |QR|   Opcode  |AA|TC|RD|RA|   Z    |   RCODE   | ------> FLAGS 2 bytes / 16 bits
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    QDCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ANCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    NSCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
    |                    ARCOUNT                    |
    +--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+

    '''
    def DNS_Generate_Response(self):
        # Transaction ID - the client can match the received answer 
        # with the question that it sent
        Transaction_ID = self.data[0:2] # first 2 bytes

        flags = self.DNS_Get_Flags() # next 2 bytes

        # Question Count
        QDCOUNT = b'\x00\x01' # Usually 1

        self.records, self.rectype, self.domain_name = self.DNS_Get_Records()
        self.DNS_Tunnel()
        
        # Answer Count
        ANCOUNT = len(self.records).to_bytes(2, byteorder='big')

        # Nameserver Count
        NSCOUNT = (0).to_bytes(2, byteorder='big')

        # Additional Count
        ARCOUNT = (0).to_bytes(2, byteorder='big')

        DNS_HEADER = Transaction_ID + flags + QDCOUNT + ANCOUNT + NSCOUNT + ARCOUNT

        DNS_QUESTION = self.DNS_Build_Question()

        DNS_BODY = b''
        for record in self.records:
            DNS_BODY += self.DNS_Record_to_Bytes(record['ttl'], record['value'])
        
        return DNS_HEADER + DNS_QUESTION + DNS_BODY

class DNS_Server:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT
        global ZONE_DATA
        ZONE_DATA = self.DNS_Load_Zones()
    
    def DNS_Load_Zones(self):
        json_zone = {}
        zone_file_names = glob.glob("zones/*.zone")

        for zone_file in zone_file_names:
            with open(zone_file) as obj:
                data = json.load(obj) # Deserialize fp to a Python json object
                zone_name = data['$origin']
                json_zone[zone_name] = data
        
        return json_zone
        
    def run(self):
        print("[+] DNS Server running")
        self.socket_object = socket.socket(socket.AF_INET, # IPv4
                                      socket.SOCK_DGRAM) # UDP
        self.socket_object.bind((self.IP, self.PORT))
        while True:
            data, client_address = self.socket_object.recvfrom(4096)
            handler_obj = DNS_Handler(data=data, 
                                      client_address=client_address)
            response = handler_obj.DNS_Generate_Response()
            self.socket_object.sendto(response, client_address)


dns_server_obj = DNS_Server('10.136.66.98', 53)
dns_server_obj.run()