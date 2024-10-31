from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def index(request):
    if not request.user.is_authenticated:
            return redirect('login_template')
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