from django.shortcuts import render,redirect
from django.contrib import messages
from admin_panel.models import Driver,company_vehicle
from driver_panel.models import VehicleMaintenance,leave_request
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from django.views.decorators.cache import never_cache
from datetime import datetime,date, timedelta
from django.core.exceptions import ObjectDoesNotExist

from django.utils.timezone import now

def driver_login(request):
    if request.method == 'POST':
        company_email = request.POST.get('company_email', '').strip().lower()
        password = request.POST.get('password')

        try:
            driver = Driver.objects.get(company_email=company_email)

            if check_password(password, driver.password):
                request.session['driver_id'] = driver.driver_id
                request.session['driver_name'] = f"{driver.first_name[0]}{driver.last_name[0]}".upper()

                request.session['driver_company_email'] = driver.company_email
                request.session['driver_phone_number'] = driver.phone_number
                request.session['driver_vehicle_link'] = driver.vehicle_link
                request.session['driver_country'] = driver.country.name if driver.country else ''
                request.session['driver_state'] = driver.state.name if driver.state else ''
                request.session['driver_city'] = driver.city.name if driver.city else ''
                request.session['driver_joined_at'] = str(driver.joined_at)
                request.session['driver_driving_licence'] = driver.driving_licence
                if driver.driver_profile_image:
                    request.session['driver_profile'] = driver.driver_profile_image.url
                else:
                    request.session['driver_profile'] = ''

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
      
def driver_profile(request):
    if 'driver_id' not in request.session:
        return redirect('driver_login')
    driver_id = request.session['driver_id']
    try:
        driver = Driver.objects.get(driver_id=driver_id)
        if request.method == 'POST':
            if 'driver_profile_image' in request.FILES:
                driver.driver_profile_image = request.FILES['driver_profile_image']
                driver.save()
                request.session['driver_profile'] = driver.driver_profile_image.url
                messages.success(request, 'Profile image updated successfully!')
            else:
                messages.warning(request, 'No image selected.')
        return render(request, 'driver_panel/driver_profile.html', {'driver': driver})
    except Driver.DoesNotExist:
        messages.error(request, 'Driver not found.')

def Dashbord(request):
    return render(request,'driver_panel/driver_dashbord.html')


def vehicle_information(request):
    if 'driver_id' not in request.session:
        return redirect('driver_login')

    driver = Driver.objects.get(driver_id=request.session['driver_id'])

    vehicle = None
    if driver.vehicle_link == 'company':
        vehicle = company_vehicle.objects.filter(driver=driver)

    return render(request, 'driver_panel/vehicle_information.html', {
        'driver': driver,
        'vehicle': vehicle
    })
def vehicle_maintenance(request):
    if 'driver_id' not in request.session:
        return redirect('driver_login')

    driver = Driver.objects.get(driver_id=request.session['driver_id'])
    vehicle = company_vehicle.objects.filter(driver=driver).first()

    if request.method == 'POST':
        service_type = request.POST.get('service_type')
        service_date = request.POST.get('service_date')
        odometer_reading = request.POST.get('odometer_reading')
        cost = request.POST.get('cost')
        next_service_due_date = request.POST.get('next_service_due_date')
        next_service_due_km = request.POST.get('next_service_due_km')
        service_center = request.POST.get('service_center')
        notes = request.POST.get('notes')
        document = request.FILES.get('document')
        status = request.POST.get('status')

        if vehicle:
            VehicleMaintenance.objects.create(
                driver=driver,
                vehicle=vehicle,
                service_type=service_type,
                service_date=service_date,
                odometer_reading=odometer_reading,
                cost=cost,
                next_service_due_date=next_service_due_date,
                next_service_due_km=next_service_due_km,
                service_center=service_center,
                notes=notes,
                document=document,
                status=status,
            )

            # Optionally update vehicle status
            vehicle.status = "Under Maintenance" if status != "Completed" else "Available"
            vehicle.save()

            messages.success(request, "Maintenance record added successfully.")
            return redirect('vehicle_maintenance')
        else:
            messages.error(request, "No vehicle assigned to you.")

    maintenance_records = VehicleMaintenance.objects.filter(driver=driver).order_by('-service_date')

    context = {
        'driver': driver,
        'vehicle': vehicle,
        'maintenance_records': maintenance_records,
    }
    return render(request, 'driver_panel/vehicle_maintenance.html', context)

def vehicle_maintenance_delete(request, service_id):
    try:
        maintenance = VehicleMaintenance.objects.get(service_id=service_id)
        maintenance.delete()
        messages.success(request, "Maintenance record deleted successfully.")
        return redirect('vehicle_maintenance')
    except VehicleMaintenance.DoesNotExist:
        messages.error(request, "Maintenance record not found.")
        return redirect('vehicle_maintenance')

def vehicle_maintenance_edit(request, service_id):
    if request.method == 'POST':
        try:
            maintenance = VehicleMaintenance.objects.get(service_id=service_id)

            maintenance.service_type = request.POST.get('edit_service_type')
            maintenance.service_date = request.POST.get('edit_service_date')
            maintenance.odometer_reading = request.POST.get('edit_odometer_reading')
            maintenance.cost = request.POST.get('edit_cost')
            maintenance.next_service_due_date = request.POST.get('edit_next_service_due_date')
            maintenance.next_service_due_km = request.POST.get('edit_next_service_due_km')
            maintenance.service_center = request.POST.get('edit_service_center')
            maintenance.notes = request.POST.get('edit_notes')
            maintenance.document = request.FILES.get('edit_document')
            maintenance.status = request.POST.get('edit_status')

            maintenance.save()
            messages.success(request, "Maintenance record updated successfully.")
            return redirect('vehicle_maintenance')
        except VehicleMaintenance.DoesNotExist:
            messages.error(request,"Maintenace record not found")
            return redirect('vehicle_maintenance')
        
#driver leaves


def driver_leaves(request):
    if 'driver_id' not in request.session:
        return redirect('driver_login')
    
    driver_id = request.session['driver_id']
    try:
        driver = Driver.objects.get(driver_id=driver_id)

        if request.method == 'POST':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            reason = request.POST.get('reason')
            leave_request.objects.create(
                driver=driver,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            messages.success(request, "Leave request submitted successfully.")
            return redirect('driver_leaves')

        # Calculate current month's leaves (exclude Rejected)
        today = now().date()
        month_start = today.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)

        current_month_leave_count = leave_request.objects.filter(
            driver=driver,
            start_date__gte=month_start,
            start_date__lt=next_month
        ).exclude(status='Rejected').count()

        remaining_leaves = max(0, 4 - current_month_leave_count)

        leaves = leave_request.objects.filter(driver=driver).order_by('-created_at')
        context = {
            'driver': driver,
            'leaves': leaves,
            'remaining_leaves': remaining_leaves,
        }
        return render(request, 'driver_panel/driver_leaves.html', context)

    except Driver.DoesNotExist:
        messages.error(request, 'Driver not found.')
        return redirect('driver_login')

    except Driver.DoesNotExist:
        messages.error(request, 'Driver not found.')
        return redirect('driver_login')