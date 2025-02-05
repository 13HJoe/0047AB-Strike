from flask import Flask
from flask import request, make_response, render_template, jsonify
from flask_cors import CORS

import connection_manager

import threading
import time
import sqlite3
import socket
from queue import Queue

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:8000/"])

@app.route("/init", methods=["GET"])
def init():
    if request.method == "GET":

        return make_response(render_template("init.html"), 200)
       
@app.route("/conn_all", methods=["GET"])
def conn_update():
    connection_manager.manage_connection_status()

    # Send connection data to the Django server
    data = {}
    for ip in connection_manager.ACTIVE_CONNECTIONS.keys():
        machine_inf = connection_manager.process_machine_info(connection_manager.ACTIVE_CONNECTIONS[ip].machine_info)
        machine_inf["Status"] = connection_manager.ACTIVE_CONNECTIONS[ip].status
        data[ip] = machine_inf

    return jsonify(data)

@app.route("/conn_execute", methods=["GET"])
def conn_execute():
    if request.method == "GET":
        ip = request.args.get("ip")
        command = request.args.get("command")

        response = connection_manager.execute_command(ip, command)


        return make_response(response.replace('>',' ').replace('<', ' '), 200)

def run_flask():
    app.run(debug=True, use_reloader=False,host="127.0.0.1", port=5000)

NUMBER_OF_THREADS = 3
JOB_NUMBERS = [1, 2, 3]
queue = Queue()

if __name__ == '__main__':    
    ip = socket.gethostname()
    port = 4444
    django_server = "http://127.0.0.1:8000"

    obj = connection_manager.Server(ip=ip, port=port, django_server=django_server)

    def create_workers():
        for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=work)
            t.daemon = True
            t.start()

    def work():
        while True:
            x = queue.get()
            if x == 1:
                run_flask()
            if x == 2:
                obj.manage_listen_and_add()
            if x == 3:
                obj.manage_update_connection_db()
    
    def create_jobs():
        for x in JOB_NUMBERS:
            queue.put(x)
        
        queue.join()

    create_workers()
    create_jobs()
    

    obj.socket_obj.close()
    