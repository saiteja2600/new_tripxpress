from django.db import models
from django.core.validators import RegexValidator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
import string
import secrets
import string
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from multiselectfield import MultiSelectField
# Create your models here.


class Country(models.Model):

    name = models.CharField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.country.name}"

class City(models.Model):
    name = models.CharField(max_length=100, unique=True, blank=True)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}, {self.state.name}"
class Branch(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name

class admin_Register(models.Model):
    admin_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE,)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    password = models.CharField(max_length=100)
    confirm_password = models.CharField(max_length=100)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def Countries(self):
        return self.country.name
    
    def States(self):
        return self.state.name
    
    def Cities(self):
        return self.city.name
    
    def Branches(self):
        return self.branch.name
    

    def __str__(self):
        return self.first_name + " " + self.last_name

class Driver(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
    ]
    VEHICLE_LINK_CHOICES = [
        ('own', 'Own Vehicle'),
        ('company', 'Company Vehicle'),
       
    ]
    
    VEHICLE_DRIVER_TYPE=[
        ('2','2 wheeler'),
        ('4','4 wheeler')
    ]

    driver_id = models.AutoField(primary_key=True)
    admin = models.ForeignKey(admin_Register, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to='driver_images/', blank=True, null=True)
    vehicle_link = models.CharField(max_length=10, choices=VEHICLE_LINK_CHOICES, default='none')
    driving_licence = models.CharField(max_length=100, blank=True, null=True)
    vehicle_driver_type = MultiSelectField(choices=VEHICLE_DRIVER_TYPE, max_length=10, blank=True)
    company_email = models.EmailField(unique=True, blank=True)
    password = models.CharField(max_length=100, blank=True)
    joined_at = models.DateField(blank=True, null=True) 
    is_active = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')

    def save(self, *args, **kwargs):
        if self.date_of_birth:
            today = date.today()
            self.age = (
                today.year - self.date_of_birth.year -
                ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
            )

        # Auto-generate company email if not provided
        if self._state.adding and self.first_name and self.last_name:
            if not self.company_email:
                base_email_name = (self.first_name + self.last_name).replace(' ', '.')
                company_domain = "tripxpress.com"
                email_candidate = f"{base_email_name}@{company_domain}"
                counter = 1
                while Driver.objects.filter(company_email=email_candidate).exists():
                    email_candidate = f"{base_email_name}{counter}@{company_domain}"
                    counter += 1
                self.company_email = email_candidate

        super().save(*args, **kwargs)
    def clean(self):
        if self.vehicle_link == 'own':
            if not self.vehicles.filter(ownership = 'driver').exists():
                raise ValidationError("You selected 'Own Vehicle' but no driver-owned vehicle is registered.")
        elif self.vehicle_link == 'company':
            if not self.vehicles.filter(ownership = 'company').exists():
                raise ValidationError("You selected 'Company Vehicle' but no company-owned vehicle is registered.")

                

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name else self.email

class company_vehicle(models.Model):
    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Under Maintenance', 'Under Maintenance'),
        ('Inactive', 'Inactive'),
        ('Reserved', 'Reserved'),
    ]

    admin = models.ForeignKey(admin_Register, on_delete=models.CASCADE)
    vehicle_id = models.AutoField(primary_key=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True, blank=True)

    vehicle_name = models.CharField(max_length=100)
    vehicle_model = models.CharField(max_length=100)
    vehicle_number = models.CharField(max_length=20)
    vehicle_color = models.CharField(max_length=50)
    vehicle_year = models.CharField(max_length=4, blank=True, null=True)
    vehicle_fuel = models.CharField(max_length=50)
    vehicle_mileage = models.CharField(max_length=10, blank=True, null=True)
    vehicle_transmission = models.CharField(max_length=50)
    vehicle_engine = models.CharField(max_length=50)
    vehicle_seats = models.CharField(max_length=50, blank=True, null=True)
    vehicle_doors = models.CharField(max_length=50, blank=True, null=True)

    vehicle_description = models.TextField()
    vehicle_type = models.CharField(max_length=50)
    vehicle_image = models.ImageField(upload_to='vehicle_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    # Car-specific fields
    vehicle_airbags = models.CharField(max_length=10, blank=True, null=True)

    # Bike-specific fields
    vehicle_brake_type = models.CharField(max_length=50, null=True, blank=True)
    vehicle_start_type = models.CharField(max_length=50, null=True, blank=True)
    vehicle_weight = models.CharField(max_length=50, null=True, blank=True)

    # Tempo-specific fields
    tempo_seats = models.CharField(max_length=50, null=True, blank=True)
    tempo_doors = models.CharField(max_length=50, null=True, blank=True)
    vehicle_capacity = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle_name} - {self.vehicle_number}"
