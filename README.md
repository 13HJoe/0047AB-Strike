﻿# 0047AB-Strike

C2 
- [ ] Django Model ( create a model for each connection )
      src_ip, src_port, device_type, device_type, os_type, host_name
    
- `MANAGER` instance (FLASK)
    - [X] func -> listen & create conn objects
    - [X] func -> sleep() and send POST periodically to Django 
    - [X] flask POST route ( for django to send commands to flask instance )
    - [X] func -> execute the commands sent by the django server
