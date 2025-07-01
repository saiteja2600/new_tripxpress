from django.shortcuts import render,redirect
from django.contrib import messages
from admin_panel.models import Driver
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

def driver_login(request):
    if request.method == 'POST':
        company_email = request.POST.get('company_email', '').strip().lower()
        password = request.POST.get('password')

        try:
            driver = Driver.objects.get(company_email=company_email)

            if check_password(password, driver.password):
                request.session['driver_id'] = driver.driver_id
                request.session['driver_name'] = f"{driver.first_name} {driver.last_name}"
                request.session['driver_company_email'] = driver.company_email
                request.session['driver_phone_number'] = driver.phone_number
                request.session['driver_vehicle_link'] = driver.vehicle_link
                request.session['driver_country'] = driver.country.name if driver.country else ''
                request.session['driver_state'] = driver.state.name if driver.state else ''
                request.session['driver_city'] = driver.city.name if driver.city else ''
                request.session['driver_joined_at'] = str(driver.joined_at)
                request.session['driver_driving_licence'] = driver.driving_licence

                messages.success(request, "Login successful.")
                return redirect('driver_dashbord')
            else:
                messages.error(request, "Incorrect password.")
        except Driver.DoesNotExist:
            messages.error(request, "Company email not found.")

        return redirect('driver_login')

    return render(request, 'driver_panel/driver_login.html')

def driver_logout(request):
    request.session.flush()
    return redirect('driver_login')


def change_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        driver_id = request.session.get('driver_id')

        if not driver_id:
            messages.error(request, "You are not logged in.")
            return redirect('driver_login')

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('change_password')

        try:
            driver = Driver.objects.get(driver_id=driver_id)
            driver.password = make_password(new_password)
            driver.save()
            messages.success(request, "Password changed successfully.")
            return redirect('driver_login')
        except Driver.DoesNotExist:
            messages.error(request, "Driver not found.")
            return redirect('driver_login')

    return render(request, 'driver_panel/change_password.html')
      

def Dashbord(request):
    return render(request,'driver_panel/driver_dashbord.html')