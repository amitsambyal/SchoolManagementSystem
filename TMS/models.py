from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = [
        ('bus', 'Bus'),
        ('van', 'Van'),
        ('car', 'Car'),
        ('other', 'Other'),
    ]
    number = models.CharField(max_length=20, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE_CHOICES)
    capacity = models.PositiveIntegerField()
    remarks = models.TextField(blank=True)
    driver = models.ForeignKey('TMS.Driver', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.number} ({self.driver})" if hasattr(self, 'number') else str(self.pk)

    def average_daily_usage(self):
        readings = self.meterreading_set.order_by('date')
        if readings.count() < 2:
            return None  # Not enough data
        total_distance = readings.last().meter_value - readings.first().meter_value
        days = (readings.last().date - readings.first().date).days
        return total_distance / days if days > 0 else None

class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    start_point = models.CharField(max_length=100)
    end_point = models.CharField(max_length=100)
    stops = models.TextField(help_text="Comma-separated list of stops")

    def __str__(self):
        return self.name

class TransportAssignment(models.Model):
    school_class = models.ForeignKey('webportal.SchoolClass', on_delete=models.CASCADE)
    student = models.ForeignKey('webportal.Student', on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True)
    pickup_point = models.CharField(max_length=100)
    drop_point = models.CharField(max_length=100)
    assigned_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} - {self.route} - {self.vehicle}"


class MeterReading(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey('TMS.Driver', on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    start_meter_value = models.PositiveIntegerField(help_text="Odometer reading when taking the vehicle")
    start_time = models.DateTimeField(help_text="Time when vehicle was taken", null=True, blank=True)
    end_meter_value = models.PositiveIntegerField(
        help_text="Odometer reading when returning the vehicle", null=True, blank=True
    )
    end_time = models.DateTimeField(
        help_text="Time when vehicle was returned", null=True, blank=True
    )
    remarks = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.driver} - {self.date}"

    @property
    def distance_covered(self):
        if self.end_meter_value is not None and self.start_meter_value is not None:
            return self.end_meter_value - self.start_meter_value
        return None

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    contact = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

