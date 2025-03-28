from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_view, name="login_template"),
    path('logout/', views.logout_view, name="logout_template"),
    path('initialize_manager', views.initialize_manager, name="initialize_manager_template"),
    path('update_conn', views.update_conn, name="update_conn"),
    path('refresh_conn', views.refresh_conn, name="refresh_conn"),
    path('exec_hist', views.exec_hist, name="exec_hist"),
    path('exec_conn/<ip>', views.exec_conn, name="exec_conn"),
    #path('dns_tun', views.dns_tunnelled_data_handler, name="dns_tun"),
]