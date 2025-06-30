from django.contrib import admin 

from admin_panel.models import admin_Register,Branch,City,Country,State,Driver,company_vehicle

# Register your models here.
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


class StateAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')

class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'state')

class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'city')


class adminRegister(admin.ModelAdmin):
    list_display = ('admin_id','first_name', 'last_name', 'email', 'phone_number', 'country', 'state', 'city')
    search_fields = ('first_name', 'last_name', 'email', 'phone_number')
    list_filter = ('first_name', 'last_name', 'email',)
    
class DriverAdmin(admin.ModelAdmin):
    list_display = ('driver_id','first_name', 'last_name','date_of_birth', 'age','email', 'phone_number', 'country', 'state', 'city', 'status')
    search_fields = ('first_name', 'last_name', 'email',)
    list_filter = ('first_name', 'last_name', 'email',)
    
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('vehicle_id','vehicle_name', 'vehicle_model','vehicle_number', 'vehicle_color', 'vehicle_year', 'vehicle_fuel', 'vehicle_mileage', 'vehicle_transmission', 'vehicle_engine', 'vehicle_seats', 'vehicle_doors', 'vehicle_description', 'vehicle_type')
    search_fields = ('vehicle_name', 'vehicle_model', 'vehicle_number',)
    list_filter = ('vehicle_name', 'vehicle_model', 'vehicle_number',)
    

admin.site.register(admin_Register, adminRegister)
admin.site.register(Driver, DriverAdmin)
admin.site.register(company_vehicle, VehicleAdmin)
admin.site.register(Branch)
admin.site.register(City)
admin.site.register(Country)
admin.site.register(State)
