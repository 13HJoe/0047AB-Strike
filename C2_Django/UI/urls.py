from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login_template"),
    path('logout/', views.logout_view, name="logout_template"),
    path('initialize_manager', views.initialize_manager, name="initialize_manager_template"),
    path('update_data', views.update_data, name="update_data_template")
]