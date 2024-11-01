from flask import Flask
from flask import request, make_response, render_template, jsonify
from flask_cors import CORS

import connection_manager

import threading
import time
import sqlite3

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:8000/"])
manager_thread = None

@app.route("/init", methods=["GET"])
def init():
    if request.method == "GET":
        ip = request.args.get("ip")
        port = int(request.args.get("port"))
        django_server = request.args.get("django-server")
        manager_thread = threading.Thread(target=connection_manager.run_manager, args=(ip, port, django_server),daemon=True)
        manager_thread.start()
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

@app.route("/conn_execute", methods=["POST"])
def conn_execute():
    if request.method == "POST":
        ip = int(request.form.get("ip"))
        command = request.form.get("command")

        response = connection_manager.execute_command(id=ip, command=command)
        """        
        execute_command_thread = threading.Thread(target=connection_manager.execute_command, args=(connection_id, command))
        execute_command_thread.start()
        execute_command_thread.join()

        response = connection_manager.RESPONSE_DIRECTORY[connection_id]
        """
        return make_response(render_template("data.html", data=response), 200)

def run_flask():
    app.run(debug=True, use_reloader=False,host="127.0.0.1", port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    flask_thread.join()
    if manager_thread:
        manager_thread.join()