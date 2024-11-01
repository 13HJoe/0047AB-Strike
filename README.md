# 0047AB-Strike
## C2 Web-based Manager
- Django Application
    - [X] Auth
    - [X] UI
    - [X] Initialize MANAGER-flask 

    - [ ] Django Model ( create a model for each connection )
            src_ip, command_history

    - [ ] View connections
        - *On refresh* -> update *status* of each connection
        - *For each connection* -> send commands > view responses
            - select `mode` of interaction
                - `mode` -> Noisy TCP 
                - `mode` -> DNS Tunnelling
                - `mode` -> ICMP Tunnelling

- `MANAGER` instance (FLASK)
    - [X] func -> listen & create conn objects
    - [X] func -> sleep() and send POST periodically to Django 
    - [X] flask POST route ( for django to send commands to flask instance )
    - [X] func -> execute the commands sent by the django server
    - [X] platform() -> return metadata of compromised machine