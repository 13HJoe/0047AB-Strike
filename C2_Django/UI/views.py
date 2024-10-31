from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
import requests

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
        return redirect('login_template')
    
    # GET all connections from FLASK manager

    return render(request, "UI/index.html", {
        "user":request.user.username
    })

def login_view(request):
    if request.user.is_authenticated:
         return redirect("index")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("index")
        else:
            return redirect("login_template")
        
    if request.method == "GET":
        return render(request, "UI/login.html")
    
    return HttpResponseForbidden("Invalid Method")

def logout_view(request):
     logout(request)
     return redirect("login_template")

def initialize_manager(request):
    if request.method == "POST":
        ip = request.POST["ip_addr"]
        port = request.POST["port"]
        flask_server = request.POST["flask_server"]
        flask_server+="/init"
        django_server = "http://127.0.0.1:8000/update_data"

        data = {"ip":ip,
                "port":port,
                "django_server":django_server}
        
        response = requests.get(url=flask_server, params=data)

        if response.status_code == 200:
            return HttpResponse("Initialized Manager")

    if request.method == "GET":
        return render(request, "UI/initialize_manager.html")
    
def update_data(request):
    if request.method == "POST":
        data = request.POST.items()
        # update DB