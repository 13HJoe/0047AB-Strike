# 0047AB-Strike

**note**: primitive implementation of a C2 server; only tested on a local network; all 3 servers need to be run simultaneously.

![alt text](/assets-readme/image.png)

### Setup
1. Delete `sqlite3.db`; Create a new `django superuser`; use the same creds. for the Django app
   ```python
   python manage.py createsuperuser
   ```
2. Start `C2_Django`;
    ```python
    python manage.py runserver
    ```
3. Start `DNS_Server` (modify IP)
    ```python
    python server.py
    ```
4. Start `TCP_Flask`
    ```python
    python app.py
    ```
5. Execute `backdoor.py` on target test machine (change C2/DNS server IP)