from django.db import models
from django.utils import timezone
from admin_panel.models import Driver,company_vehicle
from django.db.models.functions import TruncMonth
from django.db.models import Count
from dateutil.relativedelta import relativedelta
from datetime import timedelta,datetime     
from django.core.exceptions import ValidationError
from django.utils.timezone import now


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
        if self.service_date and not self.next_service_due_date:
            self.next_service_due_date = self.service_date + relativedelta(months=1)

        super().save(*args, **kwargs)

        # Always re-evaluate vehicle status based on all active maintenance
        active_records = VehicleMaintenance.objects.filter(
            vehicle=self.vehicle,
            status__in=['Scheduled', 'In Progress']
        )

        if active_records.exists():
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

class leave_request(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    leave_id = models.AutoField(primary_key=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def leave_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        if self.status == 'Approved':
            self.driver.status = 'Leave'
            self.driver.save()
        elif self.status == 'Rejected':
       
            overlapping = leave_request.objects.filter(
            driver=self.driver,
            status='Approved',
            start_date__lte=self.end_date,
            end_date__gte=self.start_date
            ).exclude(pk=self.pk)
            if not overlapping.exists():
                self.driver.status = 'Available'
                self.driver.save()

    
    def clean(self):
        # Ensure `self.start_date` is a date object
        if isinstance(self.start_date, str):
            reference_date = datetime.strptime(self.start_date, "%Y-%m-%d").date()
        else:
            reference_date = self.start_date or now().date()

        month_start = reference_date.replace(day=1)
        next_month = (month_start.replace(day=28) + timedelta(days=4)).replace(day=1)

        existing = leave_request.objects.filter(
            driver=self.driver,
            start_date__gte=month_start,
            start_date__lt=next_month
        )
        if self.pk:
            existing = existing.exclude(pk=self.pk)

        if existing.count() >= 4:
            raise ValidationError("Only 4 leaves are allowed per month.")
