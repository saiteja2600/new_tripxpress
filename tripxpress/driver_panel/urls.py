from django.urls import path
from driver_panel import views

urlpatterns = [
    path('', views.driver_login, name='driver_login'),
    path('logout/', views.driver_logout, name='driver_logout'),
    path('change_password/', views.change_password, name='change_password'),
    path('profile/', views.driver_profile, name='driver_profile'),
    path('Dashbord/', views.Dashbord, name='driver_dashbord'),
    
    # Vehicle
    path('vehicle_information/', views.vehicle_information, name='vehicle_information'),
    path('vehicle_maintenance/', views.vehicle_maintenance, name='vehicle_maintenance'),
   path('Driver/vehicle_maintenance/delete/<int:service_id>/', views.vehicle_maintenance_delete, name='delete_maintenance'),
   path('Driver/vehicle_maintenance/edit/<int:service_id>/', views.vehicle_maintenance_edit, name='edit_maintenance'),
   path('Driver/profile_update/', views.driver_profile_update, name='driver_profile_update'),
   
   #
   path('vehicles/', views.vehicles, name='vehicles'),
   
   
   #Leaves
   path('driver_leaves/', views.driver_leaves, name='driver_leaves')

]


