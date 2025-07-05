from django.urls import path
from admin_panel import views

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path('register/', views.admin_register, name='admin_register'),
    path('profile/', views.admin_profile, name='admin_profile'),
    # Dasboard
    path('Dashbord/', views.admin_dashbord, name='admin_dashbord'),
    #Driver
    path('Driver/', views.admin_driver, name='admin_drivers'),
    path('Driver/delete/<int:driver_id>/', views.admin_driver_delete, name='admin_driver_delete'),
    path('admin/drivers/delete-multiple/', views.admin_delete_multiple_drivers, name='admin_delete_multiple_drivers'),
    path('Driver/edit/<int:driver_id>/', views.admin_driver_edit, name='admin_driver_edit'),
    path('Driver/export/', views.admin_driver_export, name='admin_driver_export'),
    path('Driver/approver_leaves', views.driver_approver_leaves, name='driver_approver_leaves'),
    #Vehicle
    path('Vehicle/', views.admin_vehicle, name='admin_vehicles'),
    path('Vehicle/edit/<int:vehicle_id>/', views.admin_vehicle_edit, name='admin_vehicle_edit'),
    path('Vehicle/delete/<int:vehicle_id>/', views.admin_vehicle_delete, name='admin_vehicle_delete'),
    path('admin/vehicles/delete-multiple/', views.admin_delete_multiple_vehicles, name='admin_delete_multiple_vehicles'),
    
    #loactions
    path('all_locations/', views.all_locations, name='all_locations'),
    path('routes/', views.routes, name='routes'),
   
    # Dynamics Branches
    path('get_states/', views.get_states, name='get_states'),
    path('get_cities/', views.get_cities, name='get_cities'),
    path('get_branches/', views.get_branches, name='get_branches'),
]
