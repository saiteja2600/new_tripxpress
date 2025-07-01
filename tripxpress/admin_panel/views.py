from django.shortcuts import render, redirect
from django.contrib import messages
from admin_panel.models import admin_Register, Branch, City, Country, State,Driver,company_vehicle
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.core.files.storage import default_storage
from admin_panel.utils.driver_utils import generate_random_password,generate_unique_company_email, calculate_age,send_driver_credentials_email
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from collections import defaultdict
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # <--- Add this line before importing pyplot
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import os
import csv
import requests
from django.core.files.base import ContentFile


# ========== AJAX: Dynamic Dropdown Handlers ==========

def get_states(request):
    country_id = request.GET.get('country_id')
    states = State.objects.filter(country_id=country_id).values('id', 'name')
    return JsonResponse(list(states), safe=False)

def get_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse(list(cities), safe=False)

def get_branches(request):
    city_id = request.GET.get('city_id')
    branches = Branch.objects.filter(city_id=city_id).values('id', 'name')
    return JsonResponse(list(branches), safe=False)


# ========== ADMIN LOGIN ==========

def admin_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        try:
            admin = admin_Register.objects.get(email=email)
            if check_password(password, admin.password):
                if admin.is_active:
                    # Set session
                    request.session['admin_id'] = admin.admin_id
                    request.session['admin_email'] = admin.email
                    request.session['admin_name'] = f"{admin.first_name[0]}{admin.last_name[0]}".upper()
                    request.session['admin_phone'] = admin.phone_number
                    request.session['admin_country'] = admin.country.name
                    request.session['admin_state'] = admin.state.name
                    request.session['admin_city'] = admin.city.name
                    request.session['admin_branch'] = admin.branch.name

                    # Optional: Profile image
                    if admin.profile_image:
                        request.session['admin_profile'] = admin.profile_image.url

                    # Remember me logic
                    request.session.set_expiry(60 * 60 * 24 * 7 if remember else 0)

                    messages.success(request, "Login successful.")
                    return redirect('admin_dashbord')
                else:
                    messages.error(request, "Account is not active.")
            else:
                messages.error(request, "Invalid password.")
        except admin_Register.DoesNotExist:
            messages.error(request, "Email not found.")

    return render(request, 'admin_panel/admin_login.html')


# ========== ADMIN LOGOUT ==========

def admin_logout(request):
    request.session.flush()
    return redirect('admin_login')


# ========== ADMIN PROFILE ==========

@never_cache
def admin_profile(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    try:
        admin = admin_Register.objects.get(admin_id=admin_id)

        if request.method == 'POST':
            if 'profile_image' in request.FILES:
                admin.profile_image = request.FILES['profile_image']
                admin.save()
                request.session['admin_profile'] = admin.profile_image.url
                messages.success(request, 'Profile image updated successfully!')
            else:
                messages.warning(request, 'No image selected.')

        return render(request, 'admin_panel/admin_profile.html', {'admin': admin})

    except admin_Register.DoesNotExist:
        messages.error(request, 'Admin not found.')
        return redirect('admin_login')


# ========== ADMIN REGISTER ==========

def admin_register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        country_id = request.POST.get('country')
        state_id = request.POST.get('state')
        city_id = request.POST.get('city')
        branch_id = request.POST.get('branch')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        is_active = request.POST.get('is_active') == 'agree'

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('admin_register')

        if admin_Register.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('admin_register')

        if admin_Register.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already exists.')
            return redirect('admin_register')

        try:
            country = Country.objects.get(id=country_id)
            state = State.objects.get(id=state_id)
            city = City.objects.get(id=city_id)
            branch = Branch.objects.get(id=branch_id)

            admin_Register.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                country=country,
                state=state,
                city=city,
                branch=branch,
                password=make_password(password),
                confirm_password=make_password(confirm_password),
                is_active=is_active
            )
            messages.success(request, 'Registration successful.')
            return redirect('admin_login')

        except (Country.DoesNotExist, State.DoesNotExist, City.DoesNotExist, Branch.DoesNotExist):
            messages.error(request, 'Invalid location selection.')
            return redirect('admin_register')

    context = {
        "country": Country.objects.all(),
        "state": State.objects.all(),
        "city": City.objects.all(),
        "branch": Branch.objects.all()
    }
    return render(request, 'admin_panel/admin_register.html', context)


