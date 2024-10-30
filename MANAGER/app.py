from flask import Flask
from flask import request, make_response, render_template

from connection_manager import run_manager
import connection_manager

import threading
import time

app = Flask(__name__)

@app.route("/init", methods=["POST"])
def init():
    if request.method == "POST":
        ip = request.form.get("ip")
        port = int(request.form.get("port"))
        django_server = request.form.get("django-server")
        manager_thread = threading.Thread(target=run_manager, args=(ip, port, django_server),daemon=True)
        manager_thread.start()
        manager_thread.join()

        return make_response(render_template("init.html"), 200)

@app.route("/get_conn", methods=["GET"])
def get_conn():
    data = []
    for conn in connection_manager.ACTIVE_CONNECTIONS:
        data.append(str(conn.addr[0])+str(conn.machine_info))
    print(data)
    return render_template("data.html", data=data)

def run_flask():
    app.run(debug=True, use_reloader=False,host="127.0.0.1", port=5000)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    flask_thread.join()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        exit()

    
