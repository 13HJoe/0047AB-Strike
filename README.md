# 0047AB-Strike

**note**: primitive implementation of a C2 server; only tested on a local net.

![alt text](/assets-readme/image.png)

### Instructions
1. Start `C2_Django`
    ```python
    python manage.py runserver
    ```
2. Start `DNS_Server` (modify IP)
    ```python
    python server.py
    ```
3. Start `TCP_Flask`
    ```python
    python app.py
    ```
3. Execute `backdoor.py` on target test machine (change C2/DNS server IP)