# ========== ADMIN DASHBOARD ==========
@never_cache
def admin_dashbord(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    admin = admin_Register.objects.get(admin_id=request.session['admin_id'])
    drivers = Driver.objects.filter(admin=admin).values('joined_at', 'vehicle_link')

    from collections import defaultdict

    year_ownership_map = defaultdict(lambda: {'own': 0, 'company': 0})
    all_years = set()

    for d in drivers:
        if d['joined_at']:
            year = d['joined_at'].year
            all_years.add(year)
            if d['vehicle_link'] in ['own', 'company']:
                year_ownership_map[year][d['vehicle_link']] += 1

    sorted_years = sorted(all_years)
    own_data = [year_ownership_map[year]['own'] for year in sorted_years]
    company_data = [year_ownership_map[year]['company'] for year in sorted_years]

    context = {
        'years': json.dumps(sorted_years),
        'counts': json.dumps(own_data),
        'total_drivers': Driver.objects.filter(admin=admin).count(),
        'total_company_vehicles': company_vehicle.objects.filter(driver__vehicle_link='company', admin=admin).count(),

        'ownership_chart': {
            'years': sorted_years,
            'own': own_data,
            'company': company_data,
        }
    }

    return render(request, 'admin_panel/admin_dashbord.html', context)

#=====ADMIN DRIVER =======

@never_cache
def admin_driver(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    admin_id = request.session['admin_id']

    try:
        admin = admin_Register.objects.get(admin_id=admin_id)

        if request.method == 'POST':
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            dob_str = request.POST.get('date_of_birth')
            date_of_birth = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
            phone_number = request.POST.get('phone_number')
            vehicle_link = request.POST.get('vehicle_link')
            country_id = request.POST.get('country')
            state_id = request.POST.get('state')
            city_id = request.POST.get('city')
            joined_at_str = request.POST.get('joined_at')
            joined_at = datetime.strptime(joined_at_str, "%Y-%m-%d").date() if joined_at_str else None
            driving_licence = request.POST.get('driving_licence')
            vehicle_driver_type = request.POST.getlist('vehicle_driver_type[]')


            # Validation
            if Driver.objects.filter(email=email).exists():
                messages.error(request, "Email already exists.")
                return redirect('admin_drivers')
            elif Driver.objects.filter(phone_number=phone_number).exists():
                messages.error(request, "Phone number already exists.")
                return redirect('admin_drivers')
            elif Driver.objects.filter(first_name=first_name, last_name=last_name).exists():
                messages.error(request, "Driver already exists.")
                return redirect('admin_drivers')

            try:
                # Generate credentials and data
                raw_password = generate_random_password()
                hashed_password = make_password(raw_password)
                company_email = generate_unique_company_email(first_name, last_name)
                age = calculate_age(date_of_birth)

                # Save driver
                driver = Driver.objects.create(
                    admin=admin,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    date_of_birth=date_of_birth,
                    age=age,
                    phone_number=phone_number,
                    vehicle_link=vehicle_link,
                    country_id=country_id,
                    state_id=state_id,
                    city_id=city_id,
                    password=hashed_password,
                    company_email=company_email,
                    joined_at=joined_at,
                    driving_licence=driving_licence,
                    vehicle_driver_type=vehicle_driver_type
                )

                # Send email
                send_driver_credentials_email(first_name, last_name, email, company_email, raw_password, joined_at)

                messages.success(request, "Driver added successfully.")
                return redirect('admin_drivers')
            except Exception as e:
                messages.error(request, f"Error while adding driver: {str(e)}")
                return redirect('admin_drivers')

    except admin_Register.DoesNotExist:
        messages.error(request, "Admin not found.")
        return redirect('admin_login')

    countries = Country.objects.all()
    states = State.objects.all()
    cities = City.objects.all()
    drivers = Driver.objects.filter(admin=admin).order_by('-driver_id')

    context = {
        'countries': countries,
        'states': states,
        'cities': cities,
        'drivers': drivers
    }

    return render(request, 'admin_panel/admin_driver.html', context)


@never_cache
def admin_driver_delete(request, driver_id):
    try:
        driver = Driver.objects.get(driver_id=driver_id)
        driver.delete()
        messages.success(request, "Driver deleted successfully.")
    except Driver.DoesNotExist:
        messages.error(request, "Driver not found.")
    return redirect('admin_drivers')

@never_cache
def admin_delete_multiple_drivers(request):
    ids = request.POST.get("selected_ids")
    if ids:
        driver_ids = ids.split(",")
        Driver.objects.filter(driver_id__in=driver_ids).delete()
        messages.success(request, "Selected drivers deleted successfully.")
    else:
        messages.error(request, "No drivers selected.")
    return redirect('admin_drivers')
@never_cache
def admin_driver_edit(request, driver_id):
    if request.method == 'POST':
        first_name = request.POST.get('edit_first_name')
        last_name = request.POST.get('edit_last_name')
        email = request.POST.get('edit_email')
        dob_str = request.POST.get('edit_date_of_birth')
        country_id = request.POST.get('edit_country')
        state_id = request.POST.get('edit_state')
        city_id = request.POST.get('edit_city')
        phone_number = request.POST.get('edit_phone_number')
        vehicle_link = request.POST.get('edit_vehicle_link')
        joined_at_str = request.POST.get('edit_joined_at')
        joined_at = datetime.strptime(joined_at_str, "%Y-%m-%d").date() if joined_at_str else None
        driving_licence = request.POST.get('edit_driving_licence')
        vehicle_driver_type = request.POST.getlist('edit_vehicle_driver_type[]')


        try:
            driver = Driver.objects.get(driver_id=driver_id)
            driver.first_name = first_name
            driver.last_name = last_name
            driver.email = email
            driver.date_of_birth = datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else None
            driver.phone_number = phone_number
            driver.vehicle_link = vehicle_link
            driver.country_id = country_id
            driver.state_id = state_id
            driver.city_id = city_id
            driver.joined_at = joined_at
            driver.driving_licence = driving_licence
            driver.vehicle_driver_type = vehicle_driver_type
            driver.save()
            messages.success(request, "Driver updated successfully.")
            return redirect('admin_drivers')
        except Exception as e:
            messages.error(request, f"Error while updating driver: {str(e)}")
            return redirect('admin_drivers')
   
@never_cache
def admin_driver_export(request):
    if request.method == 'POST':
        files = request.FILES.getlist('csv_files')
        MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5 GB in bytes

        admin_id = request.session.get('admin_id')
        if not admin_id:
            messages.error(request, 'Admin session not found.')
            return redirect('admin_login')

        try:
            admin = admin_Register.objects.get(admin_id=admin_id)
        except admin_Register.DoesNotExist:
            messages.error(request, 'Admin not found.')
            return redirect('admin_login')

        for csv_file in files:
            if not csv_file.name.endswith('.csv'):
                messages.error(request, f"{csv_file.name}: Invalid file format. Only CSV files allowed.")
                continue

            if csv_file.size > MAX_FILE_SIZE:
                messages.error(request, f"{csv_file.name}: File too large. Maximum allowed size is 1.5GB.")
                continue

            try:
                file_data = csv_file.read().decode('utf-8').splitlines()
                csv_reader = csv.DictReader(file_data)

                for row in csv_reader:
                    try:
                        email = row['email'].strip()
                        phone_number = row['phone_number'].strip()
                        vehicle_link = row['vehicle_link'].strip()
                        country_name = row['country'].strip()
                        state_name = row['state'].strip()
                        city_name = row['city'].strip()
                        dob = datetime.strptime(row['date_of_birth'].strip(), "%Y-%m-%d").date() if row['date_of_birth'] else None
                        joined_at = datetime.strptime(row['joined_at'].strip(), "%Y-%m-%d").date() if row['joined_at'] else None
                        driving_licence = row['driving_licence'].strip()
                        # Handling vehicle_driver_type (e.g., "2,4")
                        raw_types = row['vehicle_driver_type'].strip()
                        type_list = [x.strip() for x in raw_types.split(',') if x.strip()]

                        # If your model expects a string, rejoin
                        vehicle_driver_type = ",".join(type_list)
                       
                        if Driver.objects.filter(email=email).exists() or Driver.objects.filter(phone_number=phone_number).exists():
                            continue

                        country = Country.objects.get(name__iexact=country_name)
                        state = State.objects.get(name__iexact=state_name, country=country)
                        city = City.objects.get(name__iexact=city_name, state=state)

                        Driver.objects.create(
                            admin=admin,
                            first_name=row['first_name'].strip(),
                            last_name=row['last_name'].strip(),
                            email=email,
                            phone_number=phone_number,
                            vehicle_link=vehicle_link,
                            date_of_birth=dob,
                            country=country,
                            state=state,
                            city=city,
                            joined_at=joined_at,
                            driving_licence=driving_licence,
                            vehicle_driver_type=vehicle_driver_type
                        )
                    except ObjectDoesNotExist:
                        messages.warning(request, f"Location not found in file {csv_file.name} for entry: {row}")
                    except Exception as e:
                        messages.error(request, f"Error importing row in file {csv_file.name}: {str(e)}")

            except Exception as e:
                messages.error(request, f"Error reading file {csv_file.name}: {str(e)}")

        messages.success(request, "CSV file(s) processed successfully.")
        return redirect('admin_drivers')

    return redirect('admin_drivers')
@never_cache
def admin_vehicle(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')
    drivers = Driver.objects.filter(vehicle_link='company')
    admin_id = request.session['admin_id']
    try:
        admin = admin_Register.objects.get(admin_id=admin_id)
        if request.method == 'POST':
            driver_id = request.POST.get('driver')
            driver = Driver.objects.get(driver_id=driver_id)
            vehicle_name = request.POST.get('vehicle_name')
            vehicle_model = request.POST.get('vehicle_model')
            vehicle_number = request.POST.get('vehicle_number')
            vehicle_color = request.POST.get('vehicle_color')
            vehicle_year = request.POST.get('vehicle_year')
            vehicle_fuel = request.POST.get('vehicle_fuel')
            vehicle_mileage = request.POST.get('vehicle_mileage')
            vehicle_transmission = request.POST.get('vehicle_transmission')
            vehicle_engine = request.POST.get('vehicle_engine')
            vehicle_seats = request.POST.get('vehicle_seats')
            vehicle_doors = request.POST.get('vehicle_doors')
            vehicle_description = request.POST.get('vehicle_description')
            vehicle_type = request.POST.get('vehicle_type')
            vehicle_image = request.FILES.get('vehicle_image')
            vehicle_airbags = request.POST.get('vehicle_airbags')
            vehicle_brake_type= request.POST.get('vehicle_brake_type')
            vehicle_start_type= request.POST.get('vehicle_start_type')
            vehicle_weight= request.POST.get('vehicle_weight')
            tempo_seats = request.POST.get('tempo_seats')
            tempo_doors = request.POST.get('tempo_doors')
            vehicle_capacity = request.POST.get('vehicle_capacity')

            

            if company_vehicle.objects.filter(vehicle_number=vehicle_number).exists():
                messages.error(request, "Vehicle number already exists.")
                return redirect('admin_vehicles')
            if company_vehicle.objects.filter(driver__first_name=driver.first_name, driver__last_name=driver.last_name).exists():
                messages.error(request, "Vehicle for this driver already exists.")
                return redirect('admin_vehicles')
            if company_vehicle.objects.filter(vehicle_engine=vehicle_engine).exists():
                messages.error(request, "Vehicle engine already exists.")
                return redirect('admin_vehicles')
            company_vehicle.objects.create(
                driver=driver,
                vehicle_name=vehicle_name,
                vehicle_model=vehicle_model,
                vehicle_number=vehicle_number,
                vehicle_color=vehicle_color,
                vehicle_year=vehicle_year,
                vehicle_fuel=vehicle_fuel,
                vehicle_mileage=vehicle_mileage,
                vehicle_transmission=vehicle_transmission,
                vehicle_engine=vehicle_engine,
                vehicle_seats=vehicle_seats,
                vehicle_doors=vehicle_doors,
                vehicle_description=vehicle_description,
                vehicle_type=vehicle_type,
                vehicle_image=vehicle_image,
                vehicle_airbags=vehicle_airbags, 
                vehicle_brake_type=vehicle_brake_type,
                vehicle_start_type=vehicle_start_type,
                vehicle_weight=vehicle_weight,
                tempo_seats=tempo_seats,
                tempo_doors=tempo_doors,
                vehicle_capacity=vehicle_capacity,
                admin=admin
            )
            messages.success(request,"Vehicle added successfully!")
            return redirect('admin_vehicles')
    except Exception as e:
            messages.error(request, f"An error occurred: {e}")
            return redirect('admin_vehicles')   
    vehicles = company_vehicle.objects.filter(admin=admin).order_by('-vehicle_id')
    
            
    context = {
        'drivers': drivers,
        'vehicles': vehicles
    }
    
    return render(request, 'admin_panel/admin_vehicle.html',context)
@never_cache
def admin_vehicle_edit(request, vehicle_id):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    if request.method == 'POST':
        try:
            vehicle = company_vehicle.objects.get(vehicle_id=vehicle_id)

            new_vehicle_number = request.POST.get('edit_vehicle_number')

            # Check for duplicate vehicle number (excluding current vehicle)
            if new_vehicle_number != vehicle.vehicle_number:
                if company_vehicle.objects.filter(vehicle_number=new_vehicle_number).exclude(vehicle_id=vehicle_id).exists():
                    messages.error(request, "Another vehicle with this number already exists.")
                    return redirect('admin_vehicles')
                if vehicle.driver:
                    if company_vehicle.objects.filter(driver=vehicle.driver).exclude(vehicle_id=vehicle_id).exists():
                        messages.error(request, "This driver is already assigned to another vehicle.")
                        return redirect('admin_vehicles')

            # Save updated values
            vehicle.vehicle_name = request.POST.get('edit_vehicle_name')
            vehicle.vehicle_model = request.POST.get('edit_vehicle_model')
            vehicle.vehicle_number = new_vehicle_number
            vehicle.vehicle_color = request.POST.get('edit_vehicle_color')
            vehicle.vehicle_year = request.POST.get('edit_vehicle_year')
            vehicle.vehicle_fuel = request.POST.get('edit_vehicle_fuel')
            vehicle.vehicle_mileage = request.POST.get('edit_vehicle_mileage')
            vehicle.vehicle_transmission = request.POST.get('edit_vehicle_transmission')
            vehicle.vehicle_engine = request.POST.get('edit_vehicle_engine')
            vehicle.vehicle_seats = request.POST.get('edit_vehicle_seats')
            vehicle.vehicle_doors = request.POST.get('edit_vehicle_doors')
            vehicle.vehicle_description = request.POST.get('edit_vehicle_description')
            vehicle.vehicle_type = request.POST.get('edit_vehicle_type')
            vehicle.vehicle_airbags = request.POST.get('edit_vehicle_airbags')
            vehicle.vehicle_brake_type = request.POST.get('edit_vehicle_brake_type')
            vehicle.vehicle_start_type = request.POST.get('edit_vehicle_start_type')
            vehicle.vehicle_weight = request.POST.get('edit_vehicle_weight')
            vehicle.tempo_seats = request.POST.get('edit_tempo_seats')
            vehicle.tempo_doors = request.POST.get('edit_tempo_doors')
            vehicle.vehicle_capacity = request.POST.get('edit_vehicle_capacity')
            

            if request.FILES.get('edit_vehicle_image'):
                vehicle.vehicle_image = request.FILES.get('edit_vehicle_image')

            vehicle.save()

            messages.success(request, "Vehicle updated successfully.")
            return redirect('admin_vehicles')

        except company_vehicle.DoesNotExist:
            messages.error(request, "Vehicle not found.")
            return redirect('admin_vehicles')
@never_cache
def admin_vehicle_delete(request, vehicle_id):
    try:
        vehicle = company_vehicle.objects.get(vehicle_id=vehicle_id)
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
        return redirect('admin_vehicles')
    except company_vehicle.DoesNotExist:
        messages.error(request,"Vehicle not found.")
        return redirect('admin_vehicles')
        

@never_cache
def admin_delete_multiple_vehicles(request):
    ids = request.POST.get("selected_ids")
    if ids:
        vehicle_ids = ids.split(",")
        company_vehicle.objects.filter(vehicle_id__in=vehicle_ids).delete()
        messages.success(request, "Selected vehicles deleted successfully.")
    else:
        messages.error(request, "No vehicles selected.")
    return redirect('admin_vehicles')

