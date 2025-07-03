from django.db import models
from django.utils import timezone
from admin_panel.models import Driver,company_vehicle



class VehicleMaintenance(models.Model):
    SERVICE_TYPES = [
        ('Oil Change', 'Oil Change'),
        ('Tyre Replacement', 'Tyre Replacement'),
        ('Brake Service', 'Brake Service'),
        ('General Service', 'General Service'),
        ('Battery Check', 'Battery Check'),
        ('Engine Work', 'Engine Work'),
        ('Tire Rotation', 'Tire Rotation'),
        ('Transmission Service', 'Transmission Service'),
        ('Air Filter Replacement', 'Air Filter Replacement'),
        ('Coolant Flush', 'Coolant Flush'),
        ('Radiator Flush', 'Radiator Flush'),
        ('Other', 'Other'),
    ]

    MAINTENANCE_STATUS = [
        ('Scheduled', 'Scheduled'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    service_id = models.AutoField(primary_key=True)
    vehicle = models.ForeignKey(company_vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='maintenance_records')

    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES)
    service_date = models.DateField(default=timezone.now)
    odometer_reading = models.PositiveIntegerField(help_text="KM at time of service")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    next_service_due_date = models.DateField(null=True, blank=True)
    next_service_due_km = models.PositiveIntegerField(null=True, blank=True)

    service_center = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(blank=True)
    document = models.FileField(upload_to='maintenance_docs/', null=True, blank=True)

    status = models.CharField(max_length=20, choices=MAINTENANCE_STATUS, default='Scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        
        active_maintenances = VehicleMaintenance.objects.filter(
            vehicle=self.vehicle,
            status__in=['Scheduled', 'In Progress']
        ).exclude(service_id=self.service_id)

       
        if self.status in ['Scheduled', 'In Progress']:
            active_exists = True
        else:
            active_exists = active_maintenances.exists()

        # Update vehicle status accordingly
        if active_exists:
            
            if self.vehicle.status != 'Under Maintenance':
                self.vehicle.status = 'Under Maintenance'
                self.vehicle.save()
        else:
            
            if self.vehicle.status != 'Available':
                self.vehicle.status = 'Available'
                self.vehicle.save()


    def __str__(self):
        return f"{self.vehicle.vehicle_number} - {self.service_type} on {self.service_date}"

    class Meta:
        ordering = ['-service_date']
