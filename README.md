# 0047AB-Strike
## C2 Web-based Manager
- Django Application
    - [X] Auth
    - [X] UI
    - [X] Initialize MANAGER-flask 


    - [X] Django Models -> Connection Data & Command History
        [X] UI All Connections -> get from DB
        [X] Update view -> write to DB (every 10 seconds)
        [X] Refresh UI -> force write to DB [*On refresh* -> update *status* of each connection]



    - *For each connection* -> send commands > view responses
        - select `mode` of interaction
            - `mode` -> Noisy TCP [X]
            - `mode` -> DNS Tunnelling
            - `mode` -> ICMP Tunnelling

- `MANAGER` instance (FLASK)
    - [X] func -> listen & create conn objects
    - [X] func -> sleep() and send POST periodically to Django 
    - [X] flask POST route ( for django to send commands to flask instance )
    - [X] func -> execute the commands sent by the django server
    - [X] platform() -> return metadata of compromised machine