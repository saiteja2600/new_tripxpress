from django.urls import path
from driver_panel import views

urlpatterns = [
    path('', views.driver_login, name='driver_login'),
    path('logout/', views.driver_logout, name='driver_logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('Dashbord/', views.Dashbord, name='driver_dashbord'),
]